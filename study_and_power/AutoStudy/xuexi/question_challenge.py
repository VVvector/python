#!/usr/bin/env python
# -*- coding:utf-8 -*-

from time import sleep

class ChallengeQuiz(object):
    def __init__(self, dev):
        self.dev = dev        
        self.question = ''  #题目内容
        self.result = ''    #选项内容
        self.correct = ''    #正确答案
        self.pos = ''       #选项位置
        self.tup = ['A','B','C','D','E','F']
    
    def _updateCorrect(self):
        cur = ord(self.correct) - 65
        next = (cur + 1)%len(self.pos)
        return self.tup[next]

    def _updateDB(self):
        self._show()
        
        self.correct = self._updateCorrect()
        
        print('[->Correct]' + self.correct)
        
        self.dev.update('Answer', self.result)
        self.dev.update('Correct',self.correct)
        
    def _show(self):
        print('\n[Question]' + self.question)
        for str in self.result:
            print("*" + str)
        print('[Correct]' + self.correct)
    
    def _entry(self):
        self.dev.click('mine_pos', True)
        self.dev.click('question_pos', True)
        self.dev.click('challenge_pos', True)

    def _submit(self):
        self.question = self.dev.decode('challenge_question', True)     #获取题目内容
        self.question = self.dev.getQuestion(self.question)
        self.pos = self.dev.get_pos('challenge_choice_pos', False)      #选项点击位置
        self.result = self.dev.decode_option('challenge_choice_content', False)
        #查询数据库
        self.correct = self.dev.search('单选题', self.question, True)
        cursor = ord(self.correct) - 65
        # 点击正确选项
        if cursor < len(self.pos):
            self.dev.tap_pos(self.pos[cursor])
        else:
             self.dev.recordlog('[Error] Click Pos Not In Options')

    def _reopened(self, repeat:bool=False)->bool:       # 本题答对否
        if not self.dev.get_pos('challenge_judge', True):
            return True
        else:
            return False

    def run(self, score):
        self._entry()
        count = 0
        while True:
            self._submit()
            sleep(1)             # 等待结果
            if self._reopened(): # 回答正确
                count +=  1
            else:
                self._updateDB()
                score -= (count//5)*6
                if score < 0:
                    return True
                count = 0
                self.dev.click('challenge_end', True)       #点击结束本局
                self.dev.click('challenge_again', True)     #点击再来一局
