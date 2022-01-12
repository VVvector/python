# -*- coding:utf-8 -*-
from configparser import ConfigParser
from time import sleep
import os
import logging
import requests

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
        count = 3

        while count:
            count -= 1
            self.dev.fresh_page()

            if self.dev.get_pos(self.cfg.get(self.rules, 'home_page_pos')):
                logger.debug("in homepage")
                return True
            else:
                logger.debug("not in homepage")
                return False

    def start(self):
        logger.debug("start shihua app")
        self.dev.enter_activity(self.cfg.get(self.rules, 'home_activity'))
        sleep(10)

        logger.debug("check if need input password")
        if not self.check_in_homepage():
            if self.dev.click(self.cfg.get(self.rules, 'pos_psw'), True):
                logger.debug("input shihua app password")
                self.dev.input_content('QWEr1234')
                self.dev.click(self.cfg.get(self.rules, 'pos_login'), True)
                # 登陆后等待15S才能进入主页
                sleep(6)

        self.dev.fresh_page()
        self.dev.click(self.cfg.get(self.rules, 'system_update_bottom'), True)

        logger.debug("check login shihua app ....")
        if self.check_in_homepage():
            logger.debug("login shihua app success!")
            return True
        else:
            logger.debug("login shihua app failed!")
            return False

    def restart(self):
        logger.debug("restart shihua app")
        count = 1
        while count < 3:
            self.dev.close_app(self.cfg.get(self.rules, 'packet_name'))
            sleep(3)
            if self.start():
                return
            count += 1

        logger.error('[Error] APP Restart Fail')
        raise AttributeError(f'[ERROR] APP start fail')

    def stop(self):
        self.dev.close_app(self.cfg.get(self.rules, 'packet_name'))

    def exit(self):
        self.dev.close_app(self.cfg.get(self.rules, 'packet_name'))
        self.dev.close_dev()

    def click_bottom(self, bottom_name):
        logger.debug("start enter: {}".format(bottom_name))
        if self.dev.click(self.cfg.get(self.rules, bottom_name), True):
            logger.debug("enter {} page success!".format(bottom_name))
            return True
        else:
            logger.debug("enter {} page failed!".format(bottom_name))
            return False

    def back_to_homepage(self):
        i = 5
        while i > 0:
            i -= 1
            if not self.check_in_homepage():
                self.dev.back()
            else:
                break

        if not self.check_in_homepage():
            self.restart()

    def listen_voice_of_party(self):
        logger.info("开始 - 收听“党建之声”")
        self.click_bottom("wode_bottom")
        sleep(1)
        self.click_bottom("wodejifen_pos")
        sleep(1)
        self.click_bottom("dangjianzhishen_pos")

        # 播放
        self.click_bottom("play_bottom")

        sleep(3)

        # 暂停
        self.click_bottom("pause_bottom")

        self.back_to_homepage()
        logger.info("结束 - 收听“党建之声”")

    def read_article(self):
        logger.info("开始 - 阅读文章")
        self.click_bottom("wode_bottom")
        sleep(1)
        self.click_bottom("wodejifen_pos")
        sleep(1)
        self.click_bottom("yueduwenzhang_pos")

        # 进入第一学习的更多
        self.click_bottom("yueduwenzhang_gengduo_pos")
        sleep(5)

        for i in range(5):
            pos_list = self.get_pos("yueduwenzhang_wenzhang_pos", True)
            logger.debug("阅读第{}篇文章".format(i))
            self.dev.tap_pos(pos_list[i])
            sleep(1)
            self.dev.draw('up', distance=100)
            sleep(1)
            self.dev.back()
            sleep(1)

        self.back_to_homepage()
        logger.info("结束 - 阅读文章")

    def read_special_article(self):
        logger.info("开始 - 阅读专题栏目文章")
        self.click_bottom("wode_bottom")
        sleep(1)
        self.click_bottom("wodejifen_pos")
        sleep(1)
        self.click_bottom("yueduzhuanti_pos")
        sleep(1)
        self.click_bottom("zhuangti_choose_pos")

        self.click_bottom("zhuangti_article_pos")
        sleep(5)

        self.back_to_homepage()
        logger.info("结束 - 阅读专题栏目文章")

    def browse_company_websites(self):
        logger.info("开始 - 浏览企业所在门户")
        self.click_bottom("wode_bottom")
        sleep(1)
        self.click_bottom("wodejifen_pos")
        sleep(1)

        self.dev.draw('up', distance=400)
        self.click_bottom("liulanmenhu_pos")
        sleep(1)

        # 进入的更多
        self.click_bottom("liulanmenhu_gengduo_pos")
        sleep(5)

        pos_list = self.get_pos("liulanmenhu_article_pos", True)
        self.dev.tap_pos(pos_list[0])
        sleep(5)

        self.back_to_homepage()
        logger.info("结束 - 浏览企业所在门户")

    def browse_external_websites(self):
        logger.info("开始 - 通过平台链接浏览外部网站")
        self.click_bottom("wode_bottom")
        sleep(1)
        self.click_bottom("wodejifen_pos")
        sleep(1)

        self.dev.draw('up', distance=400)
        self.click_bottom("lianjie_pos")
        sleep(1)

        self.click_bottom("jingxingshi_pos")
        sleep(5)

        self.back_to_homepage()
        logger.info("结束 - 通过平台链接浏览外部网站")

    def daily_practice(self):
        logger.info("开始 - 每日练习")
        self.click_bottom("wode_bottom")
        sleep(1)
        self.click_bottom("wodejifen_pos")
        sleep(1)
        self.click_bottom("meirilianxi_pos")
        sleep(1)

        # 获取 单选题 选项，且做出选择

        # 提交答案

        # 检查，并获取正确答案

        # 重新答题

        self.back_to_homepage()
        logger.info("结束 - 每日练习")

    def push_points_to_phone(self):
        logger.info("开始 - 发送积分到手机")
        self.click_bottom("wode_bottom")
        sleep(1)
        self.click_bottom("wodejifen_pos")
        sleep(2)

        points_pos = self.cfg.get(self.rules, "jinrileiji_pos")
        logger.debug(points_pos)

        send_text = "石化党建-{}".format(self.dev.get_context(points_pos))
        logger.debug(send_text)

        url = ''
        requests.post(url)

        self.back_to_homepage()
        logger.info("结束 - 发送积分到手机")

    def test_ui(self):
        if not self.check_in_homepage():
            self.restart()

        self.listen_voice_of_party()

        self.read_article()

        self.read_special_article()

        self.browse_company_websites()

        self.browse_external_websites()

        self.push_points_to_phone()

        self.stop()