# -*- coding:utf-8 -*-
import os
import codecs
import os
import time

from crf import CRFPP

FILE_PATH = os.path.split(os.path.realpath(__file__))[0]

# load crf model
segTemplateFile = '%s/crf/template/template.seg' % FILE_PATH
posTemplateFile = '%s/crf/template/template.pos' % FILE_PATH
segModel = '%s/crf/model/model_seg' % FILE_PATH
posModel = '%s/crf/model/model_pos' % FILE_PATH


class SegPOS():
    def __init__(self):
        self._textEncoding = "utf-8"
        self._segModel = segModel
        self._posModel = posModel
        self._getTokenizer()
        self._getPOSSeg()

    def loadTrainFile(self, trainFile, tagNum):
        segTrainFile = '%s/crf/tmp.seg' % FILE_PATH
        posTrainFile = '%s/crf/tmp.pos' % FILE_PATH
        segModelFile = '%s/crf/model/crf_seg.model' % FILE_PATH
        posModelFile = '%s/crf/model/crf_pos.model' % FILE_PATH
        if trainFile:
            self._readTrainFile(trainFile, segTrainFile, posTrainFile, tagNum)
            os.system('crf_learn -f 3 -c 4.0 %s %s %s' % (segTemplateFile, segTrainFile, segModelFile))
            os.system('crf_learn -f 3 -c 4.0 %s %s %s' % (posTemplateFile, posTrainFile, posModelFile))
            self._setModel(segModelFile, posModelFile)

    def _setModel(self, segModel=None, posModel=None):
        self._segModel = segModel
        self._posModel = posModel

    def _getTokenizer(self):
        self._tokenizer = CRFPP.Tagger("-m %s -v 3 -n2" % self._segModel)

    def _getPOSSeg(self):
        self._posSeg = CRFPP.Tagger("-m %s -v 3 -n2" % self._posModel)

    def _readTrainFile(self, inputFile, outputSeg, outputPos, tagNum):
        outSeg = codecs.open(outputSeg, 'w', self._textEncoding)
        outPos = codecs.open(outputPos, 'w', self._textEncoding)
        with codecs.open(inputFile, 'r', self._textEncoding) as inFile:
            for line in inFile:
                ret = line.strip().split()
                if not ret:
                    continue
                for item in ret[1:]:
                    if not item:
                        continue
                    index1 = item.find(u'[')
                    if index1 >= 0:
                        item = item[index1+1:]
                        index2 = item.find(u']')
                    if index2 > 0:
                        item = item[:index2]
                    word, tag = item.split(u'/')
                    if tag == 'w' and word in [u'。', u'，']:
                        outSeg.write('\n')
                        outPos.write('\n')
                        continue
                    outPos.write('%s %s\n' % (word, tag))
                    if word:
                        if tagNum == 4:
                            self._write4Tag(word, outSeg)
                        elif tagNum == 6:
                            self._write6Tag(word, outSeg)
                outSeg.write('\n')
                outPos.write('\n')
        outSeg.close()
        outPos.close()

    def _write4Tag(self, word, handler):
        label = ['S', 'B', 'M', 'E']
        if len(word) == 1:
            handler.write('%s %s\n' % (word, label[0]))
        else:
            handler.write('%s %s\n' % (word[0], label[1]))
            for i in word[1:-1]:
                handler.write('%s %s\n' % (i, label[2]))
            handler.write('%s %s\n' % (word[-1], label[3]))

    def _write6Tag(self, word, handler):
        label = ['S', 'B', 'B2', 'B3', 'M', 'E']
        if len(word) == 1:
            handler.write('%s %s\n' % (word, label[0]))
        elif len(word) == 2:
            handler.write('%s %s\n' % (word[0], label[1]))
            handler.write('%s %s\n' % (word[1], label[5]))
        elif len(word) == 3:
            handler.write('%s %s\n' % (word[0], label[1]))
            handler.write('%s %s\n' % (word[1], label[2]))
            handler.write('%s %s\n' % (word[-1], label[5]))
        elif len(word) == 4:
            handler.write('%s %s\n' % (word[0], label[1]))
            handler.write('%s %s\n' % (word[1], label[2]))
            handler.write('%s %s\n' % (word[2], label[3]))
            handler.write('%s %s\n' % (word[-1], label[5]))
        elif len(word) >= 5:
            handler.write('%s %s\n' % (word[0], label[1]))
            handler.write('%s %s\n' % (word[1], label[2]))
            handler.write('%s %s\n' % (word[2], label[3]))
            for i in word[3:-1]:
                handler.write('%s %s\n' % (i, label[4]))
            handler.write('%s %s\n' % (word[-1], label[5]))

    def _processSegTag(self, message, retTag):
        wordList = []
        newWord = ''
        for idx, item in enumerate(message):
            if retTag[idx] == 'S':
                wordList.append(item)
            elif retTag[idx] == 'E':
                newWord += item
                wordList.append(newWord)
                newWord = ''
            else:
                newWord += item
        return wordList

    def crfToken(self, message):
        self._getTokenizer()
        resultTag = []
        try:
            self._tokenizer.clear()
            for i in message:
                i = i.encode('utf-8')
                self._tokenizer.add(i)
            self._tokenizer.parse()
            size = self._tokenizer.size()
            for i in range(0, size):
                resultTag.append(self._tokenizer.y2(i))
            wordList = self._processSegTag(message, resultTag)
            return wordList
        except:
            return []

    def crfPos(self, wordList):
        self._getPOSSeg()
        resultPos = []
        try:
            self._posSeg.clear()
            for i in wordList:
                i = i.encode('utf-8')
                self._posSeg.add(i)
            self._posSeg.parse()
            size = self._posSeg.size()
            for i in range(0, size):
                resultPos.append(self._posSeg.y2(i))
            return resultPos
        except:
            return []

crf_tag = SegPOS()

if __name__ == '__main__':
   segPosObj = SegPOS()
   #segPosObj.loadTrainFile("people-daily.txt", 4)
   t1 = time.time()
   sentence = u'第2344张车票'
   word_list = segPosObj.crfToken(sentence)
   pos_list = segPosObj.crfPos(word_list)
   print time.time() - t1
   print ' '.join(word_list)
   print ' '.join(pos_list)
