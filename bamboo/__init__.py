#-*- coding:utf-8 -*-
"""
    WordSegment
    ~~~~~~~~~~~~~~~~~~~~

    This module implements the sample chinese words segements.

    WordSegementBase just cut sample chinese string into wordslist,
    WordSegementWithTag inherit WordSegementBase, it not only cut sample chinese
        string into wordslist, and get words' part of speech.

    __author__ = 'wang_wei@ctrip.com'
    __copyright__ = 'ctrip.com'

"""
import time
import math
import os,sys

FILE_PATH = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(FILE_PATH)

import utils
import tag
from trie import Trie

DEFAULT_ENCODEING = sys.getfilesystemencoding()

class SegmentPair(object):
    def __init__(self, word_list, tag_list):
        self.word_list = word_list
        self.tag_list = tag_list

    def __str__(self):
        pair_list = [u'{0}/{1}'.format(word, self.tag_list[idx]) for idx,word in enumerate(self.word_list)]
        return ' '.join(pair_list).encode(DEFAULT_ENCODEING)


class WordSegment(object):
    def __init__(self, dict_path):
        '''
           dict_path is the user words dict's path, trie is datastruct to store words of dict,
           trie provide get the max prob cut route of the sentence
        '''
        self.trie_model = Trie(dict_path)

    def get_continuos_singe(self, word_list):
        result = []
        start_flag = False
        count_single = 0
        start_idx = 0
        for idx, word in enumerate(word_list):
            if len(word) == 1 and not start_flag:
                start_flag = True
                start_idx = idx
                count_single += 1
            elif len(word) == 1 and start_flag:
                count_single += 1
            elif len(word) != 1 and start_flag:
                if count_single >= 2: result.append((start_idx, start_idx+count_single))
                start_flag = False
                count_single = 0
            else:
                pass
        return result

    @utils.trans_unicode
    def cut_base_on_dict(self, sentence):
        word_list, tag_list = [], []
        blocks = utils.get_blocks(sentence, utils.RE_NORMAL_HAN)
        for block in blocks:
            max_prob_route = self.trie_model.get_max_prob_route(block)
            max_prob_word_list = [block[max_prob_route[idx]: max_prob_route[idx+1]] \
                                  for idx in range(len(max_prob_route)-1)]
            continuos_singe_list = self.get_continuos_singe(max_prob_word_list)
            last_end = 0
            for start, end in continuos_singe_list:
                for pre_word in max_prob_word_list[last_end: start]:
                    word_list.append(pre_word)
                    tag_list.append(self.trie_model.word_value.get(pre_word, {}).get('tag', 'x'))
                last_end = end
                continuos_singe_str = ''.join(max_prob_word_list[start: end])
                for slices in utils.get_splits(continuos_singe_str, utils.RE_NUNMBER_ENG):
                    #print slices
                    if utils.is_number_or_eng(slices):
                        word_list.append(slices)
                        number_tag = 'm'
                        tag_list.append(number_tag)
                    else:
                        mid_word_list = tag.crf_tag.crfToken(slices)
                        mid_tag_list = tag.crf_tag.crfPos(mid_word_list)
                        word_list.extend(mid_word_list)
                        tag_list.extend(mid_tag_list)
            for word in max_prob_word_list[last_end: ]:
                word_list.append(word)
                tag_list.append(self.trie_model.word_value.get(pre_word, {}).get('tag', 'x'))

        #tag_list = [self.trie_model.word_value.get(word, {}).get('tag', 'x') \
                    #for word in word_list]
        return SegmentPair(word_list, tag_list)

    @utils.trans_unicode
    def cut_base_on_crf(self, sentence):
        word_list, tag_list = [], []
        blocks = utils.get_chinese_block(sentence)
        for block in blocks:
            word_list.extend(tag.crf_tag.crfToken(block))
        tag_list = tag.crf_tag.crfPos(word_list)
        return SegmentPair(word_list, tag_list)

    @utils.trans_unicode
    def cut_for_search(self,sentence):
        word_list = []
        tag_list = []
        all_cut_possible = self.trie_model.get_all_cut_possible()
        for idx, cut_possible_pos in all_cut_possible.iteritems():
            word_list.extend([sentence[idx: pos+1] for pos in cut_possible_pos])
        tag_list = [self.trie_model.word_value.get(word, {}).get('tag', 'x') \
                    for word in word_list]
        return SegmentPair(word_list, tag_list)

    def load_user_dict(self, dict_path):
        self.trie_model.insert_file(dict_path)

    def load_user_crf_corpus(self, corpus_path):
        pass

if __name__ == '__main__':
    a = WordSegment('{}/dict/base.dict'.format(FILE_PATH))
    start = time.time()
    mess = '帮我预订下人民广场附近的33345星级酒店，后天入住3天哈哈哈哈哈'
    result = a.cut_base_on_dict(mess)
    print 'spend time: %s' % (time.time()-start)
    print result
