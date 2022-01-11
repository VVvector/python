# -*- coding:utf-8 -*-
from configparser import ConfigParser
from pathlib import Path
from time import sleep
import logging
import os
import time
from . import adbUtil
from . import xmlUtil

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.DEBUG)

class Device(object):
    def __init__(self):
        cfg = ConfigParser()
        cur_path = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(cur_path, "config.ini")
        cfg.read(config_file_path, encoding='utf-8')
        self.rules = 'phone'
        self.cfg = cfg
        self.xmluri = Path(self.cfg.get(self.rules, 'xml_uri'))

        # xml
        self.xm = xmlUtil.Xmler(self.xmluri)

        # connect Android
        self.ad = adbUtil.ADB(self.xmluri, self.cfg.getboolean(self.rules, 'is_virtual_machine'),
                              self.cfg.get(self.rules, 'host'), self.cfg.getint(self.rules, 'port')
                              )
    def __del_(self):
        logger.error("del")
        self.ad.close()


    def fresh_page(self):
        self.ad.uiautomator()
        self.xm.load()

    def get_pos(self, pos_rule):
        return self.xm.pos(pos_rule)

    def tap_pos(self, pos):
        return self.ad.tap(pos)

    def draw(self, orientation='down', distance=100, duration=500):
        logger.debug("draw: {}".format(orientation))
        self.ad.draw(orientation, distance, duration)

    def input_content(self, content):
        self.ad.input(content)

    def input(self, pos, content):
        self.ad.tap(pos)
        self.ad.input(content)

    def go_homepage(self, home_activity):
        self.ad.enter_activity(home_activity)

    def check_home(self, pos_mine):
        self.fresh_page()
        if self.xm.pos(pos_mine):
            return True
        else:
            return False

    def swip(self, sx, sy, dx, dy):
        self.ad.swipe(sx, sy, dx, dy, 50)

    def click(self, pos_rule, fresh):
        count = 30
        if fresh:
            self.fresh_page()

        while count > 0:
            if count % 2 == 0 and fresh:
                self.fresh_page()
            pos = self.xm.pos(pos_rule)
            if pos:
                return self.ad.tap(pos)
            else:
                count -= 1
        return False

    def back(self):
        self.ad.back()

    def get_desktop_activity(self):
        self.ad.get_desktop_activity()

    def enter_activity(self, activity):
        self.ad.enter_activity(activity)

    def close_app(self, packet_name):
        self.ad.close_app(packet_name)

if __name__ == '__main__':
    pass
