#!/usr/bin/env python
# -*- coding:utf-8 -*-
from time import sleep

class UpQuiz(object):
    def __init__(self, dev):
        self.dev = dev        
        self.question = ''
        self.answer = ''    #Correct answer
        self.pos = ''
    
    def _entry(self):
        self.dev.click('mine_pos', True)        #Click Mine
        self.dev.click('question_pos', True)
        #获取争上游答题位置
        pos = 0j
        while pos == 0j:
            pos = self.dev.get_pos('up_pos', True)
        self.dev.swip(200, pos.imag, 200, pos.imag)                   #点击争上游答题
        self.dev.click('up_start_pos', True)    #点击开始比赛
        

    def _submit(self):
        self.question = ""
        count = 30
        while len(self.question) < 9 and count > 0:
            self.question = self.dev.decode('up_question_content', True)
            count -= 1
        if count==0:
            return False
        self.pos = self.dev.get_pos('up_options_pos', False)
        self.question = self.dev.getQuestion(self.question)
        #查询数据库
        self.answer = self.dev.search('单选题', self.question, False)
        cursor = ord(self.answer) - 65
        # 点击正确选项
        if cursor < len(self.pos):
            self.dev.tap_pos(self.pos[cursor])
            return True
        else:
            self.dev.recordlog('[Error] Click Pos Not In Options')
            return False
        
    def _reopened(self, repeat:bool=False)->bool:       # 本题答对否
        if self.dev.get_pos('up_again', True):
            return True
        else:
            return False

    def run(self, count):
        self._entry()
        while count > 0:
            if not self._submit():
                if not self._reopened():
                    return count
            if self._reopened(): # 判断本局是否已经结束
                self.dev.click('up_again', True)  #下一局
                self.dev.click('up_start_pos', True)    #点击开始比赛
                count -= 1
            else:
                continue
        return count
