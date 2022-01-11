# -*- coding:utf-8 -*-
from pathlib import Path
from configparser import ConfigParser
from time import sleep
import os
import logging

from . import question_daily
from . import question_challenge
from . import question_battle
from . import question_up
from . import media_video
from . import media_reader

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class App(object):
    def __init__(self, device, db):
        cfg = ConfigParser()
        cur_path = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(cur_path, "config.ini")
        cfg.read(config_file_path, encoding='utf-8')
        self.dev = device
        self.cfg = cfg
        self.rules = 'monitor_rule'

    def get_pos_rule(self, pos_name):
        return self.cfg.get(self.rules, pos_name)

    def get_pos(self, pos_name, fresh):
        if fresh:
            self.dev.fresh_page()
        pos_rule = self.cfg.get(self.rules, pos_name)
        logger.debug(pos_rule)
        return self.dev.xm.pos(pos_rule)

    def click(self, pos_name, fresh):
        return self.dev.click(self.cfg.get(self.rules, pos_name), fresh)

    def go_app_homepage(self):
        self.dev.enter_activity(self.cfg.get(self.rules, 'home_activity'))

    def check_in_homepage(self):
        self.dev.fresh_page()
        if self.dev.get_pos(self.cfg.get(self.rules, 'pos_mine')):
            return True
        else:
            logger.debug("not in homepage")
            return False

    def start(self):
        logger.debug("start xuexi app")
        self.dev.enter_activity(self.cfg.get(self.rules, 'home_activity'))
        sleep(10)

        if not self.check_in_homepage():
            if self.dev.click(self.cfg.get(self.rules, 'pos_psw'), True):
                logger.debug("login xuexi app")
                self.dev.input_content('QWEr1234')
                self.dev.click(self.cfg.get(self.rules, 'pos_login'), True)
                # 登陆后等待5S才能进入主页
                sleep(15)

        logger.debug("check login xuexi app ....")
        if self.check_in_homepage():
            logger.debug("login xuexi app success!")
            return True
        else:
            logger.debug("login xuexi app failed!")
            return False

    def restart(self):
        count = 1
        while count < 3:
            self.dev.close_app(self.cfg.get(self.rules, 'packet_name'))
            sleep(3)
            if self.start():
                return
            count += 1

        logger.error('[Error] APP Restart Fail')
        raise AttributeError(f'[ERROR] APP start fail')

    def exit(self):
        self.dev.close_app(self.cfg.get(self.rules, 'packet_name'))
        self.dev.close_dev()

    # 文章阅读
    def artical_study(self):
        logger.debug("start to read article")
        count = self.cfg.getint(self.rules, 'article_cnt')

        rd = media_reader.Reader(self.dev, self)
        if not self.check_in_homepage():
            self.restart()

        logger.debug("===read article working...===")
        while count > 0:
            count = rd.run(count)
