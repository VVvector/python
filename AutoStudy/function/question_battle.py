#!/usr/bin/env python
# -*- coding:utf-8 -*-

class BattleQuiz(object):
    def __init__(self, dev):
        self.dev = dev        
        self.question = ''
        self.answer = ''    #Correct answer
        self.pos = ''
    
    def _entry(self):
        self.dev.click('mine_pos', True)        #点击我的
        self.dev.click('question_pos', True)    #点击我要答题
        self.dev.click('battle_pos', True)      #点击双人对战
        self.dev.click('battle_start_pos', True)#点击随机匹配
        

    def _submit(self):
        self.pos = 0j
        while self.pos == 0j:
            self.pos = self.dev.get_pos('battle_options_pos', True)    #选项点击位置
        self.question = self.dev.decode('battle_question_content', True)     #获取题目内容
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
        if not self.dev.get_pos('battle_end_pos', True):
            return True
        else:
            return False

    def run(self):
        self._entry()
        while True:
            if not self._submit():
                return True
            if self._reopened(): # 判断本局是否已经结束
                continue
            else:
                self.dev.back()  #已经结束了
                return True
