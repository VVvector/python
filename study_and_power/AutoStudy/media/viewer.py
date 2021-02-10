# -*- coding:utf-8 -*-
from time import sleep
from common import timerUtil

'''设计思路：
    1. 点击‘百灵’，下拉刷新
    2. 点击第一个视频进入观看
    3. 延时指定时间后上划屏幕，进入下一则视频
    4. 重复步骤3直到完成指定视频数
    5. 右划退出观看，点击Home返回首页
'''


class Viewer:
    def __init__(self, cfg, rules, ad, xm):
        self.cfg = cfg
        self.rules = rules
        self.ad = ad
        self.xm = xm
        self.home = 0j
        self.ding = 0j

    def _fresh(self):
        sleep(1)
        self.ad.uiautomator()
        self.xm.load()

    def enter(self):
        '''进入，点击百灵、刷新、点击第一条视频'''
        self._fresh()
        self.home = self.xm.pos(self.cfg.get(self.rules, 'rule_bottom_work'))
        self.ding = self.xm.pos(self.cfg.get(self.rules, 'rule_bottom_ding'))
        try:
            self.ad.tap(self.ding)
        except Exception as e:
            raise AttributeError(f'没有找到 百灵 的点击坐标')
        self._fresh()
        video_column = self.cfg.get('common', 'video_column_name')
        pos_col = self.xm.pos(f'//node[@text="{video_column}"]/@bounds')
        try:
            self.ad.tap(pos_col)  # 点击{video_column}刷新
            # logger.debug(f'百灵 {video_column}：{pos_col}')
        except Exception as e:
            pass
            # logger.debug(f'百灵 {video_column} 不知道为什么找不到了 摊手')
            # logger.info(e)
        finally:
            self.ad.tap(self.ding)  # 再点一次百灵刷新
        sleep(3)
        self._fresh()
        first = self.xm.pos(self.cfg.get(self.rules, 'rule_first_video'))
        # logger.debug(f'第一个视频： {first}')
        self.ad.tap(first)

    def next(self):
        '''下一条，上划'''
        # logger.debug(f'下一条')
        self.ad.draw('up', 800)

    def exit(self):
        '''点击HOME'''
        self.ad.back()
        sleep(2)
        # self._fresh()        
        self.ad.tap(self.home)
        # logger.debug(f'点击HOME {self.home}')
        sleep(5)

    def run(self):
        '''运行脚本，count刷视频数，delay每个视频观看时间'''
        count = 15
        delay = 240
        self.enter()
        while count:
            with timerUtil.Timer() as t:
                count -= 1
                sleep(5)
                print('正在视听学习 第{}条，还剩{}条，{}秒后进入下一条...'.format(count + 1, count, delay))
                sleep(delay)
                self.next()

        self.exit()


if __name__ == "__main__":
    pass
