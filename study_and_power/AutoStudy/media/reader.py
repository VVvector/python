# -*- coding:utf-8 -*-
import pymysql
import datetime
from time import sleep
from common import timerUtil


class Reader:
    '''设计思路：
        0. 前提，APP位于首页
        1. 点击Home，找到订阅栏，要求用户有订阅公号，建议取关各大学习平台，因为学习平台喜欢上传本地新闻联播视频
        2. 点击订阅栏，刷新
        3. 保存第一个Item坐标
        4. 依次学习后续可点击Item（第二个开始），将最后一个Item拉至第一个Item处
        5. 在第一轮阅读中插入收藏、分享、评论操作
        6. 重复步骤4直到完成指定篇数新闻阅读
        7. 退出文章学习（其实不用退出，本来就在Home页
    '''

    def __init__(self, cfg, rules, ad, xm):
        self.cfg = cfg
        self.rules = rules
        self.ad = ad
        self.xm = xm
        # connect MySQL
        cfg_section = 'common'
        db_host = self.cfg.get(cfg_section, 'db_host')
        db_port = self.cfg.getint(cfg_section, 'db_port')
        db_user = self.cfg.get(cfg_section, 'db_user')
        db_passwd = self.cfg.get(cfg_section, 'db_pwd')
        db_name = self.cfg.get(cfg_section, 'db_name')
        self.conn = pymysql.connect(host=db_host, port=db_port, database=db_name, user=db_user, passwd=db_passwd)
        self.cur = self.conn.cursor()

        # parameter
        self.sqliSearch = 'select Title from article where Title like %s'
        self.sqliInsert = 'insert into article (Title,Date) value (%s,%s)'

        # Today
        self.date = datetime.datetime.now().strftime('%Y-%m-%d')

        # Botton
        self.home = 0j
        self.feeds = 0j
        self.fixed_top = 0j
        self.fixed_bottom = 0j

    def _fresh(self):
        sleep(1)
        self.ad.uiautomator()
        self.xm.load()

    def enter(self):
        # 进入‘订阅’，要求用户首先订阅公号
        self._fresh()
        self.home = self.xm.pos(self.cfg.get(self.rules, 'rule_bottom_work'))
        self.ad.tap(self.home)

        # 找到“订阅”栏
        while 0j == self.feeds:
            columns = [(t, p) for t, p in zip(self.xm.texts(self.cfg.get(self.rules, 'rule_columns_content')),
                                              self.xm.pos(self.cfg.get(self.rules, 'rule_columns_bounds')))]
            p0, p1 = columns[0][1], columns[-1][1]
            for col in columns:
                if self.cfg.get('common', 'article_column_name') == col[0]:
                    self.feeds = col[1]
                    break
            else:
                self.ad.slide(p1, p0, duration=1000)
                self._fresh()
        else:
            self.ad.tap(self.feeds)
            sleep(3)  # 等3秒刷新

    def _read_news(self, count, delay):
        # 上划次数
        slide_times = 4
        per_delay = delay // slide_times
        print('上划{}次，每次{}秒'.format(slide_times, per_delay))

        # 等待文章渲染
        sleep(3)
        for i in range(slide_times):
            sleep(per_delay)
            self.ad.draw('up', distance=300)

    def _star_share_comment(self, title):
        self._fresh()
        pos_comment = self.xm.pos(self.cfg.get(self.rules, 'rule_comment_bounds'))
        if pos_comment:
            pos_star = self.xm.pos(self.cfg.get(self.rules, 'rule_star_bounds'))
            pos_share = self.xm.pos(self.cfg.get(self.rules, 'rule_share_bounds'))
            # 分享
            self.ad.tap(pos_share)
            sleep(1)
            self.ad.uiautomator(filesize=6000)
            self.xm.load()
            pos_share2xuexi = self.xm.pos(self.cfg.get(self.rules, 'rule_share2xuexi_bounds'))
            self.ad.tap(pos_share2xuexi)
            sleep(1)
            self.ad.back()
            sleep(1)
            # 收藏
            self.ad.tap(pos_star)
            sleep(1)
            return 1
        else:
            print('该文章关闭评论！')
            return 0

    def run(self):
        # 阅读文章数量
        count = 10
        # 每篇文章阅读时间
        delay = 80
        # 分享文章数量
        ssc = 2
        self.enter()
        self.fixed_top = self.xm.pos(self.cfg.get(self.rules, 'rule_fixed_top_bounds'))
        if not self.fixed_top:
            print('没有获取到任何新闻，请确认是否订阅任何一个公众号！')

        while count > 0:
            self._fresh()
            pos_bottom = self.xm.pos(self.cfg.get(self.rules, 'rule_fixed_bottom_bounds'))
            if pos_bottom.imag > self.fixed_bottom.imag:
                self.fixed_bottom = pos_bottom

            # logger.debug(f'固定坐标点 TOP: {self.fixed_top}\tBOTTOM: {self.fixed_bottom}')
            poslist = self.xm.pos(self.cfg.get(self.rules, "rule_news_bounds"))
            if isinstance(poslist, complex):
                poslist = [poslist]

            articles = [(t, p) for t, p in zip(self.xm.texts(self.cfg.get(self.rules, "rule_news_content")), poslist)]
            for title, pos in articles:
                if self.cur.execute(self.sqliSearch, (title.replace('"', '%'))):
                    continue  # 该文章已经读过

                with timer.Timer() as t:
                    count -= 1
                    self.ad.tap(pos)
                    sleep(1)
                    self._read_news(count, delay)
                    if ssc > 0:
                        ssc -= self._star_share_comment(title)
                    # 时间到了，不读了
                    self.ad.back()
                    sleep(1)

                # 将文章添加到数据库
                self.cur.execute(self.sqliInsert, (title, self.date))
                if 0 == count:
                    self.conn.commit()
                    break
            else:
                self.ad.slide(self.fixed_bottom, self.fixed_top, duration=1000)
                sleep(3)
        sleep(5)


if __name__ == '__main__':
    pass
