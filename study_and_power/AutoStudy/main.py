# -*- coding:utf-8 -*-
import argparse
import pymysql
from pathlib import Path
from configparser import ConfigParser

from common import adbUtil, timerUtil, xmlUtil
from media import viewer, reader


class App(object):
    def __init__(self, config_file_path):
        cfg = ConfigParser()
        cfg.read(config_file_path, encoding='utf-8')
        self.cfg = cfg
        self.dev_section = self.cfg.get('common', 'device')
        self.xml_uri = Path(self.cfg.get(self.dev_section, 'xml_uri'))

        # connect Android by ADB
        self.adb = adbUtil.ADB(
            self.xml_uri,
            self.cfg.getboolean(self.dev_section, 'is_virtual_machine'),
            self.cfg.get(self.dev_section, 'host'),
            self.cfg.getint(self.dev_section, 'port'))

        self.xm = xmlUtil.Xmler(self.xml_uri)

        # connect MySQL
        cfg_section = 'common'
        db_host = self.cfg.get(cfg_section, 'db_host')
        db_port = self.cfg.getint(cfg_section, 'db_port')
        db_user = self.cfg.get(cfg_section, 'db_user')
        db_passwd = self.cfg.get(cfg_section, 'db_pwd')
        db_name = self.cfg.get(cfg_section, 'db_name')

        print("{} {} {} {}".format(db_host, db_port, db_user, db_passwd))

        self.conn = pymysql.connect(host=db_host, port=db_port, database=db_name, user=db_user, passwd=db_passwd)
        self.cur = self.conn.cursor()

    def _art_run(self):
        rd = reader.Reader(self.cfg, self.dev_section, self.adb, self.xm)
        rd.run()

    def _vdo_run(self):
        vd = viewer.Viewer(self.cfg, self.dev_section, self.adb, self.xm)
        vd.run()

    def _quiz_run(self, day, chg):
        qApp = Quiz(self.cfg, self.dev_section, self.adb, self.xm, self.conn, self.cur)
        qApp.start(day, chg)

    def start(self, art, vdo, day, chg):
        if art:
            print('正在浏览文章……')
            with timerUtil.Timer() as t:
                self._art_run()
            print(f'文章完成【{round(t.elapsed, 2)}】')

        if vdo:
            print('正在浏览视频……')
            with timerUtil.Timer() as t:
                self._vdo_run()
            print(f'视听完成【{round(t.elapsed, 2)}】')

        if day or chg:
            print('正在答题……')
            with timerUtil.Timer() as t:
                self._quiz_run(day, chg)
            print(f'答题完成【{round(t.elapsed, 2)} 】')

    def __del__(self):
        self.adb.close()


def main():
    parser = argparse.ArgumentParser(description="-----------show app arg-----------")
    parser.add_argument('-a', '--article', metavar='article', nargs='?', const=True, type=bool, default=False,
                        help='阅读文章')
    parser.add_argument('-c', '--challenge', metavar='challenge', nargs='?', const=True, type=bool, default=False,
                        help='挑战答题')
    parser.add_argument('-d', '--daily', metavar='daily', nargs='?', const=True, type=bool, default=False, help='每日答题')
    parser.add_argument('-v', '--video', metavar='video', nargs='?', const=True, type=bool, default=False, help='视听学习')

    args = parser.parse_args()
    if any([args.article, args.video, args.daily, args.challenge]):
        print(f'\n\t阅读文章{("[×]", "[√]")[args.article]}\t视听学习{("[×]", "[√]")[args.video]}\t'
              f'每日答题{("[×]", "[√]")[args.daily]}\t挑战答题{("[×]", "[√]")[args.challenge]}\n')

        # get configuration file information
        config_file_name = "config.ini"
        config_file_path = Path.cwd().joinpath(config_file_name)

        app = App(config_file_path)
        app.start(args.article, args.video, args.daily, args.challenge)
    else:
        pass


if __name__ == '__main__':
    main()
