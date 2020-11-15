# -*- coding:utf-8 -*-
from time import sleep


class ChallengeQuiz(object):
    def __init__(self, cfg, rules, ad, xm, conn, cur):
        self.cfg = cfg
        # connect MySQL
        self.conn = conn
        self.cur = cur
        # parameter
        self.rules = rules
        self.ad = ad
        self.xm = xm
        self.count = 0

        self.question = ''
        self.options = ''
        self.answer = ''  # Correct answer
        self.pos = ''
        self.p_back = 0j
        self.p_return = 0j
        self.p_share = 0j

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

    # 点击进入挑战答题
    def _enter(self):
        self._fresh()
        pos = self.xm.pos(self.cfg.get(self.rules, 'rule_challenge_entry'))
        self.ad.tap(pos)
        sleep(2)

    # 点击结束本局
    def _end(self):
        self._fresh()
        pos = self.xm.pos(self.cfg.get(self.rules, 'rule_end_bounds'))
        self.ad.tap(pos)
        sleep(1)

    # 点击再来一局
    def _again(self):
        self._fresh()
        pos = self.xm.pos(self.cfg.get(self.rules, 'rule_again_bounds'))
        self.ad.tap(pos)
        sleep(1)

    def _fresh(self):
        self.ad.uiautomator()
        self.xm.load()

    def _content(self):
        res = self.xm.content(self.cfg.get(self.rules, 'rule_challenge_content'))
        return res

    def _pos(self):
        res = self.xm.pos(self.cfg.get(self.rules, 'rule_challenge_options_bounds'))
        return res

    def _search(self):
        sqli = 'select Correct from Questionbank where Question like %s and Classify=%s LIMIT 1'
        if self.cur.execute(sqli, (self.question.replace('"', '%'), '学习强国')):
            self.answer = self.cur.fetchone()
            self.answer = self.answer[0]
        else:
            self.answer = 'A'  # 填写答案A

    def _submit(self):
        self._fresh()
        self.question = self._content()  # 获取题目内容
        # print(self.question)
        self.question = self._getQuestion(self.question)
        self.pos = self._pos()  # 选项点击位置
        # 查询数据库
        self._search()
        cursor = ord(self.answer) - 65
        sleep(3)  # 延时按钮
        # 点击正确选项
        while 0j == self.pos[cursor]:
            self.ad.draw('up')
            self._fresh()
            self.pos = self._pos()
        # 现在可以安全点击(触摸)
        self.ad.tap(self.pos[cursor])

    def _reopened(self, repeat: bool = False) -> bool:
        self._fresh()
        # 本题答对否
        if not self.xm.pos(self.cfg.get(self.rules, 'rule_judge_bounds')):
            return True
        else:
            return False

    def run(self):
        score = 0
        self._enter()  # 点击进入答题
        while True:
            self.count = 0
            while True:
                if self.count // 5 + score >= 3:
                    score = score + self.count // 5
                    sleep(30)
                    self.ad.back()
                    break
                self._submit()
                sleep(3)
                if self._reopened():  # 回答正确
                    self.count += 1
                else:
                    score = score + self.count // 5
                    print("当前得分：%d" % (score * 2))
                    self._end()
                    self._again()
            if score >= 3:
                sleep(3)
                self.ad.back()  # 返回到答题界面
                break
