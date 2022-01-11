# -*- coding:utf-8 -*-
import re
from lxml import etree
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.DEBUG)

def str2complex(s):
    x0, y0, x1, y1 = [int(x) for x in re.findall(r'\d+', s)]
    res = complex((x0 + x1) // 2, (y0 + y1) // 2)
    return res


class Xmler(object):
    def __init__(self, path=None):
        self.path = path
        self.root = None
        logger.debug(self.path)

    def load(self):
        #logger.debug("path: {}".format(self.path))
        self.root = etree.parse(str(self.path))

    def texts(self, rule: str) -> list:
        res = [x.replace(u'\xa0', u' ') for x in self.root.xpath(rule)]
        res = [' ' if '' == x else x for x in res]
        return res

    def pos(self, rule: str) -> list:
        res = self.texts(rule)
        logger.debug(res)
        points = [str2complex(x) for x in res]
        if len(points) == 0:
            logger.warning("can't find out the points!!!!")

        if len(points) == 1:
            res = points[0]
        else:
            res = points
        return res

    def content(self, rule: str) -> str:
        res = ''.join(self.texts(rule))
        return res

    def options(self, rule: str) -> list:
        res = [re.sub(r'\|', '_', x) for x in self.root.xpath(rule)]
        return res

    def count(self, rule: str) -> int:
        res = self.root.xpath(rule)
        return len(res)


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
    rule = '//node[@content-desc="收听“党建之声”"]/following-sibling::node[3]/node/@bounds'
    rules.append(rule)

    rule = '//node[@content-desc="阅读文章"]/following-sibling::node[3]/node/@bounds'
    rules.append(rule)

    rule = '//node[@content-desc="阅读专题栏目文章"]/following-sibling::node[3]/node/@bounds'
    rules.append(rule)

    rule = '//node[@content-desc="浏览所在企业门户"]/following-sibling::node[3]/node/@bounds'
    rules.append(rule)

    rule = '//node[@content-desc="通过平台链接浏览外部网站"]/following-sibling::node[3]/node/@bounds'
    rules.append(rule)

    rule = '//node[@content-desc="每日练习"]/following-sibling::node[3]/node/@bounds'
    rules.append(rule)

    #text = xm.content(rule)
    #logger.debug(text)

    rule = '//node[@content-desc="学习"]/@bounds'
    rules.append(rule)

    rule = '//node[@content-desc="共享"]/@bounds'
    rules.append(rule)

    rule = '//node[@content-desc="业务"]/@bounds'
    rules.append(rule)

    rule ='//node[@content-desc="我的"]/@bounds'
    rules.append(rule)

    rule = '//node[@text="确认"]/@bounds'
    rules.append(rule)

    rule = '//node[@text="门户矩阵"]/@bounds'
    rules.append(rule)

    rule = '//node[@text="浏览所在企业门户"]/following-sibling::node[3]/node/@bounds'
    rules.append(rule)

    rule = '//node[@content-desc="播放" or @text="播放"]/@bounds'
    rules.append(rule)

    rule = '//node[@content-desc="暂停" or @text="暂停"]/@bounds'
    rules.append(rule)

    rule = '//node[@text="第一学习"]/following-sibling::node[1]/node/@bounds'
    rules.append(rule)

    rule ='//node[@text="下拉刷新"]/following-sibling::node[1]/child::node()/node[1]/@bounds'
    rules.append(rule)

    for rule in rules:
        logger.debug(rule)
        pos = xm.pos(rule)
        logger.debug(pos)