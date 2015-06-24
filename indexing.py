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

'''
Information of an index term
'''
class IndexTerm:
    def __init__(self, term_id, term):
        self.term_id = term_id
        self.term = term
        self.freq = 0 # frequency of the term in the collection


'''
Document
'''
class Doc:
    def __init__(self, doc_id, filename):
        self.doc_id = doc_id
        self.filename = filename
        self.terms = dict() # term vector of the document

    '''
    Increase the frequency of a term in the document's term vector by 1.
    '''
    def addTermId(self, term_id):
        # FIXME: replace dict with a more efficient vector representation
        # May use numpy array here?
        if term_id in self.terms:
            self.terms[term_id] += 1
        else:
            self.terms[term_id] = 1

'''
State constants used by the document indexing code
'''
STATE_SKIP = 1 # skip
STATE_CHI = 2 # Chinese
STATE_ENG = 3 # English

'''
The document collection of the search engine
'''
class Collection:

    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.terms = dict()
        self.docs = []
        self.new_doc_id = 0
        self.new_term_id = 0
        self.stemmer = PorterStemmer()

        # load from disk
        self.loadTerms()
        self.loadDocs()

    '''
    Load the terms/vocabularies in the collection from disk
    '''
    def loadTerms(self):
        self.terms = dict()
        term_id = 0
        try:
            f = codecs.open(self.dir_path + "/terms", "r", "utf-8")
            for line in f:
                line = line.strip()
                self.terms[line] = term_id
                term_id += 1
            f.close()
        except:
            print "terms cannot be loaded"
        self.new_term_id = term_id

    '''
    Load the documents and their indexes in the collection from disk
    '''
    def loadDocs(self):
        # load doc list
        doc_id = 0
        try:
            f = codecs.open(self.dir_path + "/docs", "r", "utf-8")
            for line in f:
                doc = Doc(doc_id, line.strip())
                self.docs.append(doc)
                doc_id += 1
            f.close()
        except:
            print "docs cannot be loaded"
        self.new_doc_id = doc_id

        # load index and build document vectors
        term_id = 0
        try:
            f = open(self.dir_path + "/index", "r")
            for line in f:
                for doc_id in line.split():
                    doc_id = int(doc_id)
                    doc = self.docs[doc_id]
                    doc.addTermId(term_id)
                term_id += 1
            f.close()
        except:
            print "index cannot be loaded"

    '''
    Add a index term to the vocabularies and returns its term_id
    If the term already exists, its frequency is increased by 1.
    Otherwise, a new IndexTerm entry will be created for the term.
    If @isEnglish is True, the term will be converted to lower case and
    stemming will be performed.
    '''
    def addTerm(self, term, isEnglish = True):
        if isEnglish:
            term = self.stemmer.stem(term.lower())

        index_term = None
        if term in self.terms:
            index_term = self.terms[term]
            index_term.freq += 1
        else:
            index_term = IndexTerm(self.new_term_id, term)
            self.new_term_id += 1
            index_term.freq = 1
            self.terms[term] = index_term
        return index_term.term_id

    '''
    Add a new document to the collection
    '''
    def addDoc(self, filename):
        new_id = self.new_doc_id
        doc = Doc(new_id, filename)
        self.docs.append(doc)
        self.new_doc_id += 1
        self.indexDoc(doc)

    '''
    Index the specified document
    @doc is a Doc object
    '''
    def indexDoc(self, doc):
        f = codecs.open(doc.filename, "r", "utf-8")
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
                    term_id = self.addTerm(word, isEnglish = True)
                    doc.addTermId(term_id)
                if next_state != STATE_SKIP:
                    word = ch
                else:
                    word = u''
            elif next_state != STATE_SKIP:
                if next_state == STATE_CHI: # the last char and current char are all Chinese
                    term_id = self.addTerm(word, isEnglish = False) # unigram
                    doc.addTermId(term_id)
                    word = word + ch # make it a bigram
                    term_id = self.addTerm(word, isEnglish = False)
                    doc.addTermId(term_id)
                    word = ch # make the next Chinese char unigram again
                else: # English word
                    word = word + ch
            state = next_state # update state

        if word:
            term_id = self.addTerm(word, isEnglish = True)
            doc.addTermId(term_id)

        for term in sorted(self.terms):
            index_term = self.terms[term]
            print index_term.term_id, term, index_term.freq


def main():
    if len(sys.argv) < 2:
        return 1
    collection = Collection(".")
    collection.addDoc(sys.argv[1])

    return 0

if __name__ == '__main__':
    main()

