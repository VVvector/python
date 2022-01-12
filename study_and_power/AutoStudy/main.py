# -*- coding:utf-8 -*-
import logging


from common import device
from common import dbUtil
from xuexi import xuexiapp
from shihua import shihuaapp


def main():
    logging.basicConfig(format='%(asctime)s - [%(filename)s:%(lineno)d] - %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG)

    db = dbUtil.DB()
    dev = device.Device()
    dev.fresh_page()

    #xuexi_app = xuexiapp.App(dev, db)
    #xuexi_app.artical_study()

    shihua_app = shihuaapp.App(dev, db)
    shihua_app.test_ui()

if __name__ == "__main__":
    main()
