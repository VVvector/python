# -*- coding:utf-8 -*-
import re

class DailyQuiz(object):
    def __init__(self, app):
        self.app = app
        # parameter
        self.question = ''  # question content
        self.result = ''    # result content
        self.correct = ''    # answer for this question
        self.options = ''   # pos of answer
        self.type = ''      # question type ['单选题','多选题','填空题']
        
        self.rightCount = 0 #统计本局答对题目数量
        
    def _show(self):
        print('[Question]' + self.question)
        if self.type == '填空题':
            pass
        else:    
            for str in self.result:
                print("* " + str)   
        print('[Correct]' + self.correct + '\n')
        
    def _entry(self):
        self.dev.click('mine_pos', True) #点击我的
        self.dev.click('question_pos', True)  #点击我要答题
        self.dev.click('daily_question_pos', True)# 点击开始答题
        
    def _updateDB(self):
        if self.type == '单选题' or self.type == '多选题':
            self.dev.update('Answer', self.result)
        self.dev.update('Correct',self.correct)
    
    #填空题处理     
    def _blank(self):
        self.question = self.dev.decode("daily_question_blank", False)  #获取题干
        self.question = self.dev.getQuestion(self.question)
        edits = self.dev.get_pos('daily_blank_pos', False)              #获取空格位置
        if isinstance(edits, list):
            count_blank = len(edits)
        else:
            count_blank = 1
            edits = [edits]
        self.correct = self.dev.search(self.type, self.question, True)
        answers = self.correct.split(' ')#拆分答案
        for edit, self.correct in zip(edits, answers):
            self.dev.input(edit, self.correct)

    #选择题处理
    def _check(self):
        self.question = self.dev.decode('daily_question_choice', False)
        self.question = self.dev.getQuestion(self.question)
        
        self.options = self.dev.get_pos('daily_choice_pos', False)
        self.result = self.dev.decode_option('daily_choice_content', False)#获取答案内容
        self.correct = self.dev.search(self.type, self.question, True)
        for c in self.correct:
            if (ord(c)-65) < len(self.options):
                self.dev.tap_pos(self.options[ord(c)-65])
            else:
                self.dev.recordlog('[Error] Click Pos Not In Options')

    def _desc(self):
        res = self.dev.decode('daily_question_desc', True)
        if '' == res:
            self.rightCount = self.rightCount+1                     #答对后正确数+1
        else:
            self.correct = re.sub(r'正确答案：', '', res)           #答错后获取正确答案
            self._updateDB()
            self.dev.click('daily_question_submit', True)          #答错后再次点击下一题
            return False   

    def _dispatch(self):
        self.type = self.dev.decode('daily_question_type', True)    #获取题目类型
        if '填空题' == self.type:
            self._blank()
        elif '单选题' == self.type or '多选题' == self.type:
            self._check()
        else:
            return False
        self.dev.click('daily_question_submit', True)              #点击确定
        self._desc()                                                #判断是否答对
        #self._show()                                                #输出题目内容到控制台
        return True
        
    def run(self, score):
        self._entry()
        while True:
            self.rightCount = 0
            for j in range(5):
                if not self._dispatch():
                    break
            if self.rightCount == 5:
                score-=2
            elif self.rightCount > 1:
                score-=1
                
            if score > 0:
                self.dev.click('daily_question_next', True)
            else:
                self.dev.homepage()
                break
        return score

if __name__ == "__main__":
    pass
