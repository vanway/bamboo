#-*- coding:utf-8 -*-
"""
    __author__ = 'wang_wei@ctrip.com'
    __copyright__ = 'ctrip.com'
"""
import re

"""
re_han, re_skip = re.compile(ur"([\u4E00-\u9FA5a-zA-Z0-9+#|]+)"), re.compile(ur"[^\r\n]")
re_eng,re_num = re.compile(ur"[a-zA-Z+#]+"), re.compile(ur"[0-9]+")
"""

RE_NORMAL_HAN = re.compile(ur"([\u4E00-\u9FA5a-zA-Z0-9+#]+)")
RE_NORMAL_HAN_DICT = re.compile(ur"([\u4E00-\u9FA5a-zA-Z0-9+#|]+)")
RE_NUNMBER_ENG = re.compile(ur"([a-zA-Z0-9+#]+)")

def filter_useless_char(re_compile):
    def _filter_useless_char(func):
        def __filter_useless_char(self, sentence):
            sentence = ''.join(re_compile.findall(sentence))
            return func(self, sentence)
        return __filter_useless_char
    return _filter_useless_char

def trans_unicode(func):
    def __trans_unicode(self, sentence):
        if not isinstance(sentence,  unicode):
            try:
                sentence = sentence.decode('utf-8')
            except:
                sentence = sentence.decode('gbk','ignore')
        sentence.strip()
        return func(self, sentence)
    return __trans_unicode

def get_blocks(sentence, re_compile):
    return re_compile.findall(sentence)

def get_splits(sentence, re_compile):
    return re_compile.split(sentence)

def is_number_or_eng(sentence):
    return RE_NUNMBER_ENG.match(sentence)


if __name__ == "__main__":
    class A(object):
        def __init__(self):
            self.abc = "abc"
            pass
        @filter_useless_char(RE_NORMAL_HAN_DICT)
        def test(self, line):
            print line
            print self.abc
    a = A()
    print ' '.join(get_splits(u'的33345星', RE_NUNMBER_ENG))
