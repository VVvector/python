# -*- coding:utf-8 -*-
import re
import pymysql
from time import sleep


class Quzi(object):
    def __init__(self, cfg, rules, ad, xm, entrance, question, ):
        # connect MySQL
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123qwe???')
        self.cur = self.conn.cursor()
        # select databases
        self.conn.select_db('education')
        # parameter
        self.question = ''  # question content
        self.result = ''  # result content
        self.correct = ''  # answer for this question
        self.options = ''  # pos of answer
        self.type = ''  # question type ['单选题','多选题','填空题']

        self.isInDB = True  # if Question not in DB, Then add to DB
        self.isCorrect = True  # if Answer if false, Then Update DB

        self.rules = rules
        self.cfg = cfg
        self.ad = ad  # Android development
        self.xm = xm  # xml file decode
        self.entrance = entrance
        self.count_blank = 0
        self.p_submit = 0j  # submit botton
        self.p_next = 0j  # next botton
        self.allRight = True

    def __del__(self):
        self.conn.close()
        self.cur.close()

    def _enter(self):
        self._fresh()
        pos = self.xm.pos(self.cfg.get(self.rules, self.entrance))
        self.ad.tap(pos)

    def _getQuestion(self, str):
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
        return str

    def _fresh(self):
        # 刷新xml布局
        self.ad.uiautomator()
        self.xm.load()

    def _search(self):
        sqli = 'select Correct from questionbank where Question like %s and Classify=%s and Type=%s'
        if self.cur.execute(sqli, (self.question.replace('"', '%'), '学习强国', self.type)):
            self.isInDB = True
            self.correct = self.cur.fetchone()
            self.correct = self.correct[0]  # 仅返回正确答案
        else:
            self.isInDB = False
            # 先将题目和随机答案添加进数据库
            if self.type == '单选题':
                self.correct = 'A'
            elif self.type == '多选题':
                self.correct = 'ABC'
            else:
                self.correct = '不忘初心牢记使命 不忘初心牢记使命 不忘初心牢记使命 不忘初心牢记使命'

    def _updateDB(self):
        if self.isInDB:
            pass
        else:
            # Print Question
            print("[Update DB]")
            print("【%s】%s" % (self.type, self.question))
            sqli = 'insert into questionbank (Type,Question,Correct,Classify) value (%s,%s,%s,%s)'
            self.cur.execute(sqli, (self.type, self.question, self.correct, '学习强国'))
            if self.type == '单选题' or self.type == '多选题':
                for i in range(len(self.result)):
                    # sqli = 'update questionbank set Answer'+
                    if i == 0:
                        sqli = 'update questionbank set AnswerA = %s where Question like %s'
                    elif i == 1:
                        sqli = 'update questionbank set AnswerB = %s where Question like %s'
                    elif i == 2:
                        sqli = 'update questionbank set AnswerC = %s where Question like %s'
                    elif i == 3:
                        sqli = 'update questionbank set AnswerD = %s where Question like %s'
                    elif i == 4:
                        sqli = 'update questionbank set AnswerE = %s where Question like %s'
                    else:
                        break
                    print("* %s" % self.result[i])
                    self.cur.execute(sqli, (self.result[i], self.question.replace('"', '%')))
        self.conn.commit()
        print("【正确答案】%s" % self.correct)

    # 填空题处理
    def _blank(self):
        self.question = self.xm.content(self.cfg.get(self.rules, 'rule_blank_content'))
        self.question = self._getQuestion(self.question)
        edits = self.xm.pos(self.cfg.get(self.rules, 'rule_edits'))
        if isinstance(edits, list):
            self.count_blank = len(edits)
        else:
            self.count_blank = 1
            edits = [edits]
        self._search()
        answers = self.correct.split(' ')  # 拆分答案
        for edit, self.correct in zip(edits, answers):
            self.ad.tap(edit)
            self.ad.input(self.correct)

    # 选择题处理
    def _check(self):
        self.question = self.xm.content(self.cfg.get(self.rules, 'rule_content'))
        self.question = self._getQuestion(self.question)
        self.options = self.xm.pos(self.cfg.get(self.rules, 'rule_options'))
        self.result = self.xm.options(self.cfg.get(self.rules, 'rule_options_content'))  # 获取答案内容
        # self.result = self.result.split(' ')
        self._search()
        for c in self.correct:
            self.ad.tap(self.options[ord(c) - 65])

    def _submit(self):
        if self.p_submit == 0j:
            self._fresh()
            self.p_submit = self.xm.pos(self.cfg.get(self.rules, 'rule_submit'))
        self.ad.tap(self.p_submit)

    def _next(self):
        if self.p_next == 0j:
            self._fresh()
            self.p_next = self.xm.pos(self.cfg.get(self.rules, 'rule_next'))
        self.ad.tap(self.p_next)

    def _desc(self):
        self._fresh()
        res = self.xm.content(self.cfg.get(self.rules, 'rule_desc'))
        if '' == res:
            return True
        else:
            self.allRight = False
            self.correct = re.sub(r'正确答案：', '', res)
            return False

    def _type(self):
        self._fresh()  # 刷新xml布局文件
        return self.xm.content(self.cfg.get(self.rules, 'rule_type'))  # 返回题目类型

    def _dispatch(self):
        self.type = self._type()
        if '填空题' == self.type:
            self._blank()
        elif '单选题' == self.type or '多选题' == self.type:
            self._check()
        else:
            print('未知题目类型')
        self._submit()  # 点击确定
        # 提交答案后，获取答案解析，若为空，则回答正确，否则，返回正确答案
        if self._desc():  # 返回结果为正确无需处理
            pass
        else:
            self._submit()  # 点击下一题或者完成
        self._updateDB()  # 若不在题库中，则提交至题库

    def runDaily(self):
        score = 0
        self._enter()  # 点击开始答题
        sleep(5)
        # 每次回答5题，每日答题6组
        while True:
            self.allRight = True
            for j in range(5):
                self._dispatch()
                sleep(3)
            sleep(10)
            if self.allRight:
                score += 2
            else:
                score += 1
            if score < 6:
                self._next()  # 点击再来一组
            else:
                break
        self.ad.back()  # 返回到我要答题界面
        return True

    def runChallenge(self):
        while True:
            self.count = 15
            self._enter()  # 点击进入答题
            while True:
                if self.count <= 0:
                    sleep(30)
                    self.ad.back()
                    break
                self._submit()
                sleep(3)
                if self._reopened():  # 回答正确
                    self.count -= 1
                else:
                    self.ad.back()
                    break
            if self.count <= 0:
                sleep(3)
                self.ad.back()  # 返回到答题界面
                break


if __name__ == "__main__":
    pass
