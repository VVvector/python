import sqlite3
import os
import json
import time
import argparse
import re
import logging as log
import sys


class INFO:
    function_name = None
    abstime = 0
    duration = 0
    flag = None
    ftrace_log = None


class STACK():
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


def parse_line(str):
    t_str = str.split("|")
    if len(t_str) != 3:
        return 1, 1

    info = INFO()

    # get abstime
    info.abstime = t_str[0]

    # get duration time
    if "us" in t_str[1]:
        t_str2 = t_str[1].split()
        info.duration = t_str2[-2]

    # get function name
    if ";" in t_str[2]:
        info.function_name = t_str[2][:-4].replace(' ', '')
    elif "{" in t_str[2]:
        info.function_name = t_str[2][:-5].replace(' ', '')
        info.flag = "{"
    elif "}" in t_str[2]:
        info.flag = "}"
    else:
        info.ftrace_log = t_str[2]

    log.debug("{}, {}, {}, {}, {}".format(info.function_name, info.abstime, info.duration, info.flag, info.ftrace_log))
    return 0, info


def get_funciton_duration_info(sqlite3_cur, table_name, fucntion_name_col, latency_col, function):
    sql = "SELECT COUNT({}) FROM {} WHERE {} LIKE '{}';".format(latency_col, table_name, fucntion_name_col, function)
    sqlite3_cur.execute(sql)
    count = sqlite3_cur.fetchone()[0]

    sql = "SELECT MAX({}) FROM {} WHERE {} LIKE '{}';".format(latency_col, table_name, fucntion_name_col, function)
    sqlite3_cur.execute(sql)
    max = sqlite3_cur.fetchone()[0]

    sql = "SELECT MIN({}) FROM {} WHERE {} LIKE '{}';".format(latency_col, table_name, fucntion_name_col, function)
    sqlite3_cur.execute(sql)
    min = sqlite3_cur.fetchone()[0]

    sql = "SELECT AVG({}) FROM {} WHERE {} LIKE '{}';".format(latency_col, table_name, fucntion_name_col, function)
    sqlite3_cur.execute(sql)
    avg = sqlite3_cur.fetchone()[0]

    sql = "SELECT SUM({}) FROM {} WHERE {} LIKE '{}';".format(latency_col, table_name, fucntion_name_col, function)
    sqlite3_cur.execute(sql)
    sum = sqlite3_cur.fetchone()[0]

    log.info("{}() - count:{}, max:{}, min:{}, avg:{:.6f}, sum:{:.6f}".format(function, count, max, min, avg, sum))


def get_info_by_col_name(sqlite3_cur, table_name, col_name):
    sql = "SELECT COUNT({}) FROM {};".format(col_name, table_name)
    sqlite3_cur.execute(sql)
    count = sqlite3_cur.fetchone()[0]

    sql = "SELECT MAX({}) FROM {};".format(col_name, table_name)
    sqlite3_cur.execute(sql)
    max = sqlite3_cur.fetchone()[0]

    sql = "SELECT MIN({}) FROM {};".format(col_name, table_name)
    sqlite3_cur.execute(sql)
    min = sqlite3_cur.fetchone()[0]

    sql = "SELECT AVG({}) FROM {};".format(col_name, table_name)
    sqlite3_cur.execute(sql)
    avg = sqlite3_cur.fetchone()[0]

    sql = "SELECT SUM({}) FROM {};".format(col_name, table_name)
    sqlite3_cur.execute(sql)
    sum = sqlite3_cur.fetchone()[0]

    log.info("{}() - count:{}, max:{}, min:{}, avg:{:.6f}, sum:{:.6f}".format(col_name, count, max, min, avg, sum))


def update_the_function_duration(sqlite3_conn, table_name, update_col_name):
    flush_time = 0
    stack = STACK()

    # query the table data
    for row in sqlite3_conn.execute("SELECT * FROM {}".format(table_name)):
        if row[4] == "{":
            row_id = row[0]
            stack.push(row_id)
            continue

        if stack.is_empty() is not True:
            if row[4] == "}":
                latency = row[3]
                row_id = stack.pop()
                sql = "UPDATE {} SET {} = {} where ID={}".format(table_name, update_col_name, latency, row_id)
                sqlite3_conn.execute(sql)

                flush_time = flush_time + 1
                if flush_time % 1000 == 0:
                    sqlite3_conn.commit()

    sqlite3_conn.commit()


