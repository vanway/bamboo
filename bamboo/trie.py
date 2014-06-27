#-*- coding:utf-8 -*-
"""
    trie
    __author__ = 'wang_wei@ctrip.com'
    __copyright__ = 'ctrip.com'
"""
import time
import math
import utils

class Trie(object):
    def __init__(self, dict_path, is_cache=False):
        self.trie = {'is_end':False, 'childs':{}, 'value':{}}
        self.total_freq = 0.0 # total words frequency
        self.word_value = {} # dict of word to frequency, probability(log(word frequency/total frequency)), tag
        self.min_prob = 0.0 # the min probability
        self.insert_file(dict_path)

    def __add_word_prob(self):
        for k,v in self.word_value.iteritems():
            prob = math.log(float(v['frequency'])/self.total_freq)
            self.word_value[k]['probability'] = prob
            if self.min_prob > prob:
                self.min_prob = prob

    def insert_file(self, dict_path):
        print('loading dict: {}'.format(dict_path))
        start = time.time()
        with open(dict_path, 'rb') as lines:
            for idx,line in enumerate(lines):
                self.__insert_line(line)
        self.__add_word_prob()
        print('loading over, has cost: {}s'.format(time.time()-start))

    @utils.trans_unicode
    @utils.filter_useless_char(utils.RE_NORMAL_HAN_DICT)
    def __insert_line(self, line):
        line_sp = line.split("|")
        if len(line_sp) != 3:
            print('line:%s, wrong format!' % line)
            return
        word, freq, tag = line_sp
        freq = float(freq)
        value = dict([('frequency', freq), ('tag', tag)])
        self.__insert_word(word, '')
        self.word_value[word] = value
        self.total_freq += freq

    def __insert_word(self, word, value):
        ptr = self.trie
        for char in word:
            if char not in ptr['childs']:
                ptr['childs'][char] = {'is_end':False, 'childs':{}, 'value':{}}
            ptr = ptr['childs'][char]
        ptr['is_end'] = True
        ptr['value'] = value

    def get(self, word):
        ptr = self.trie
        for char in word:
            if char in ptr['childs']:
                ptr = ptr['childs'][char]
            else:
                return None
        if ptr['is_end']:
            return ptr['value']
        else:
            return None

    def get_all_cut_possible(self, sentence):
        '''
        get all cut paths for input sentence

        '''
        sentence_len = len(sentence)
        ptr = self.trie
        all_cut_possible = {}
        for i in range(sentence_len):
            for j, char in enumerate(sentence[i:]):
                if char in ptr['childs']:
                    ptr = ptr['childs'][char]
                    if ptr['is_end']:
                        if i not in all_cut_possible: all_cut_possible[i]=[]
                        all_cut_possible[i].append(i+j)
                else:
                    break
            ptr = self.trie
            if i not in all_cut_possible: all_cut_possible[i] =[i]
        return all_cut_possible

    @utils.trans_unicode
    @utils.filter_useless_char(utils.RE_NORMAL_HAN)
    def get_max_prob_route(self, sentence):
        route = {}
        all_cut_possible = self.get_all_cut_possible(sentence)
        len_sentence = len(sentence)
        route[len_sentence] = (1.0, '')
        for idx in xrange(len_sentence-1, -1, -1):
            candidates = [(self.word_value.get(sentence[idx:pos+1], {}).get('probability', self.min_prob) \
                           + route[pos+1][0], pos) \
                           for pos in all_cut_possible[idx]]
            route[idx] = max(candidates)
        cut_route = []
        idx = 0
        while idx <= len_sentence-1:
            cut_route.append(idx)
            idx = route[idx][1] + 1 # the next cut pos
        cut_route.append(idx)
        return cut_route

if __name__ == '__main__':
    test = Trie('base.dict')
    t1 = time.time()
    c = test.get_max_prob_route(u'上海去北京的机票')
    print time.time() - t1
    print c
