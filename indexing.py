#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  iindexing.py
#  
#  Copyright 2015 PCMan <pcman.tw@gmail.com>
#

import sys
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
        self.doc_ids = set() # doc ID list of documents containing this term
        self.doc_freq = 0 # document frequency (for calculating IDF)

'''
Reader of *.srt files
'''
class SrtFileReader:
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        state = 0
        f = open(self.filename, "r")
        lines = []
        for line in f:
            if state == 0: # skip No. of subtitle
                state = 1
            elif state == 1: # skip time
                state = 2
            else: # subtitle
                line = line.strip()
                if line:
                    lines.append(line)
                else: # end of subtitle
                    state = 0
        f.close()
        return '\n'.join(lines)


'''
Document
'''
class Doc:
    def __init__(self, doc_id, filename, attachment = ''):
        self.doc_id = doc_id
        self.filename = filename
        self.attachment = attachment
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

    def setTermFreq(self, term_id, val):
        self.terms[term_id] = val

    def getTermFreq(self, term_id):
        if term_id in self.terms:
            return self.terms[term_id]
        return 0


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
        self.term_ids = dict() # string to term_id mapping
        self.terms = [] # list of IndexTerm objects
        self.docs = [] # list of Doc objects
        self.doc_ids = dict() # map document names to doc IDs
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
        self.term_ids = dict()
        self.terms = []
        try:
            '''
            Format of the "terms" file:
            each line contains:
            <term_string> <term_id> <collection_freq>
            '''
            f = open(self.dir_path + "/terms", "r")
            for line in f:
                vals = line.split()
                term = vals[0]
                term_id = int(vals[1])
                index_term = IndexTerm(term_id, term)
                index_term.freq = int(vals[2])
                self.term_ids[term] = term_id
                self.terms.append(index_term)
            f.close()
        except:
            print("terms cannot be loaded")
        self.new_term_id = len(self.terms)

    '''
    Load the documents and their indexes in the collection from disk
    '''
    def loadDocs(self):
        # load doc list
        doc_id = 0
        try:
            '''
            Format of the file-list: each line contains a file path
            the line nunmber is doc ID (zero-based)
            '''
            f = open(self.dir_path + "/file-list", "r")
            for line in f:
                filename = line.strip()
                if filename:
                    doc = Doc(doc_id, filename)
                    self.docs.append(doc)
                    self.doc_ids[filename] = doc_id # map filename to doc ID
                    doc_id += 1
            f.close()
        except:
            print("file-list cannot be loaded")
        self.new_doc_id = doc_id

        # load inverted file
        try:
            '''
            Format of the inverted-file:
            <term_id> <doc1>:<tf1> <doc2>:<tf2> <doc3>:<tf3> ....
            '''
            f = open(self.dir_path + "/inverted-file", "r")
            for line in f:
                line = line.strip()
                if line:
                    vals = line.split()
                    term_id = int(vals[0])
                    index_term = self.terms[term_id]
                    items = vals[1:]
                    index_term.doc_freq = len(items) # DF of the index term
                    for item in items:
                        cols = item.split(':')
                        doc_id = int(cols[0])
                        freq = int(cols[1])
                        index_term.doc_ids.add(doc_id)
                        # build document vector
                        doc = self.docs[doc_id]
                        doc.setTermFreq(term_id, freq)
            f.close()
        except:
            print("inverted-file cannot be loaded")


    '''
    Write all index terms and docs to files.
    '''
    def save(self):
        # write index terms
        f = open(self.dir_path + "/terms", "w")
        for index_term in self.terms:
            f.write("%s %d %d\n" % (index_term.term, index_term.term_id, index_term.freq))
        f.close()

        # write doc list
        f = open(self.dir_path + "/file-list", "w")
        for doc in self.docs:
            f.write("%s\n" % (doc.filename))
        f.close()

        # write inverted file
        f = open(self.dir_path + "/inverted-file", "w")
        for term in self.terms:
            f.write("%d" % (term.term_id))
            for doc_id in term.doc_ids:
                doc = self.docs[doc_id]
                f.write(" %d:%d" % (doc_id, doc.getTermFreq(term.term_id)))
            f.write("\n")
        f.close()


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
        if term in self.term_ids:
            term_id = self.term_ids[term]
            index_term = self.terms[term_id]
            index_term.freq += 1
        else:
            index_term = IndexTerm(self.new_term_id, term)
            self.new_term_id += 1
            index_term.freq = 1
            self.term_ids[term] = index_term.term_id
            self.terms.append(index_term)
        return index_term.term_id

    '''
    Add a new document to the collection
    '''
    def addDoc(self, filename, attachment = ''):
        # check for duplication
        if filename in self.doc_ids:
            return # the document is already in the collection
        new_id = self.new_doc_id
        doc = Doc(new_id, filename, attachment)
        self.docs.append(doc)
        self.new_doc_id += 1
        self.indexDoc(doc)

    '''
    Index the specified document
    @doc is a Doc object
    '''
    def indexDoc(self, doc):
        # FIXME:
        # need to improve the way of indexing so we can update DF of the index term
        # correctly after new documents are added.

        if doc.filename.endswith(".srt"): # *.srt subtitle file
            reader = SrtFileReader(doc.filename)
            content = reader.read()
        else: # ordinary text file
            f = open(doc.filename, "r")
            content = f.read()
            f.close()

        word = ''
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
                    doc.addTermId(term_id) # add the term to the vector of the doc
                    self.terms[term_id].doc_ids.add(doc.doc_id) # add the doc to the doc list of the term
                if next_state != STATE_SKIP:
                    word = ch
                else:
                    word = ''
            elif next_state != STATE_SKIP:
                if next_state == STATE_CHI: # the last char and current char are all Chinese
                    term_id = self.addTerm(word, isEnglish = False) # unigram
                    doc.addTermId(term_id)
                    self.terms[term_id].doc_ids.add(doc.doc_id) # add the doc to the doc list of the term

                    word = word + ch # make it a bigram
                    term_id = self.addTerm(word, isEnglish = False)
                    doc.addTermId(term_id)
                    self.terms[term_id].doc_ids.add(doc.doc_id) # add the doc to the doc list of the term

                    word = ch # make the next Chinese char unigram again
                else: # English word
                    word = word + ch
            state = next_state # update state

        if word:
            term_id = self.addTerm(word, isEnglish = True)
            doc.addTermId(term_id)
            self.terms[term_id].doc_ids.add(doc.doc_id) # add the doc to the doc list of the term


def main():
    if len(sys.argv) < 2:
        return 1
    collection = Collection(".")
    collection.addDoc(sys.argv[1])
    collection.save()

    return 0

if __name__ == '__main__':
    main()

