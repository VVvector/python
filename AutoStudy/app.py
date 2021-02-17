# -*- coding:utf-8 -*-
from time import sleep
from common import Device
from function import question_daily, question_challenge, question_battle, question_up
from function import media_video, media_reader


class App(object):
    def __init__(self, cfg, log, question, database):
        self.cfg = cfg
        self.rules = self.cfg.get('common', 'device')
        self.dev = Device(self.rules, cfg)
        self.log = log
        self.question = question
        self.database = database

    # 每日答题
    def _question_daily(self):
        count = self.cfg.getint(self.rules, 'daily_question_cnt')
        dq = question_daily.DailyQuiz(self.dev)
        while count > 0:
            if not self.dev.checkhome():
                self.dev.restart()
            count = dq.run(count)
            self.dev.backtohome()

    # 挑战答题
    def _question_challenge(self):
        count = self.cfg.getint(self.rules, 'challenge_question_cnt')
        cq = question_challenge.ChallengeQuiz(self.dev)
        if not self.dev.checkhome():
            self.dev.restart()
        cq.run(count)
        self.dev.backtohome()

    # 争上游答题
    def _question_up(self):
        count = self.cfg.getint(self.rules, 'up_question_cnt')
        uq = question_up.UpQuiz(self.dev)
        while count > 0:
            if not self.dev.checkhome():
                self.dev.restart()
            count = uq.run(count)
        self.dev.backtohome()

    # 双人对战
    def _question_battle(self):
        bq = question_battle.BattleQuiz(self.dev)
        if not self.dev.checkhome():
            self.dev.restart()
        bq.run()
        self.dev.backtohome()

    # 视频学习
    def _video_study(self):
        count = self.cfg.getint(self.rules, 'video_cnt')
        vi = media_video.Video(self.dev)
        if not self.dev.checkhome():
            self.dev.restart()
        vi.run(count)
        self.dev.backtohome()

    # 文章阅读
    def _new_study(self):
        count = self.cfg.getint(self.rules, 'article_cnt')
        rd = media_reader.Reader(self.dev)
        if not self.dev.checkhome():
            self.dev.restart()
        while count > 0:
            count = rd.run(count)
        self.dev.backtohome()

    # 本地频道
    def _local_platform(self):
        if not self.dev.checkhome():
            self.dev.restart()
        if self.dev.click('local_beijing', True):
            sleep(2)
            if not self.dev.click('local_beijing_study', True):
                self.dev.recordlog('[Error] Open Local Platform Fail')
                return
        sleep(2)
        self.dev.back()

    def start(self):
        if not self.dev.checkhome():
            self.dev.restart()

        # 学习前分数
        self.dev.recordlog('Start Auto Study: ' + self.dev.decode('score', True))

        self.dev.recordlog('Start Local Platform')
        self._local_platform()

        self.dev.recordlog('Start Article Read')
        self._new_study()

        self.dev.recordlog('Start Challenge Question')
        self._question_challenge()

        self.dev.recordlog('Start Daily Question')
        self._question_daily()

        self.dev.recordlog('Start Up Question')
        self._question_up()

        self.dev.recordlog('Start Battle Question')
        self._question_battle()

        self.dev.recordlog('Start Video Study')
        self._video_study()

        # 记录学习后分数
        self.dev.recordlog('End Auto Study: ' + self.dev.decode('score', True))
        self.dev.sendlog()

        self.dev.exit()
