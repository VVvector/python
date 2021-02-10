# -*- coding:utf-8 -*-
from time import sleep


class ZhengShangYou(object):
    def __init__(self, cfg, rules, ad, xm, conn, cur):
        self.cfg = cfg
        # connect MySQL
        self.conn = conn
        self.cur = cur
        # parameter
        self.cfg = cfg
        self.rules = rules
        self.ad = ad  # Android development
        self.xm = xm  # xml file decode

        self.question = ''  # question content
        self.result = ''  # result content
        self.correct = ''  # answer for this question
        self.options = ''  # pos of answer
        self.type = ''  # question type ['单选题','多选题','填空题']
        self.fun = ''  # 功能选择，进行周答题或专项答题

        self.count_blank = 0
        self.p_submit = 0j  # submit botton
        self.p_next = 0j  # next botton

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
            self.correct = "A"

    # 选择题处理
    def _check(self):
        self.question = self.xm.content(self.cfg.get(self.rules, 'rule_zhengshangyou_content'))
        # self.question = self._getQuestion(self.question)
        self.options = self.xm.pos(self.cfg.get(self.rules, 'rule_zhengshangyou_options_pos'))
        self.result = self.xm.options(self.cfg.get(self.rules, 'rule_zhengshangyou_options_content'))  # 获取答案内容
        # self._search()
        print('【题目】%s' % self.question)
        for i in range(len(self.result)):
            print(self.result[i])
        print('【答案】%s\n' % self.correct)

        # for c in self.correct:
        # self.ad.tap(self.options[ord(c)-65])

    def run(self):
        self.fun = input('请进入答题页面……')
        count = 1000
        for j in range(count):
            # self._fresh()# 刷新xml布局文件
            self._check()
            sleep(2)
        return True
