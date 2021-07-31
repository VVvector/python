import matplotlib.pyplot as plt
import os
import sqlite3
import logging
import argparse
import sys


def get_sqlite(sqlite_db):
    conn = sqlite3.connect(sqlite_db)
    cur = conn.cursor()
    logging.debug("Opened database successfully")
    return conn, cur


def close_sqlite(conn):
    conn.close()


def get_col_data(conn, cur, table_name, col_name):
    sql = "SELECT {} FROM {};".format(col_name, table_name)
    cur.execute(sql)

    return cur.fetchall()


def draw_hist(data):
    plt.style.use('seaborn-white')

    plt.figure()
    plt.hist(data, bins=200, alpha=0.5)
    plt.grid()

    plt.xlabel("duration")
    plt.ylabel("frequency")
    plt.title("duration-frequency")

    plt.savefig('./test2.jpg')
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="This is a example program")
    parser.add_argument('-d', '--database', default=None, required=True, help='the sqlite database')
    args = parser.parse_args()

    database = args.database
    if os.path.exists(database) is not True:
        logging.error("The sqlite database not exist, please check!")
        sys.exit(1)

    conn, cur = get_sqlite(database)

    table_name = "latency"
    col_name = "t1"
    col_data = get_col_data(conn, cur, table_name, col_name)

    draw_hist(col_data)
    close_sqlite(conn)


def log_config():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


if __name__ == '__main__':
    log_config()
    main()
