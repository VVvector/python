# -*- coding:utf-8 -*-
from time import sleep
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class Reader:
    def __init__(self, dev, app):
        self.dev = dev
        self.app = app
        self.share = 2
        self.comment = 1
        self.delay = 15  # 每篇滑动等待时间
        self.slide = 15  # 每篇文章上滑次数

    def _read(self):
        for i in range(self.slide):
            sleep(self.delay)
            self.dev.draw('up', distance=100)
        return True

    def _share(self):
        if self.app.click('share_pos', True):
            if self.app.click('share_to_pos', True):
                self.share -= 1
            else:
                logger.error('[Error] Article Share Fail')
            self.dev.back()

    def _start(self):
        if self.app.click('start_pos', True):
            return True
        else:
            logger.error('[Error]文章收藏失败')
            return False

    def _comment(self):
        if self.app.click('comment_pos', True):
            self.dev.input_content('在党的领导下，早日实现中国梦，实现中华民族的伟大复兴。')
            self.dev.swip(986, 1708, 986, 1708)
            # if self.dev.click('publish_pos', True):
            self.comment -= 1
            # Delete Comment
            self.app.click('comment_del', True)
            if not self.app.click('comment_del_confirm', True):
                logger.error('[Error] Article Comment Fail')

    def run(self, count):
        while count > 0:
            logger.debug("check in app home page")
            if not self.app.check_in_homepage():
                self.dev.start()

            logger.debug("click 要闻")
            if not self.app.click('news_pos', False):
                self.app.restart()
                return count

            logger.debug("start reading ...")
            slide_cnt = 16 - count
            while slide_cnt > 0:
                self.dev.draw('up', 1300)
                slide_cnt -= 1

            # 获取该页面的文章位置
            poslist = self.app.get_pos('article_pos', True)
            if isinstance(poslist, complex):
                poslist = [poslist]

            # 对每篇文件进行阅读
            logger.debug("poslist: {}".format(poslist))
            for pos in poslist:
                if not self.dev.tap_pos(pos):  # Entry Article
                    continue
                count -= 1
                logger.debug('Article - ' + str(16 - count))

                logger.debug("read")
                if not self._read():
                    return count

                logger.debug("share")
                if self.share > 0:
                    self._share()

                logger.debug("comment")
                if self.comment > 0:
                    self._comment()

                if not self.app.check_in_homepage():
                    self.dev.back()
                if count == 0:
                    break
        return count
