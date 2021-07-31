# -*- coding:utf-8 -*-
from m1.m1_1 import t_1_1
from m2 import t_2

def api():
    print("i'm {} api".format(__name__))
    t_1_1.api()
    t_2.api()
