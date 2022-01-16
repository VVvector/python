# -*- coding:utf-8 -*-
import re
from lxml import etree
import logging
import shutil
from . import util

logger = util.get_logger(__name__)


class Xmler(object):
    def __init__(self, path=None):
        self.path = path
        self.root = None
        logger.debug(self.path)

    def load(self):
        self.root = etree.parse(str(self.path))

    def str2complex(self, s):
        x0, y0, x1, y1 = [int(x) for x in re.findall(r'\d+', s)]
        res = complex((x0 + x1) // 2, (y0 + y1) // 2)
        return res

    def texts(self, rule: str) -> list:
        res = [x.replace(u'\xa0', u' ') for x in self.root.xpath(rule)]
        res = [' ' if '' == x else x for x in res]
        return res

    def get_position(self, rule: str) -> list:
        res = self.texts(rule)
        logger.debug(res)
        points = [self.str2complex(x) for x in res]
        if len(points) == 1:
            res = points[0]
        else:
            res = points
        return res

    def get_content(self, rule: str) -> str:
        res = ''.join(self.texts(rule))
        return res

    def get_options(self, rule: str) -> list:
        res = [re.sub(r'\|', '_', x) for x in self.root.xpath(rule)]
        return res

    def get_count(self, rule: str) -> int:
        res = self.root.xpath(rule)
        return len(res)

    def save_page_xml(self, file_name):
        shutil.copyfile("C:/Users/vec/AppData/Local/Temp/ui.xml", "D:/xpath/{}.xml".format(file_name))


if __name__ == "__main__":
    from argparse import ArgumentParser
    from pathlib import Path

    logging.basicConfig(format='%(asctime)s - [%(filename)s:%(lineno)d] - %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG)

    parse = ArgumentParser()
    parse.add_argument(dest='filename', metavar='filename', nargs="?", type=str,
                       default='C:/Users/vec/AppData/Local/Temp/ui.xml', help='目标文件路径')
    args = parse.parse_args()

    path = Path(args.filename)
    xm = Xmler(path)
    xm.load()

    logger.debug(path)
    rules = []
    rule = '//node[@content-desc="1/3" or @text="1/3"]/parent::node/following-sibling::node[1]/node/@bounds'
    rules.append(rule)

    for rule in rules:
        logger.debug(rule)
        pos = xm.get_position(rule)
        logger.debug(pos)

    # 获取第一个选择题的选项
    rules = []
    rule = '//node[@content-desc="1/3" or @text="1/3"]/parent::node/following-sibling::node[1]/node/@text'
    rules.append(rule)

    rule = '//node/@text'
    rules.append(rule)

    for rule in rules:
        logger.debug(rule)
        text = xm.get_content(rule)
        logger.debug(text)
        text_list = text.split(' ')
        logger.debug(text)
        if "学习" in text_list and "共享" in text_list and "业务" in text_list and "我的" in text_list:
            logger.debug("在主页中")
