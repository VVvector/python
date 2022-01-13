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
        self.dev.enter_activity(self.cfg.get(self.rules, '软件启动'))

    def check_in_homepage(self):
        count = 3
        while count > 0:
            count -= 1
            self.dev.fresh_page()
            if self.dev.get_pos(self.cfg.get(self.rules, '主页')):
                return True
            else:
                logger.debug("进入主页失败")
                return False

    def start(self):
        logger.debug("启动 石化党建 软件")
        self.dev.enter_activity(self.cfg.get(self.rules, '软件启动'))
        sleep(10)

        logger.debug("查看是否需要登录")
        if not self.check_in_homepage():
            if self.dev.click(self.cfg.get(self.rules, '密码'), True):
                logger.debug("输入密码")
                self.dev.input_content(self.cfg.get(self.rules, '实际密码'))
                self.dev.click(self.cfg.get(self.rules, '登录'), True)
                logger.debug("等待登录。。。")
                sleep(6)

        # 确认系统过久的提示
        self.dev.fresh_page()
        self.dev.click(self.cfg.get(self.rules, '系统提示确认'), True)

        if self.check_in_homepage():
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
            self.dev.close_app(self.cfg.get(self.rules, '软件包名字'))
            sleep(3)
            if self.start():
                return
            count += 1

        logger.error('[Error] APP Restart Fail')
        raise AttributeError(f'[ERROR] APP start fail')

    def stop(self):
        self.dev.close_app(self.cfg.get(self.rules, '软件包名字'))

    def exit(self):
        self.dev.close_app(self.cfg.get(self.rules, '软件包名字'))
        self.dev.close_dev()

    def click_bottom(self, bottom_name):
        if self.dev.click(self.cfg.get(self.rules, bottom_name), True):
            logger.debug("进入 <{}> 成功".format(bottom_name))
            return True
        else:
            logger.debug("进入 <{}> 失败".format(bottom_name))
            self.dev.save_page_xml(bottom_name)
            return False

    def back_to_homepage(self):
        i = 5
        ret = False
        while i > 0:
            i -= 1
            if not self.check_in_homepage():
                self.dev.back()
                sleep(1)
            else:
                ret = True
                break

        if  not ret:
            logger.debug("保存进入主页失败时的页面xml文件")
            self.dev.save_page_xml("主页检查失败")
            self.restart()

    def listen_voice_of_party(self):
        logger.info("开始 - 收听“党建之声”")
        self.click_bottom("我的")
        sleep(1)
        self.click_bottom("我的积分")
        sleep(1)
        self.click_bottom("收听党建之声")

        # 播放
        self.click_bottom("收听党建之声的播放")

        sleep(3)

        # 暂停
        # self.click_bottom("pause_bottom")

        self.back_to_homepage()
        logger.info("结束 - 收听“党建之声”")

    def read_article(self):
        logger.info("开始 - 阅读文章")
        self.click_bottom("我的")
        sleep(1)
        self.click_bottom("我的积分")
        sleep(1)
        self.click_bottom("阅读文章")
        sleep(3)
        self.click_bottom("第一学习的更多")
        sleep(3)

        for i in range(5):
            pos_list = self.get_pos("第一学习的文章列表", True)
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
        self.click_bottom("我的")
        sleep(1)
        self.click_bottom("我的积分")
        sleep(1)
        self.click_bottom("阅读专题栏目文章")
        sleep(1)
        self.click_bottom("学党史")

        self.click_bottom("上级精神的第一篇文章")

        # 学习3分钟
        sleep(185)

        self.back_to_homepage()
        logger.info("结束 - 阅读专题栏目文章")

    def browse_company_websites(self):
        logger.info("开始 - 浏览企业所在门户")
        self.click_bottom("我的")
        sleep(1)
        self.click_bottom("我的积分")
        sleep(1)

        self.dev.draw('up', distance=400)
        self.click_bottom("浏览所在企业门户")
        sleep(1)

        self.click_bottom("工作动态的更多")
        sleep(5)

        pos_list = self.get_pos("工作动态的第一篇文章", True)
        self.dev.tap_pos(pos_list[0])

        # 学习30秒
        sleep(35)

        self.back_to_homepage()
        logger.info("结束 - 浏览企业所在门户")

    def browse_external_websites(self):
        logger.info("开始 - 通过平台链接浏览外部网站")
        self.click_bottom("我的")
        sleep(1)
        self.click_bottom("我的积分")
        sleep(1)

        self.dev.draw('up', distance=400)
        self.click_bottom("通过平台链接浏览外部网站")
        sleep(1)

        self.click_bottom("学习进行时")
        sleep(5)

        self.back_to_homepage()
        logger.info("结束 - 通过平台链接浏览外部网站")

    def daily_practice(self):
        logger.info("开始 - 每日练习")
        self.click_bottom("我的")
        sleep(1)
        self.click_bottom("我的积分")
        sleep(1)
        self.click_bottom("每日练习")
        sleep(1)

        # 获取 单选题 选项，且做出选择

        # 提交答案

        # 检查，并获取正确答案

        # 重新答题

        self.back_to_homepage()
        logger.info("结束 - 每日练习")

    def push_points_to_phone(self):
        logger.info("开始 - 发送积分到手机")
        self.click_bottom("我的")
        sleep(1)
        self.click_bottom("我的积分")
        sleep(2)

        points_pos = self.cfg.get(self.rules, "今日积分")
        logger.debug(points_pos)

        send_text = "石化党建-{}".format(self.dev.get_context(points_pos))
        logger.debug(send_text)

        url = self.cfg.get(self.rules, "推送链接")
        url = '{}{}'.format(url, send_text)
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
