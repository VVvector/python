# -*- coding:utf-8 -*-

from . import mysql, adble, xmler
from pathlib import Path
from time import sleep
from requests import post
import time


class Device(object):
    def __init__(self, rules, cfg):
        self.rules = rules
        self.cfg = cfg
        self.xmluri = Path(self.cfg.get(self.rules, 'xml_uri'))
        # xml
        self.xm = xmler.Xmler(self.xmluri)

        # url&log
        self.url = self.cfg.get(self.rules, 'msg_url')
        self.log = ''

        # connect Android
        self.ad = adble.Adble(
            self.xmluri,
            self.cfg.getboolean(self.rules, 'is_virtual_machine'),
            self.cfg.get(self.rules, 'host'),
            self.cfg.getint(self.rules, 'port')
        )

        # connect sql
        self.db = mysql.Mysql(
            self.cfg.get(self.rules, 'db_type'),
            self.cfg.get(self.rules, 'db_host'),
            self.cfg.getint(self.rules, 'db_port'),
            self.cfg.get(self.rules, 'db_user'),
            self.cfg.get(self.rules, 'db_pwd'),
            self.cfg.get(self.rules, 'db_name'),
            self.cfg.get(self.rules, 'db_table_name')
        )

    def _fresh(self):
        self.ad.uiautomator()
        self.xm.load()

    # log记录与消息发送
    def _gettime(self):
        ctime = time.localtime(time.time())
        return str(ctime.tm_hour) + ':' + str(ctime.tm_min) + ':' + str(ctime.tm_sec) + '    '

    def recordlog(self, log):
        print(log)
        self.log = self.log + self._gettime() + log + '\n\n'

    def sendlog(self):
        # url = self.url + 'Log&desp=' + self.log
        # post(url)
        pass

    # 数据库操作相关接口
    def search(self, q_type, q_question, is_insert):
        return self.db.search(q_type, q_question, is_insert)

    def getQuestion(self, str):
        return self.db.getQuestion(str)

    def update(self, key, value):
        self.db.update(key, value)

    # 为填空题和多选题返回pos和循环点击，后期考虑优化
    def get_pos(self, pos_rule, fresh):
        if fresh:
            self._fresh()
        pos_rule = self.cfg.get(self.rules, pos_rule)
        return self.xm.pos(pos_rule)

    def tap_pos(self, pos):
        return self.ad.tap(pos)

    def draw(self, orientation='down', distance=100, duration=500):
        self.ad.draw(orientation, distance, duration)

    def input_content(self, content):
        self.ad.input(content)

    def input(self, pos, content):
        self.ad.tap(pos)
        self.ad.input(content)

    def homepage(self):
        self.ad.enter_activity(self.cfg.get(self.rules, 'home_activity'))

    def checkhome(self):
        self._fresh()
        if self.xm.pos(self.cfg.get(self.rules, 'pos_mine')):
            return True
        else:
            return False

    def decode_option(self, content_rule, fresh):
        if fresh:
            self._fresh()
        content_rule = self.cfg.get(self.rules, content_rule)

        return self.xm.options(content_rule)

    def decode(self, content_rule, fresh):
        if fresh:
            self._fresh()
        content_rule = self.cfg.get(self.rules, content_rule)
        return self.xm.content(content_rule)

    def swip(self, sx, sy, dx, dy):
        self.ad.swipe(sx, sy, dx, dy, 50)

    def click(self, pos_rule, fresh):
        count = 30
        if fresh:
            self._fresh()
        pos_rule = self.cfg.get(self.rules, pos_rule)  # get pos_rule from config.ini
        while count > 0:
            if count % 2 == 0 and fresh:
                self._fresh()
            pos = self.xm.pos(pos_rule)
            if pos:
                return self.ad.tap(pos)
            else:
                count -= 1
        return False

    def back(self):
        self.ad.back()

    def backtohome(self):
        count = 8
        while count > 0:
            if self.checkhome():
                self.click('news_pos', False)
                return True
            self.ad.back()
            sleep(1)
            count -= 1
        self.restart()

    # 此处应保证重启成功
    def start(self):
        self.ad.enter_activity(self.cfg.get(self.rules, 'home_activity'))
        sleep(5)
        if self.click('pos_psw', True):
            self.recordlog('Login……')
            self.ad.input('h123456')
            self.click('pos_login', True)
            sleep(8)  # 登陆后等待5S才能进入主页
        if self.checkhome():
            return True
        else:
            return False

    def restart(self):
        count = 1
        while count < 3:
            self.ad.close_app(self.cfg.get(self.rules, 'packet_name'))
            if self.start():
                return
            count += 1
        self.recordlog('[Error] APP Restart Fail')
        self.sendlog()
        raise AttributeError(f'[ERROR] APP start fail')

    def exit(self):
        self.ad.close_app(self.cfg.get(self.rules, 'packet_name'))
        self.ad.close()
        self.db.close()
