#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from time import sleep

class Video:
    def __init__(self, dev):
        self.dev = dev
        self.delay = 30 #滑动间隔时间

    def enter(self):
        self.dev.click('video_pos', True)
        self.dev.click('video_first_pos', True)

    def next(self):
        self.dev.draw('up', 1300)

    def run(self, count):
        self.enter()
        while count:       
            count -= 1
            sleep(self.delay)
            self.next()

if __name__ == "__main__":
    pass