# -*- coding:utf-8 -*-
from configparser import ConfigParser
from pathlib import Path
import logging
import os
import time
from . import adbUtil
from . import xmlUtil

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class Device(object):
    def __init__(self):
        cfg = ConfigParser()
        cur_path = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(cur_path, "config.ini")
        cfg.read(config_file_path, encoding='utf-8')
        self.rules = 'phone'
        self.cfg = cfg
        self.xml_path = Path(self.cfg.get(self.rules, 'xml_path'))

        self.xml = xmlUtil.Xmler(self.xml_path)
        self.adb = adbUtil.ADB(self.xml_path, self.cfg.getboolean(self.rules, 'is_virtual_machine'),
                               self.cfg.get(self.rules, 'host'),
                               self.cfg.getint(self.rules, 'port'))

    def __del__(self):
        logger.debug("close device")
        self.adb.close()

    def fresh_page(self):
        self.adb.get_position_xml()
        self.xml.load()

    def get_text(self, text_rule):
        self.fresh_page()
        return self.xml.get_content(text_rule)

    def set_text(self, content):
        self.adb.input(content)

    def click_and_set_text(self, pos, content):
        self.adb.tap(pos)
        self.adb.input(content)

    def get_position(self, position_rule):
        return self.xml.get_position(position_rule)

    def tap_position(self, pos):
        return self.adb.tap(pos)

    def draw(self, orientation='down', distance=100, duration=500):
        self.adb.draw(orientation, distance, duration)

    def startup_application(self, startup_activity):
        self.adb.set_activity(startup_activity)

    def check_current_page(self, page_rule):
        self.fresh_page()
        if self.xml.get_position(page_rule):
            return True
        else:
            return False

    def swipe(self, sx, sy, dx, dy):
        self.adb.swipe(sx, sy, dx, dy, 50)

    def click(self, position_rule, fresh):
        count = 30
        if fresh:
            self.fresh_page()

        while count > 0:
            if count % 2 == 0 and fresh:
                self.fresh_page()
            pos = self.xml.get_position(position_rule)
            if pos:
                return self.adb.tap(pos)
            else:
                count -= 1
        return False

    def back(self):
        logger.debug("返回到上一级")
        self.adb.back()

    def set_activity(self, activity):
        self.adb.set_activity(activity)

    def close_application(self, application_packet_name):
        self.adb.close_app(application_packet_name)

    def save_page_xml(self, file_name):
        file_name = "{}-{}".format(time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()), file_name)
        self.xml.save_page_xml(file_name)


if __name__ == '__main__':
    pass
