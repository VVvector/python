#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from time import sleep

class Reader:
    def __init__(self, dev):
        self.dev = dev
        self.share = 2
        self.comment = 1
        self.delay = 15  #每篇滑动等待时间
        self.slide = 15 #每篇文章上滑次数

    def _read(self):
        if self.dev.checkhome():
            return False
        for i in range(self.slide):
            sleep(self.delay)
            self.dev.draw('up', distance=100)
        return True

    def _share(self):
        if self.dev.click('share_pos', True):
            if self.dev.click('share_to_pos', True):
                self.share -= 1
            else:
                self.dev.recordlog('[Error] Article Share Fail')
            self.dev.back()

    def _start(self):
        if self.dev.click('start_pos', True):
            return True
        else:
            self.dev.recordlog('[Error]文章收藏失败')
            return False

    def _comment(self):
        if self.dev.click('comment_pos', True):
            self.dev.input_content('在党的领导下，早日实现中国梦，实现中华民族的伟大复兴。')
            self.dev.swip(986,1708,986,1708)
            #if self.dev.click('publish_pos', True):
            self.comment -= 1
            #Delete Comment
            self.dev.click('comment_del',True)
            if not self.dev.click('comment_del_confirm',True):
                self.dev.recordlog('[Error] Article Comment Fail')

    def run(self, count):
        while count > 0:
            if not self.dev.checkhome():
                self.dev.start()
            if not self.dev.click('news_pos', False):
                self.dev.restart()
                return count
            slide_cnt = 16 - count
            while slide_cnt > 0:
                self.dev.draw('up', 1300)
                slide_cnt -= 1
            poslist = self.dev.get_pos('article_pos', True)
            if isinstance(poslist, complex):
                poslist = [poslist]
            for pos in poslist:
                if not self.dev.tap_pos(pos):   #Entry Article
                    continue 
                count -= 1
                self.dev.recordlog('Article - ' + str(16-count))                    
                if not self._read():
                    return count
                if self.share > 0:
                    self._share()
                if self.comment > 0:
                    self._comment()
                if not self.dev.checkhome():
                    self.dev.back()
                if count == 0:
                    break
        return count