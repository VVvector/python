# -*- coding:utf-8 -*-
from configparser import ConfigParser
from time import sleep
import os
import requests
import random
import json
from common import util

logger = util.get_logger(__name__)


class App(object):
    def __init__(self, device, db=None):
        cfg = ConfigParser()
        cur_path = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(cur_path, "config.ini")
        cfg.read(config_file_path, encoding='utf-8')

        self.dev = device
        self.cfg = cfg
        self.rules = 'monitor_rule'
        self.start_times = 0

        cur_path = os.path.dirname(os.path.abspath(__file__))
        user_info_path = os.path.join(cur_path, "user_info.json")
        self.user_info_list = []
        with open(user_info_path, 'r') as f:
            user_info_dict = json.load(f)
            self.user_info_list = user_info_dict["user_info"]
            logger.debug(self.user_info_list)

        self.user = None
        self.psd = None
        self.push_link = None

    def get_position_rule(self, position_name):
        return self.cfg.get(self.rules, position_name)

    def get_position(self, pos_name, fresh):
        if fresh:
            self.dev.fresh_page()
        pos_rule = self.cfg.get(self.rules, pos_name)
        logger.debug(pos_rule)
        return self.dev.get_position(pos_rule)

    def click(self, position_name, fresh):
        return self.dev.click(self.cfg.get(self.rules, position_name), fresh)

    def check_homepage(self):
        count = 3
        while count > 0:
            count -= 1
            self.dev.fresh_page()
            page_content = self.dev.get_text(self.cfg.get(self.rules, '主页'))
            text_list = page_content.split(' ')
            if "学习" in text_list and "共享" in text_list and "业务" in text_list and "我的" in text_list:
                return True
            else:
                logger.debug("进入主页失败")
                return False

    def start(self):
        logger.debug("启动 石化党建 软件")

        # 防止死循环，导致过多启动和停止app
        self.start_times += 1
        if self.start_times > 6:
            logger.error('failed to restart APP')
            raise AttributeError('failed to restart APP')

        self.dev.set_activity(self.cfg.get(self.rules, '软件启动'))
        sleep(5)

        logger.debug("查看是否需要登录")
        if not self.check_homepage():
            if self.dev.click(self.cfg.get(self.rules, '用户名'), True):
                for i in range(20):
                    self.dev.delete()
                logger.debug("输入用户名")
                self.dev.set_text(self.user)
            if self.dev.click(self.cfg.get(self.rules, '密码'), True):
                logger.debug("输入密码")
                self.dev.set_text(self.psd)

            self.dev.click(self.cfg.get(self.rules, '登录'), True)
            logger.debug("等待登录。。。")
            sleep(6)

        # 确认系统过久的提示
        self.dev.fresh_page()
        self.dev.click(self.cfg.get(self.rules, '系统提示确认'), True)

        if self.check_homepage():
            logger.debug("登录成功!")
            return True
        else:
            logger.debug("登录失败!")
            return False

    def restart(self):
        logger.debug("重新启动 石化党建 软件")
        count = 1
        while count < 3:
            logger.debug("关闭 石化党建 软件")
            self.dev.close_application(self.cfg.get(self.rules, '软件包名字'))
            sleep(3)
            if self.start():
                return
            count += 1

        logger.error('failed to restart APP')
        raise AttributeError('failed to restart APP')

    def stop(self):
        self.dev.close_application(self.cfg.get(self.rules, '软件包名字'))

    def click_bottom(self, bottom_name):
        if self.dev.click(self.cfg.get(self.rules, bottom_name), True):
            return True
        else:
            logger.debug("进入 <{}> 页面失败".format(bottom_name))
            self.dev.save_page_xml(bottom_name)
            return False

    def back_to_homepage(self):
        i = 5
        ret = False
        while i > 0:
            i -= 1
            if not self.check_homepage():
                self.dev.back()
                sleep(1)
            else:
                ret = True
                break

        if not ret:
            logger.debug("保存进入主页失败时的页面xml文件")
            self.dev.save_page_xml("主页检查失败")
            self.restart()

    def update_user_info(self, i):
        self.user = self.user_info_list[i]["name"]
        self.psd = self.user_info_list[i]["psd"]
        self.push_link = self.user_info_list[i]["push_link"]
        logger.info("user info: {}, {}, {}".format(self.user, self.psd, self.push_link))

    def enter_my_points_page(self):
        self.back_to_homepage()
        self.click_bottom("学习")
        self.click_bottom("我的")
        self.click_bottom("我的积分")

    def listen_voice_of_party(self):
        logger.info("开始 - 收听“党建之声”")
        self.click_bottom("收听党建之声")
        sleep(random.randint(2, 5))
        # 播放
        self.click_bottom("收听党建之声的播放")
        sleep(random.randint(2, 5))
        # 暂停
        # self.click_bottom("收听党建之声的暂停")
        logger.info("结束 - 收听“党建之声”")

    def read_article(self):
        logger.info("开始 - 阅读文章")
        self.click_bottom("阅读文章")
        sleep(6)
        self.click_bottom("第一学习的更多")
        sleep(6)
        for i in range(5):
            pos_list = self.get_position("第一学习的文章列表", True)
            logger.debug("阅读第{}篇文章".format(i))
            self.dev.tap_position(pos_list[i])
            sleep(1)
            self.dev.draw('up', distance=100)
            sleep(random.randint(1, 3))
            self.dev.back()
            sleep(1)
        logger.info("结束 - 阅读文章")

    def read_special_article(self):
        logger.info("开始 - 阅读专题栏目文章")
        self.click_bottom("阅读专题栏目文章")
        sleep(random.randint(2, 5))
        self.click_bottom("学党史")
        self.click_bottom("上级精神的第一篇文章")
        # 学习3分钟
        sleep(3 * 60 + random.randint(1, 20))
        logger.info("结束 - 阅读专题栏目文章")

    def browse_company_websites(self):
        logger.info("开始 - 浏览企业所在门户")
        self.dev.draw('up', distance=400)
        self.dev.draw('up', distance=500)
        self.click_bottom("浏览所在企业门户")
        sleep(6)
        self.click_bottom("工作动态的更多")
        sleep(6)
        pos_list = self.get_position("工作动态的第一篇文章", True)
        self.dev.tap_position(pos_list[0])
        # 学习30秒
        sleep(30 + random.randint(1, 10))
        logger.info("结束 - 浏览企业所在门户")

    def browse_external_websites(self):
        logger.info("开始 - 通过平台链接浏览外部网站")
        self.dev.draw('up', distance=400)
        self.dev.draw('up', distance=500)
        self.click_bottom("通过平台链接浏览外部网站")
        sleep(3)
        self.click_bottom("学习进行时")
        sleep(random.randint(1, 3))
        logger.info("结束 - 通过平台链接浏览外部网站")

    def daily_practice(self):
        logger.info("开始 - 每日练习")
        self.click_bottom("每日练习")
        sleep(1)

        # 获取 单选题 选项，且做出选择

        # 提交答案

        # 检查，并获取正确答案

        # 重新答题

        logger.info("结束 - 每日练习")

    def push_points_to_phone(self):
        logger.info("开始 - 发送积分到手机")
        points_pos = self.cfg.get(self.rules, "今日积分")
        logger.debug(points_pos)

        send_text = "石化党建-{}".format(self.dev.get_text(points_pos))
        logger.debug(send_text)

        url = self.push_link
        url = '{}{}'.format(url, send_text)
        requests.post(url)

        logger.info("结束 - 发送积分到手机")

    def auto_test(self):
        if not self.check_homepage():
            self.restart()

        self.enter_my_points_page()
        self.listen_voice_of_party()

        self.enter_my_points_page()
        self.read_article()

        self.enter_my_points_page()
        self.read_special_article()

        self.enter_my_points_page()
        self.browse_company_websites()

        self.enter_my_points_page()
        self.browse_external_websites()

        self.enter_my_points_page()
        self.push_points_to_phone()

    def test_ui(self):
        for i in range(len(self.user_info_list)):
            self.update_user_info(i)
            self.auto_test()
        self.stop()
