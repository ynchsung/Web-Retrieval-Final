#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  iindexing.py
#  
#  Copyright 2015 PCMan <pcman.tw@gmail.com>
#

import sys
import codecs
import string
from nltk.stem.porter import *

STATE_SKIP = 1 # skip
STATE_CHI = 2 # Chinese
STATE_ENG = 3 # English

class Indexer:

    def __init__(self, filename):
        self.filename = filename
        self.terms = dict()
        self.stemmer = PorterStemmer()

    def addTerm(self, term, isEnglish = True):
        if isEnglish:
            term = self.stemmer.stem(term.lower())
        if term in self.terms:
            self.terms[term] += 1
        else:
            self.terms[term] = 1

    def createIndex(self):
        f = codecs.open(self.filename, "r", "utf-8")
        content = f.read()
        f.close()

        word = u''
        state = STATE_SKIP
        for ch in content:
            next_state = None
            u = ord(ch) # get the unicode value of the character
            if ch in string.whitespace: # skip white space
                next_state = STATE_SKIP
            elif ch in string.punctuation: # skip English punctuations
                next_state = STATE_SKIP
            elif u >= 0x3000 and u <= 0x303f: # skip Chinese punctuations (http://www.unicode.org/reports/tr38/)
                next_state = STATE_SKIP
            # http://www.utf8-chartable.de/unicode-utf8-table.pl?start=65280&number=256
            # handle full width punctuations
            elif (u >= 0xff00 and u <= 0xff20) or (u >= 0xff3b and u <= 0xff40) or (u >= 0xff5b and u <= 0xff65):
                next_state = STATE_SKIP
            else: # other printable chars (Chinese or English)
                if u <= 128: # ch is an English char (FIXME: this is inaccurate)
                    next_state = STATE_ENG
                else: # non-English chars are all treated as Chinese
                    next_state = STATE_CHI

            if next_state != state: # state transition
                if word:
                    self.addTerm(word, isEnglish = True)
                if next_state != STATE_SKIP:
                    word = ch
                else:
                    word = u''
            elif next_state != STATE_SKIP:
                if next_state == STATE_CHI: # the last char and current char are all Chinese
                    self.addTerm(word, isEnglish = False) # unigram
                    word = word + ch # make it a bigram
                    self.addTerm(word, isEnglish = False)
                    word = ch # make the next Chinese char unigram again
                else: # English word
                    word = word + ch
            state = next_state # update state

        if word:
            self.addTerm(word, isEnglish = True)

        for term in self.terms:
            print term, self.terms[term]


def main():
    if len(sys.argv) < 2:
        return 1
    indexer = Indexer(sys.argv[1])
    indexer.createIndex()

    return 0

if __name__ == '__main__':
    main()

