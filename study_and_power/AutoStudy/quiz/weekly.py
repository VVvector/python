# -*- coding:utf-8 -*-
import re
import pymysql
from time import sleep
from pathlib import Path


class WeeklyQuiz(object):
    def __init__(self, cfg, rules, ad, xm):
        # connect MySQL
        self.conn = pymysql.connect(host='192.168.3.4', port=3306, user='root', passwd='123qwe???')
        self.cur = self.conn.cursor()
        # select databases
        self.conn.select_db('education')
        # parameter
        self.question = ''  # question content
        self.result = ''  # result content
        self.correct = ''  # answer for this question
        self.options = ''  # pos of answer
        self.type = ''  # question type ['单选题','多选题','填空题']
        self.fun = ''  # 功能选择，进行周答题或专项答题

        self.cfg = cfg
        self.rules = rules
        self.ad = ad  # Android development
        self.xm = xm  # xml file decode
        self.count_blank = 0
        self.p_submit = 0j  # submit botton
        self.p_next = 0j  # next botton

    def __del__(self):
        self.conn.close()
        self.cur.close()

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
            self.correct = self.cur.fetchone()
            self.correct = self.correct[0]  # 仅返回正确答案
        else:
            # 先将题目和随机答案添加进数据库
            self.correct = input('请输入正确答案')
            sqli = 'insert into questionbank (Type,Question,Correct,Classify) value (%s,%s,%s,%s)'
            if self.cur.execute(sqli, (self.type, self.question, self.correct, '学习强国')):
                print("【Update DB】")
                print('【%s】%s' % (self.type, self.question))
            else:
                print("【Update DB Error】")
            self.conn.commit()
            if self.type == '单选题' or self.type == '多选题':
                for i in range(len(self.result)):
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
                        print('答案超过五个')
                        break
                    self.cur.execute(sqli, (self.result[i], self.question.replace('"', '%')))
                self.conn.commit()

    # 填空题处理
    def _blank(self):
        self.question = self.xm.content(self.cfg.get(self.rules, 'rule_blank_content'))
        self.question = self._getQuestion(self.question)
        edits = self.xm.pos(self.cfg.get(self.rules, 'rule_edits'))
        print('【%s】%s' % (self.type, self.question))
        if isinstance(edits, list):
            self.count_blank = len(edits)
        else:
            self.count_blank = 1
            edits = [edits]
        self._search()
        print('【答案】%s\n' % self.correct)
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
        self._search()
        print('【%s】%s' % (self.type, self.question))
        print('【答案】%s\n' % self.correct)
        for c in self.correct:
            self.ad.tap(self.options[ord(c) - 65])

    def _submit(self):
        print('点击确定按钮')
        '''
        self._fresh()
        self.p_submit = self.xm.pos(cfg.get(self.rules, 'rule_submit'))
        self.ad.tap(self.p_submit)
        '''

    def _next(self):
        print('点击确定按钮')
        '''
        self._fresh()
        self.p_next = self.xm.pos(cfg.get(self.rules, 'rule_next'))
        self.ad.tap(self.p_next)
        '''

    def _desc(self):
        self._fresh()
        res = self.xm.content(self.cfg.get(self.rules, 'rule_desc'))
        if '' == res:
            return True
        else:
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
            sqli = 'update questionbank set Correct = %s where Question like %s'
            if self.cur.execute(sqli, (self.correct, self.question.replace('"', '%'))):
                print('【答案】%s\n' % self.correct)
                self.conn.commit()
            else:
                print('【Update DB Error】')
            self._submit()  # 点击下一题或者完成

    def run(self):
        self.fun = input('请进入答题页面……')
        count = 5
        for j in range(count):
            self._dispatch()
        self.ad.back()  # 点击返回
        sleep(1)  # 需要再点击一次返回
        self.ad.back()  # 点击返回
        return True


if __name__ == "__main__":
    from argparse import ArgumentParser
    from ..common import adble, xmler

    parse = ArgumentParser()
    parse.add_argument('-v', '--virtual', metavar='virtual', nargs='?', const=True, type=bool, default=False,
                       help='是否模拟器')

    args = parse.parse_args()
    path = Path('D:/Documents/uimumu.xml')
    ad = adble.Adble(path, args.virtual)
    xm = xmler.Xmler(path)
    cg = WeeklyQuiz('mumu', ad, xm)
    cg.run()
    ad.close()
