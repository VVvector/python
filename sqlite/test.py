import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


def gen_insert_sql(table_name, col_num):
    sql = "INSERT INTO {} VALUES (".format(table_name)

    for i in range(0, col_num):
        sql += "?,"
    sql = sql.strip(',')
    sql = sql + ")"

    print(sql)
    return sql

def main():
    conn = sqlite3.connect('test.db')
    courses = ((1, 'math', 6), (2, 'english', 3), (3, 'C++', 4), (4, 'Java', 2), (5, 'Python', 3), (6, 'Computer Science', 2),
               (7, 'network', 3))

    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS courses")
    cur.execute("CREATE TABLE courses(id INT, name TEXT, credit INT)")

    #cur.executemany("INSERT INTO courses VALUES(?, ?, ?)", courses)

    #sql = "INSERT INTO {} ({}) VALUES (?)".format("courses", "name")
    #cur.execute(sql, ("aa",))

    #sql = "INSERT INTO {} ({}) VALUES (?)".format("courses", "credit")
    #cur.execute(sql, (1,))

    test = [1, "bb", 3]
    sql = gen_insert_sql("courses", len(test))
    cur.execute(sql, test)

    test = []
    test1 = [2, "bb", 4]
    test.append(test1)
    test2 = [4, "bb", 1]
    test.append(test2)
    print(test)

    sql = gen_insert_sql("courses", 3)
    cur.executemany(sql, test)
    conn.commit()

    #cur.execute("select * from courses")
    #print(cur.fetchall())

    df = pd.read_sql_query("select * from courses limit 5;", conn)
    print(type(df))

    #总数、平均数、标准差、最小值、最大值、25% / 50% / 75% 分位数
    print(df.describe())
    #print(df.value_counts)

    print(df.id.value_counts())

    df.hist(bins=10)
    plt.savefig('./test2.jpg')
    plt.show()

    conn.close()

if __name__ == '__main__':
    main()