def get_latency_between_two_function(sqlite3_conn, table_name, func1, func2):
    latency_list = []
    abs_time1 = 0
    # query the table data
    for row in sqlite3_conn.execute("SELECT * FROM {}".format(table_name)):
        if row[1] == func1:
            abs_time1 = row[2]
            continue

        if abs_time1 != 0:
            if row[1] == func2:
                abs_time2 = row[2]
                latency = abs_time2 - abs_time1
                abs_time1 = 0

                latency_list.append(round(latency, 6))
                # latency_list.append(float("{:.6f}".format(latency)))

    log.debug(latency_list)
    return latency_list


def creat_sqlite3_db(sqlite_db, table_name, col_format):
    # delete the old DB file
    if os.path.exists(sqlite_db) is True:
        os.remove(sqlite_db)

    # create a sqlite
    conn = sqlite3.connect(sqlite_db)
    log.debug("Opened database successfully")

    # create a cursor
    cur = conn.cursor()

    # execute a SQL CMD to create a table
    sql = " CREATE TABLE IF NOT EXISTS {} ({} INTEGER PRIMARY KEY NOT NULL," \
          "{} TEXT,{} REAL,{} REAL,{} CHAR(1),{} TEXT);".format(table_name,
                                                                col_format[0], col_format[1], col_format[2],
                                                                col_format[3], col_format[4], col_format[5])
    cur.execute(sql)
    log.debug("Table created successfully")
    conn.commit()

    return conn, cur


def parse_ftrace_log(sqlite3_conn, sqlite3_cur, table_name, col_format, ftrace):
    flush_time = 0
    # parse the ftrace file to sqlite3
    with open(ftrace, 'r', encoding='UTF-8') as f:
        line = f.readline()
        while line is not None and line != '':
            ret, info = parse_line(line)
            if ret == 0:
                # insert some test data
                sql = "INSERT INTO {} ({}, {}, {}, {}, {}) VALUES (?, ?, ?, ?, ?)".format(
                    table_name, col_format[1], col_format[2], col_format[3], col_format[4], col_format[5]
                )
                sqlite3_cur.execute(sql, (info.function_name, info.abstime, info.duration, info.flag, info.ftrace_log))
            line = f.readline()

        if flush_time % 1000 == 0:
            sqlite3_conn.commit()

    sqlite3_conn.commit()
    log.debug('Records created successfully')


def get_function_by_duration(sqlite3_conn, table_name, duration):
    func_list = set()
    # query the table data
    for row in sqlite3_conn.execute("SELECT * FROM {}".format(table_name)):
        if row[3] >= duration and row[1] != None:
            func_list.add(row[1])

    log.info(func_list)


def get_info_between_two_function(sqlite3_conn, table_name, col_info, func1, func2, event1):
    func_time = 0
    start_flag = False
    func_times_list = []

    # query the table data
    sql = "SELECT * FROM {}".format(table_name)
    for row in sqlite3_conn.execute(sql):
        if row[col_info.index("FUNCTION_NAME")] == func1 and start_flag is False:
            start_flag = True
            continue

        if start_flag is True:
            if row[col_info.index("FUNCTION_NAME")] == event1:
                func_time = func_time + 1

            if row[col_info.index("FUNCTION_NAME")] == func2:
                start_flag = False
                func_times_list.append(func_time)
                func_time = 0

    log.debug(func_times_list)


def add_new_col_in_table(sqlite3_conn, sqlite3_cur, table_name, col_name, col_type):
    sql = " CREATE TABLE IF NOT EXISTS {} ({} INTEGER PRIMARY KEY NOT NULL);".format(table_name, "ID")
    sqlite3_cur.execute(sql)
    log.debug("Table {}: created successfully".format(table_name))

    sql = "ALTER TABLE {} ADD COLUMN '{}' {}".format(table_name, col_name, col_type)
    sqlite3_cur.execute(sql)
    log.debug("col {}: alter new col successfully".format(col_name))

    sqlite3_conn.commit()


