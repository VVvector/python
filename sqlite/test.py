import re
str_1='wo shi yi shi da da niu:::(11)(22)'
char_1='u'


def get_num_in_brackets(line_str, keyword):
    n_pos = line_str.find(keyword)
    if n_pos < 0:
        return False, 0

    str1 = line_str[n_pos:]
    num_str = re.findall(r'[(](.*?)[)]', str1)
    if num_str[0].isdigit() is not True:
        return False, 0

    num = int(num_str[0])
    print(num)


get_num_in_brackets(str_1, char_1)