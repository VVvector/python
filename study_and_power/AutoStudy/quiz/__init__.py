# -*- coding:utf-8 -*-
from time import sleep
from .challenge import ChallengeQuiz
from .daily import DailyQuiz
from .zhengshangyou import ZhengShangYou


class Quiz(object):
    def __init__(self, cfg, rules, ad, xm, conn, cur):
        self.cfg = cfg
        self.rules = rules
        self.ad = ad
        self.xm = xm
        self.conn = conn
        self.cur = cur
        self.home = 0j
        self.mine = 0j

    def _fresh(self):
        self.ad.uiautomator()
        self.xm.load()

    def start(self, day, chg):
        # 点击我的
        self._fresh()
        self.mine = self.xm.pos(self.cfg.get(self.rules, 'rule_bottom_mine'))
        self.ad.tap(self.mine)

        # 点击我要答题
        sleep(2)
        self._fresh()
        pos = self.xm.pos(self.cfg.get(self.rules, 'rule_quiz_entry'))
        self.ad.tap(pos)

        # zq = ZhengShangYou(self.cfg, self.rules, self.ad, self.xm)
        # zq.run();
        if day:
            print('开始每日答题')
            dq = DailyQuiz(self.cfg, self.rules, self.ad, self.xm, self.conn, self.cur)
            dq.run()
            sleep(5)
        if chg:
            print('开始挑战答题')
            cq = ChallengeQuiz(self.cfg, self.rules, self.ad, self.xm, self.conn, self.cur)
            cq.run()
            sleep(5)
        self._fresh()
        self.home = self.xm.pos(self.cfg.get(self.rules, 'rule_bottom_work'))
        self.ad.tap(self.home)
        sleep(5)