def add_multi_cols_in_table(sqlite3_conn, sqlite3_cur, table_name, cols_info):
    for k, v in cols_info.items():
        add_new_col_in_table(sqlite3_conn, sqlite3_cur, table_name, k, v)


def add_list_to_col(sqlite3_conn, sqlite3_cur, table_name, col_name, val_list):
    flush = 0
    for val in val_list:
        # insert some test data
        sql = "INSERT INTO {} ({}) VALUES (?)".format(
            table_name, col_name)
        sqlite3_cur.execute(sql, (val,))
        flush = flush + 1
        if flush % 1000 == 0:
            sqlite3_conn.commit()

    sqlite3_conn.commit()


def get_num_in_brackets(line_str, keyword):
    n_pos = line_str.find(keyword)
    if n_pos < 0:
        return False, 0

    str1 = line_str[n_pos:]
    num_str = re.findall(r'[(](.*?)[)]', str1)
    if num_str[0].isdigit() is not True:
        return False, 0

    num = int(num_str[0])
    log.debug(num)
    return True, num


def get_num_in_ftrace_log(sqlite3_conn, table_name, keyword):
    num_list = []
    # query the table data
    sql = "SELECT * FROM {}".format(table_name)
    for row in sqlite3_conn.execute(sql):
        ftrace_log = row[5]
        if ftrace_log is not None and keyword in ftrace_log:
            ret, num = get_num_in_brackets(ftrace_log, keyword)
            if ret is True:
                num_list.append(num)

    log.debug(num_list)
    return num_list


def main():
    parser = argparse.ArgumentParser(description="This is a example program")
    parser.add_argument('-f', '--file', default=None, required=True, help='the ftrace test log file')
    args = parser.parse_args()

    file = args.file
    if os.path.exists(file) is not True:
        log.error("The ftrace file not exist, please check!")
        sys.exit(1)

    ftrace_log_name = os.path.basename(file)
    ftrace_db = "{}.db".format(ftrace_log_name)

    # parse the columns format json file
    with open("db_configture.json", 'r') as load_f:
        json_data = json.load(load_f)
        log.debug(json_data)

    col_format = json_data["col_info"]
    table_name = json_data["table_info"][0]

    # create a sqlite3 database
    conn, cur = creat_sqlite3_db(ftrace_db, table_name, col_format)

    # parse the ftrace log file to sqlite3
    parse_ftrace_log(conn, cur, table_name, col_format, ftrace_log_name)

    # update the function latency with "{", "}"
    update_the_function_duration(conn, table_name, "DURATION")

    # get the latency between two function according abs_time
    latency_list = get_latency_between_two_function(conn, table_name, "tty_insert_flip_string_fixed_flag",
                                                    "tty_ldisc_receive_buf")
    add_new_col_in_table(conn, cur, "latency", "t1", "REAL")
    add_list_to_col(conn, cur, "latency", "t1", latency_list)

    # get function latency information, such as, max, min, avg, sum ...
    get_funciton_duration_info(cur, table_name, "FUNCTION_NAME", "DURATION", "tty_ldisc_ref")

    # get max/min/avg information by col name
    get_info_by_col_name(cur, table_name, "DURATION")

    # get the information up specific value
    get_function_by_duration(conn, table_name, 10)

    # get event information between two function
    get_info_between_two_function(conn, table_name, col_format,
                                  "tty_insert_flip_string_fixed_flag", "tty_insert_flip_string_fixed_flag",
                                  "tty_ldisc_ref")

    # get number from ftrace log
    get_num_in_ftrace_log(conn, table_name, "test_num")

    # add multiple cols
    cols_info = {"col1": "TEXT", "col2": "INT"}
    add_multi_cols_in_table(conn, cur, "test", cols_info)

    conn.close()


if __name__ == '__main__':
    log.basicConfig(level=log.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    main()
