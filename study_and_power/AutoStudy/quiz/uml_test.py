# -*- coding:utf-8 -*-

class xml_test(object):
    def __init__(self, xm):
        self.xm = xm  # xml file decode

    def _fresh(self):
        self.xm.load()

    def _find_text(self, rule):
        text = self.xm.content(rule)
        print(text)

    def _find_pos(self, rule):
        edits = self.xm.pos(rule)
        print(edits)

    def _find_options(self, rule):
        result = self.xm.options(rule)  # 获取答案内容
        print(result)

    def run(self):
        self._fresh()
        rule = '//node[@content-desc="1 /5" or @content-desc="2 /5" or @content-desc="3 /5" or @content-desc="4 /5" or @content-desc="5 /5"]/following-sibling::node[1]/node/@content-desc'
        self._find_text(rule)


if __name__ == "__main__":
    import xmler

    path = Path('C:/Users/何伟/AppData/Local/Temp/ui.xml')
    xm = xmler.Xmler(path)
    cg = xml_test('mumu', ad, xm)
    cg.run()
