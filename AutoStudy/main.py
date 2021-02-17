# -*- coding:utf-8 -*-
from argparse import ArgumentParser
import configparser
from pathlib import Path
import os
from app import App

def main():
    parse = ArgumentParser()
    parse.add_argument('-l', '--log', metavar='log', nargs='?', const=True, type=bool, default=False, help='Log记录')
    parse.add_argument('-s', '--question', metavar='question', nargs='?', const=True, type=bool, default=False, help='题目输出')
    parse.add_argument('-d', '--database', metavar='db', nargs='?', const=True, type=bool, default=False, help='存储数据库')
    args = parse.parse_args()

    # 读取配置文件
    path = Path(__file__).parent
    print(path)
    cfg_path = os.path.join(path, 'config.ini')
    cfg = configparser.ConfigParser()
    cfg.read(cfg_path, encoding='utf-8')

    if any([args.log, args.question, args.database]):
        print(f'\n\t日志记录{("[×]", "[√]")[args.log]}\t题目输出{("[×]", "[√]")[args.question]}\t题目保存{("[×]", "[√]")[args.database]}\n')
        app = App(cfg, args.log, args.question, args.database)
        app.start()
    else:
        pass

if __name__ == "__main__":
    main()