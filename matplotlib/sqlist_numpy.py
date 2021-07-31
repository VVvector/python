import matplotlib.pyplot as plt
import pandas as pd
import os
import sqlite3
import logging
import argparse
import sys
import random


def get_sqlite(sqlite_db):
    conn = sqlite3.connect(sqlite_db)
    cur = conn.cursor()
    logging.debug("Opened database successfully")
    return conn, cur


def close_sqlite(conn):
    conn.close()


def setup_sqlite(sqlite_db, table_name, col_name, col_type):
    sqlite3_conn = sqlite3.connect(sqlite_db)
    sqlite3_cur = sqlite3_conn.cursor()

    sql = " CREATE TABLE IF NOT EXISTS {} ({} INTEGER PRIMARY KEY NOT NULL);".format(table_name, "ID")
    sqlite3_cur.execute(sql)
    logging.debug("Table {}: created successfully".format(table_name))

    sql = "ALTER TABLE {} ADD COLUMN '{}' {}".format(table_name, col_name, col_type)
    sqlite3_cur.execute(sql)
    logging.debug("col {}: alter new col successfully".format(col_name))
    sqlite3_conn.commit()

    sql = "INSERT INTO {} ({}) VALUES (?)".format(table_name, col_name)
    for i in range(0, 10000):
        sqlite3_cur.execute(sql, (random.randint(0,1000),))

        if i % 1000 == 0:
            sqlite3_conn.commit()

    sqlite3_conn.commit()

    return sqlite3_conn, sqlite3_cur

def main():
    parser = argparse.ArgumentParser(description="This is a example program")
    parser.add_argument('-d', '--database', default=None, required=True, help='the sqlite database')
    args = parser.parse_args()

    database = args.database
    test_table = "test1"
    test_col = "t1"
    if os.path.exists(database) is not True:
        logging.error("The sqlite database not exist, please check!")
        setup_sqlite(database, test_table, test_col, "INT")
        sys.exit(1)

    conn, cur = get_sqlite(database)
    sql = "select * from {};".format(test_table)
    df = pd.read_sql_query(sql, conn)
    print(df.describe())

    df.hist(bins=100)
    #plt.savefig('./test2.jpg')
    #plt.show()

    print(df[test_col].value_counts())
    print(df[test_col].value_counts(normalize=True))

    close_sqlite(conn)


def log_config():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


if __name__ == '__main__':
    log_config()
    main()
