# -*- coding:utf-8 -*-
from m1 import t_1
from m1.m1_1 import t_1_1
from m2 import *
from m3 import t_3
import t1


def t_api():
    print("i'm {} api".format(__name__))


if __name__ == "__main__":
    t_api()
    t1.api()
    t_1.api()
    t_1_1.api()
    t_2.api()
    t_3.api()





