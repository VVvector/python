# -*- coding:utf-8 -*-
import re
from time import sleep


class DailyQuiz(object):
    def __init__(self, cfg, rules, ad, xm, conn, cur):
        self.cfg = cfg
        self.rules = rules
        self.ad = ad  # Android development
        self.xm = xm  # xml file decode
        # connect MySQL
        self.conn = conn
        self.cur = cur
        # parameter
        self.question = ''  # question content
        self.result = ''  # result content
        self.correct = ''  # answer for this question
        self.options = ''  # pos of answer
        self.type = ''  # question type ['单选题','多选题','填空题']
        self.isInDB = True  # if Question not in DB, Then add to DB
        self.count_blank = 0
        self.p_submit = 0j  # submit botton
        self.p_next = 0j  # next botton
        self.rightCount = 0

    def _fresh(self):
        # 刷新xml布局
        self.ad.uiautomator()
        self.xm.load()
        sleep(2)

    def _enter(self):
        self._fresh()
        pos = self.xm.pos(self.cfg.get(self.rules, 'rule_daily_entry'))
        self.ad.tap(pos)

    def _getQuestion(self, str):
        str = str.split('（出题单位')
        str = str[0]
        str = str.split('(出题单位')
        str = str[0]
        str = str.split('（ 出题单位')
        str = str[0]
        str = str.split('(来源')
        str = str[0]
        str = str.split('（来源')
        str = str[0]
        str = str.split('来源：')
        str = str[0]
        return str

    def _search(self):
        sql = 'select Correct from autostudy where Question like %s and Type=%s LIMIT 1'
        self.findStr = self.question.replace(' ', '%')
        if self.cur.execute(sql, (self.findStr.replace('"', '%'), self.type)):
            self.isInDB = True
            self.correct = self.cur.fetchone()
            self.correct = self.correct[0]  # 仅返回正确答案
        else:
            self.isInDB = False
            # 先将题目和随机答案添加进数据库
            if self.type == '单选题':
                self.correct = 'A'
            elif self.type == '多选题':
                self.correct = 'AB'
            else:
                self.correct = '不忘初心牢记使命 不忘初心牢记使命 不忘初心牢记使命 不忘初心牢记使命'
        print("正确答案 - {}".format(self.correct))

    def _updateDB(self):
        if self.isInDB:
            pass
        else:
            sql = 'insert into autostudy (Type,Question,Correct) value (%s,%s,%s)'
            try:
                self.cur.execute(sql, (self.type, self.question, self.correct))
            except:
                print("数据库插入失败!")
                return
            else:
                pass
        if self.type == '单选题' or self.type == '多选题':
            for i in range(len(self.result)):
                if i == 0:
                    sqli = 'update autostudy set AnswerA = %s where Question like %s'
                elif i == 1:
                    sqli = 'update autostudy set AnswerB = %s where Question like %s'
                elif i == 2:
                    sqli = 'update autostudy set AnswerC = %s where Question like %s'
                elif i == 3:
                    sqli = 'update autostudy set AnswerD = %s where Question like %s'
                elif i == 4:
                    sqli = 'update autostudy set AnswerE = %s where Question like %s'
                else:
                    break
                print("* {}".format(self.result[i]))
                self.cur.execute(sqli, (self.result[i], self.question.replace('"', '%')))
        self.conn.commit()

    # 填空题处理
    def _print_question(self):
        print("{} - {}".format(self.type, self.question))
        print("correct answers - {}".format(self.correct))

    def _blank(self):
        # 查找题目描述
        self.question = self.xm.content(self.cfg.get(self.rules, 'rule_blank_content'))
        self.question = self._getQuestion(self.question)
        print("question: {}".format(self.question))

        # 查找对应的填空位置
        edits = self.xm.pos(self.cfg.get(self.rules, 'rule_edits'))
        print("edits: {}".format(edits))
        if isinstance(edits, list):
            self.count_blank = len(edits)
        else:
            self.count_blank = 1
            edits = [edits]

        # 在数据库中搜索答案
        self._search()

        # 拆分答案
        answers = self.correct.split(' ')
        for edit, self.correct in zip(edits, answers):
            print("input answers: {}".format(self.correct))
            self.ad.tap(edit)
            sleep(1)
            self.ad.input(self.correct)
            sleep(1)

    # 选择题处理
    def _check(self):
        self.question = self.xm.content(self.cfg.get(self.rules, 'rule_content'))
        self.question = self._getQuestion(self.question)
        print("question: {}".format(self.question))
        self.options = self.xm.pos(self.cfg.get(self.rules, 'rule_options'))
        self.result = self.xm.options(self.cfg.get(self.rules, 'rule_options_content'))  # 获取答案内容
        print("answers - {}".format(self.result))
        self._search()
        for c in self.correct:
            self.ad.tap(self.options[ord(c) - 65])

    def _submit(self):
        if self.p_submit == 0j:
            self._fresh()
            self.p_submit = self.xm.pos(self.cfg.get(self.rules, 'rule_submit'))
            print("p_submit: {}".format(self.p_submit))

        self.ad.tap(self.p_submit)

    def _next(self):
        if self.p_next == 0j:
            self._fresh()
            self.p_next = self.xm.pos(self.cfg.get(self.rules, 'rule_next'))
        self.ad.tap(self.p_next)

    def _desc(self):
        self._fresh()
        res = self.xm.content(self.cfg.get(self.rules, 'rule_desc'))
        if '' == res:
            if self.isInDB:
                pass
            else:
                self._updateDB()
            self.rightCount = self.rightCount + 1
            return True
        else:
            self.correct = re.sub(r'正确答案：', '', res)
            self._updateDB()
            return False

    def _type(self):
        # 刷新xml布局文件
        self._fresh()
        # 返回题目类型
        return self.xm.content(self.cfg.get(self.rules, 'daily_type'))

    def _dispatch(self):
        self.type = self._type()
        if '填空题' == self.type:
            self._blank()
        elif '单选题' == self.type or '多选题' == self.type:
            self._check()
        else:
            print('未知题目类型')

        # 点击确定
        self._submit()

        # 提交答案后，获取答案解析，若为空，则回答正确，否则，返回正确答案
        if self._desc():  # 返回结果为正确无需处理
            pass
        else:
            self._submit()  # 点击下一题或者完成
        self._print_question()

    def run(self):
        score = 0
        # 开始答题
        self._enter()
        # 每次回答5题，每日答题6组
        while True:
            self.rightCount = 0
            for j in range(5):
                sleep(2)
                self._dispatch()
            sleep(5)

            if self.rightCount == 5:
                score += 2

            elif self.rightCount > 1:
                score += 1

            print("当前得分：%s" % score)

            if score < 6:
                self._next()  # 点击再来一组
            else:
                break

        self.ad.back()  # 返回到我要答题界面
        return True


if __name__ == "__main__":
    pass
