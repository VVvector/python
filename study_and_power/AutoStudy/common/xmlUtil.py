# -*- coding:utf-8 -*-
import re
from pathlib import Path
from lxml import etree


def str2complex(s):
    x0, y0, x1, y1 = [int(x) for x in re.findall(r'\d+', s)]
    res = complex((x0 + x1) // 2, (y0 + y1) // 2)
    return res


class Xmler(object):
    def __init__(self, path=Path('./temp/xml/reader.xml')):
        self.path = path
        self.root = None

    def load(self):
        self.root = etree.parse(str(self.path))

    def texts(self, rule: str) -> list:
        res = [x.replace(u'\xa0', u' ') for x in self.root.xpath(rule)]
        res = [' ' if '' == x else x for x in res]
        return res

    def pos(self, rule: str) -> list:
        res = self.texts(rule)
        points = [str2complex(x) for x in res]
        if len(points) == 0:
            print("can't find out the points!!!!")

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

    parse = ArgumentParser()
    parse.add_argument(dest='filename', metavar='filename', nargs="?", type=str,
                       default='C:/Users/vec/AppData/Local/Temp/ui.xml', help='目标文件路径')
    args = parse.parse_args()

    path = Path(args.filename)
    xm = Xmler(path)
    xm.load()

    rule = '//node[@content-desc="1 /5" or @content-desc="2 /5" or @content-desc="3 /5" or @content-desc="4 /5" or @content-desc="5 /5"]/following-sibling::node[1]/node/@content-desc'
    text = xm.content(rule)
    print(text)
