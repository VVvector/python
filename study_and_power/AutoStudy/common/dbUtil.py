# -*- coding:utf-8 -*-
import pymysql
import sqlite3
from configparser import ConfigParser
import os

class DB(object):
    def __init__(self):
        cfg = ConfigParser()
        cur_path = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(cur_path, "config.ini")
        cfg.read(config_file_path, encoding='utf-8')
        self.rules = 'data_base'
        self.cfg = cfg

        self.db_type =  self.cfg.get(self.rules, 'db_type')
        self.host = self.cfg.get(self.rules, 'db_host')
        self.port = self.cfg.getint(self.rules, 'db_port')
        self.user = self.cfg.get(self.rules, 'db_user')
        self.pwd =  self.cfg.get(self.rules, 'db_pwd')
        self.db_name = self.cfg.get(self.rules, 'db_name')
        self.table_name = self.cfg.get(self.rules, 'db_table_name')
        self.question = ''

        if self.db_type == "mysql":
            self.open_mysql()
            self.check_mysql_table()
        else:
            self.open_sqlite3()
            self.check_sqlite3_table()

    def open_mysql(self):
        # connect MySQL
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.pwd)
        self.cur = self.conn.cursor()
        # select databases
        self.conn.select_db(self.db_name)

    def open_sqlite3(self):
        self.conn = sqlite3.connect(self.db_name + '.db')
        self.cur = self.conn.cursor()

    def check_sqlite3_table(self):
        col_format = ["ID", "Type", "Question", "AnswerA", "AnswerB", "AnswerC", "AnswerD", "AnswerE", "Correct"]
        sql = " CREATE TABLE IF NOT EXISTS {} ({} INTEGER PRIMARY KEY NOT NULL," \
              "{} CHAR,{} VARCHAR,{} VARCHAR,{} VARCHAR,{} VARCHAR, {} VARCHAR, {} VARCHAR, {} VARCHAR);".format(
            self.table_name, col_format[0], col_format[1], col_format[2],
            col_format[3], col_format[4], col_format[5], col_format[6],
            col_format[7], col_format[8])

        self.cur.execute(sql)
        self.conn.commit()

    def check_mysql_table(self):
        col_format = ["Type", "Question", "AnswerA", "AnswerB", "AnswerC", "AnswerD", "AnswerE", "Correct"]
        sql = 'CREATE TABLE IF NOT EXISTS `{}` (`{}` CHAR,`{}` VARCHAR(255),`{}` VARCHAR(255),`{}` VARCHAR(255),`{}` VARCHAR(255), `{}` VARCHAR(255), `{}` VARCHAR(255), `{}` VARCHAR(255))ENGINE=InnoDB DEFAULT CHARSET=utf8;'.format(
            self.table_name, col_format[0], col_format[1], col_format[2],
            col_format[3], col_format[4], col_format[5], col_format[6],
            col_format[7])
        self.cur.execute(sql)
        self.conn.commit()

    # 数据库搜索或添加前过滤掉无用字符串
    def getQuestion(self, str):
        str = str.split('（出题单位')
        str = str[0]
        str = str.split('(出题单位')
        str = str[0]
        str = str.split('（ 出题单位')
        str = str[0]
        str = str.split('(来源')
        str = str[0]
        str = str.split('（来源')
        str = str[0]
        str = str.split('来源：')
        str = str[0]
        str = str.replace('1. ', '')
        str = str.replace('2. ', '')
        str = str.replace('3. ', '')
        str = str.replace('4. ', '')
        str = str.replace('5. ', '')
        str = str.replace('6. ', '')
        str = str.replace('7. ', '')
        str = str.replace('8. ', '')
        str = str.replace('9. ', '')
        str = str.replace('10. ', '')
        str = str.replace('11. ', '')
        return str

    def search(self, type, str, insertDB):
        self.question = str.replace('"', '%')
        if self.db_type == "mysql":
            sql = 'select Correct from autostudy where Type=%s and Question like %s LIMIT 1'
        else:
            sql = 'select Correct from autostudy where Type=? and Question like ? LIMIT 1'

        self.cur.execute(sql, (type, self.question))
        result = self.cur.fetchone()

        # 返回查找到的正确答案，如果没有查找到，就将该题目添加到数据库
        if result is not None:
            result = result[0]
        else:
            if type == '单选题':
                result = 'A'
            elif type == '多选题':
                result = 'AB'
            else:
                result = '不忘初心牢记使命 不忘初心牢记使命 不忘初心牢记使命 不忘初心牢记使命'

            if insertDB:
                if self.db_type == "mysql":
                    sql = 'insert into autostudy (Type,Question,Correct) value (%s,%s,%s)'
                else:
                    sql = 'insert into autostudy (Type,Question,Correct) values (?,?,?)'
                try:
                    self.cur.execute(sql, (type, str, result))
                except:
                    print("failed to insert database")
                self.conn.commit()

        return result

    def update(self, key, value):
        '''
        sql = 'update autostudy set %s = %s where Question like %s'%(key, value, self.question)
        self.cur.execute(sql)
        self.conn.commit()
        '''
        # 选择题
        if key == 'Answer':
            for i in range(len(value)):
                if self.db_type == "mysql":
                    if i == 0:
                        sql = 'update autostudy set AnswerA = %s where Question like %s'
                    elif i == 1:
                        sql = 'update autostudy set AnswerB = %s where Question like %s'
                    elif i == 2:
                        sql = 'update autostudy set AnswerC = %s where Question like %s'
                    elif i == 3:
                        sql = 'update autostudy set AnswerD = %s where Question like %s'
                    elif i == 4:
                        sql = 'update autostudy set AnswerE = %s where Question like %s'
                    else:
                        break
                else:
                    if i == 0:
                        sql = 'update autostudy set AnswerA = ? where Question like ?'
                    elif i == 1:
                        sql = 'update autostudy set AnswerB = ? where Question like ?'
                    elif i == 2:
                        sql = 'update autostudy set AnswerC = ? where Question like ?'
                    elif i == 3:
                        sql = 'update autostudy set AnswerD = ? where Question like ?'
                    elif i == 4:
                        sql = 'update autostudy set AnswerE = ? where Question like ?'
                    else:
                        break
                self.cur.execute(sql, (value[i], self.question))
                self.conn.commit()
            return True
        # 判断题
        elif key == "Correct":
            if self.db_type == "mysql":
                sql = 'update autostudy set Correct = %s where Question like %s'
            else:
                sql = 'update autostudy set Correct = ? where Question like ?'
            self.cur.execute(sql, (value, self.question))
            self.conn.commit()
            return True
        else:
            return False

    def close(self):
        self.conn.close()
        self.cur.close()


if __name__ == "__main__":
    pass
