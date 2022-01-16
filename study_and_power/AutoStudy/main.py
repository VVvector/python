# -*- coding:utf-8 -*-
from common import device
from common import util

from xuexi import xuexiapp
from shihua import shihuaapp


def main():
    logger = util.get_logger(__name__)

    dev = device.Device()
    dev.fresh_page()
    # dev.save_page_xml("全部完成")

    # xuexi_app = xuexiapp.App(dev, db)
    # xuexi_app.artical_study()

    shihua_app = shihuaapp.App(dev)
    shihua_app.test_ui()

    logger.info("自动学习完成")


if __name__ == "__main__":
    main()
