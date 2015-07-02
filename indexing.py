#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  indexing.py
#  
#  Copyright 2015 PCMan <pcman.tw@gmail.com>
#

import os
import sys
import string
import math
import subprocess
from nltk.stem.porter import *
# import cProfile
import reader

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
Document
'''
class Doc:
    def __init__(self, doc_id, filename, associated_url = ""):
        self.doc_id = doc_id
        self.filename = filename
        self.associated_url = associated_url
        self.category = ""
        self.terms = dict() # term vector of the document (key: term_id, value: term_freq)


'''
The document collection of the search engine
'''
class Collection:

    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.term_ids = {} # string to term_id mapping
        self.terms = [] # list of IndexTerm objects
        self.docs = [] # list of Doc objects
        self.doc_ids = {} # map document names to doc IDs
        self.doc_ids_without_url = set() # ID of documents without associated URLs
        self.categories = {} # string cate: set(doc_id1,doc_id2...)
        self.new_doc_id = 0
        self.deleted_doc_ids = set() # set of doc_ids recycled from deleted files.
        self.new_term_id = 0
        self.stemmer = PorterStemmer()

        # load from disk
        self.loadTerms()
        self.loadDocs()
        self.updateIdf()

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
            f = open(self.dir_path + "/terms", "r", errors="ignore")
            for line in f:
                vals = line.split(" ")
                term = vals[0]
                term_id = int(vals[1])
                index_term = IndexTerm(term_id, term)
                index_term.freq = int(vals[2])
                self.term_ids[term] = term_id
                self.terms.append(index_term)
            f.close()
        except:
            print("terms cannot be loaded", sys.exc_info())
        self.new_term_id = len(self.terms)

    '''
    Load the documents and their indexes in the collection from disk
    '''
    def loadDocs(self):
        # load doc list
        doc_id = 0
        try:
            '''
            Format of the file-list: each line contains:
            <file_path>\t<associated_url>\t<category>
            the line nunmber is doc ID (zero-based)
            <associated_url> and <category> are optional and can be empty
            If the filename is "?", that means, the document is already 
            deleted and we should set it to None.
            '''
            f = open(self.dir_path + "/file-list", "r", errors="ignore")
            for line in f:
                line = line.strip()
                if line:
                    doc = None
                    category = ""
                    if line != "?": # the file is deleted if its name is "?"
                        parts = line.rsplit("\t", maxsplit = 2) # split filename and associated URL
                        filename = parts[0]
                        associated_url = ""
                        if len(parts) > 1:
                            associated_url = parts[1]
                            if not associated_url: # if the document has no associated URL
                                self.doc_ids_without_url.add(doc_id)
                            if len(parts) > 2:
                                category = parts[2]
                        doc = Doc(doc_id, filename, associated_url)
                        self.doc_ids[filename] = doc_id # map filename to doc ID
                    else:
                        self.deleted_doc_ids.add(doc_id) # this doc ID is not in used and can be reused later.
                    self.docs.append(doc)
                    if category: # add the document to the category dict
                        self.setDocCategory(doc_id, category)
                    doc_id += 1
            f.close()
        except:
            print("file-list cannot be loaded", sys.exc_info())
        self.new_doc_id = doc_id

        # load inverted file
        try:
            '''
            Format of the inverted-file:
            <term_id> <num_docs> <doc1>:<tf1> <doc2>:<tf2> <doc3>:<tf3> ....
            '''
            f = open(self.dir_path + "/inverted-file", "r", errors="ignore")
            for line in f:
                line = line.strip()
                if line:
                    vals = line.split(" ")
                    term_id = int(vals[0])
                    index_term = self.terms[term_id]
                    items = vals[2:]
                    index_term.doc_freq = len(items) # DF of the index term
                    for item in items:
                        cols = item.split(':')
                        doc_id = int(cols[0])
                        freq = int(cols[1])
                        index_term.doc_ids.add(doc_id)
                        # build document vector
                        doc = self.docs[doc_id]
                        doc.terms[term_id] = freq # set term frequency in the doc vector
            f.close()
        except:
            print("inverted-file cannot be loaded", sys.exc_info())


    '''
    Update the inverted document frequency (IDF) values for each index term
    after the number of documents in the collection is changed.
    '''
    def updateIdf(self):
        n_docs = len(self.docs) - len(self.deleted_doc_ids) # since self.docs contains deleted files, we should not count them.
        for index_term in self.terms:
            if index_term.doc_freq == 0:
                index_term.idf = 0.0
            else:
                index_term.idf = math.log10(n_docs / index_term.doc_freq)

    '''
    Write all index terms and docs to files.
    '''
    def save(self):
        # write index terms
        f = open(self.dir_path + "/terms", "w", errors="ignore")
        for index_term in self.terms:
            f.write("%s %d %d\n" % (index_term.term, index_term.term_id, index_term.freq))
        f.close()

        # write doc list
        f = open(self.dir_path + "/file-list", "w", errors="ignore")
        for doc in self.docs:
            if doc:
                f.write("%s\t%s\t%s\n" % (doc.filename, doc.associated_url, doc.category))
            else:
                f.write("?\n") # the doc is already deleted, write "?" for its filename
        f.close()

        # write inverted file
        f = open(self.dir_path + "/inverted-file", "w", errors="ignore")
        for term in self.terms:
            f.write("%d %d" % (term.term_id, len(term.doc_ids)))
            for doc_id in term.doc_ids:
                doc = self.docs[doc_id]
                f.write(" %d:%d" % (doc_id, doc.terms[term.term_id]))
            f.write("\n")
        f.close()


    '''
    Add a new document to the collection
    After calling addDoc(), call updateIdf() to re-calculate IDF for terms.
    @associated_url is an URL associated with the file, such as the original download URL
    or the URL of the course website.
    @category is the category or label of the file.
    Both @associated_url and @category are optional and can be empty.
    Returns the doc_id of the newly added document.
    '''
    def addDoc(self, filename, associated_url = "", category = ""):
        # check for duplication
        if not os.path.exists(filename):
            return -1
        if filename in self.doc_ids:
            return self.doc_ids[filename] # the document is already in the collection
        if self.deleted_doc_ids: # see if we can reuse the doc ID of a deleted file.
            new_id = self.deleted_doc_ids.pop()
        else:
            new_id = self.new_doc_id # generated a new doc ID
            self.new_doc_id += 1
        doc = Doc(new_id, filename, associated_url)
        if new_id < len(self.docs):
            self.docs[new_id] = doc
        else:
            self.docs.append(doc)
        self.doc_ids[filename] = new_id
        if not associated_url:
            self.doc_ids_without_url.add(new_id)
        if category:
            self.setDocCategory(new_id, category)
        self.indexDoc(doc)
        return new_id


    '''
    Remove an existing document from the collection
    After calling removeDoc(), call updateIdf() to re-calculate IDF for terms.

    NOTE: simply removing the doc from the list will not work since
        we have to re-assign new doc_ids to all docs after the doc_id and
        this is very expensive. There needs to be a better way to do it.
        So we allow some "holes" containing empty docs in the Doc object
        list (self.docs).
        1. Here we set the deleted entries to "None" rather than really
          removing the items from the lists so we can keep the other doc ids
          unchanged. However, to reclaim the wasted space, some garbage collection
          mechanisms are needed in the future.
        2. the doc_ids of the deleted files are collected in self.deleted_doc_ids
          sets so the IDs can be reused for newly added documents later.
        3. The real number of all documents in the collection is hence
          len(self.docs) - len(self.deleted_doc_ids)
    '''
    def removeDoc(self, doc_id):
        if doc_id >= len(self.docs):
            return # no such document in the collection
        doc = self.docs[doc_id]     # remove from the filename list
        del self.doc_ids[doc.filename]
        # update term frequencies
        for term_id in doc.terms:
            freq = doc.terms[term_id] # freq of the term in the doc

            index_term = self.terms[term_id] # get the IndexTerm object for the term
            index_term.doc_ids.remove(doc_id) # remove the doc from the term
            index_term.freq -= freq # frequency of the term in the collection
            index_term.doc_freq -= 1 # number of docs containing the term

        # remove the document from its category
        if doc.category:
            self.categories[doc.category].remove(doc.doc_id)

        self.docs[doc_id] = None # remove the doc object
        self.deleted_doc_ids.add(doc_id) # make the doc ID reusable
        if doc_id in self.doc_ids_without_url:
            self.doc_ids_without_url.remove(doc_id)


    '''
    Remove document by filename
    @doc_name is the file path of the document
    '''
    def removeDocByName(self, doc_name):
        if doc_name in self.doc_ids:
            doc_id = self.doc_ids[doc_name]
            self.removeDoc(doc_id)


    '''
    Set a new category for the doc.
    If @new_category is "", the doc is removed from its current category.
    '''
    def setDocCategory(self, doc_id, new_category = ""):
        if doc_id >= len(self.docs):
            return # no such doc
        doc = self.docs[doc_id]
        # if doc.category == new_category:
           # return
        # remove from old category

        if doc.category:
            self.categories[doc.category].remove(doc_id)

        # add the document to the category dict
        if new_category:
            if new_category not in self.categories:
                self.categories[new_category] = set()
        self.categories[new_category].add(doc_id)
        doc.category = new_category

    '''
    Segment text into a dict containing (term:frequency) pairs
    '''
    def tokenizeText(self, content):
        STATE_SKIP = 1
        STATE_ENG = 2 # Engligh
        STATE_CHI = 3 # Chinese

        terms = dict()

        word = ''
        state = STATE_SKIP
        for ch in content:
            next_state = None
            u = ord(ch) # get the unicode value of the character
            if ch in string.whitespace: # skip white space
                next_state = STATE_SKIP
            elif ch in string.punctuation: # skip English punctuations
                next_state = STATE_SKIP
            elif ch in string.digits: # skip digits
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
                    if state == STATE_ENG:
                        word = self.stemmer.stem(word.lower()) # stemming for English
                    terms[word] = terms.get(word, 0) + 1
                if next_state != STATE_SKIP:
                    word = ch
                else:
                    word = ''
            elif next_state != STATE_SKIP:
                if next_state == STATE_CHI: # the last char and current char are all Chinese
                    terms[word] = terms.get(word, 0) + 1 # unigram

                    word = word + ch # make it a bigram
                    terms[word] = terms.get(word, 0) + 1 # unigram

                    word = ch # make the next Chinese char unigram again
                else: # English word
                    word = word + ch
            state = next_state # update state

        if word:
            word = self.stemmer.stem(word.lower()) # stemming for English
            terms[word] = terms.get(word, 0) + 1 # unigram

        return terms


    '''
    Index the specified document
    @doc is a Doc object
    '''
    def indexDoc(self, doc):
        content = reader.extractTextFromFile(doc.filename)

        terms = self.tokenizeText(content)
        for term in terms:
            freq = terms[term]
            term_id = 0
            index_term = None
            if term in self.term_ids:
                term_id = self.term_ids[term]
                index_term = self.terms[term_id]
                index_term.freq += freq
            else:
                term_id = self.new_term_id
                index_term = IndexTerm(term_id, term)
                self.new_term_id += 1
                index_term.freq = freq
                self.term_ids[term] = index_term.term_id
                self.terms.append(index_term)

            doc.terms[term_id] = freq # set term frequency in the doc vector

            index_term.doc_ids.add(doc.doc_id) # add the doc to the doc list of the term
            index_term.doc_freq += 1 # update DF of the term


    '''
    Calculate the cosine similarity of two term vectors
    @vec1 and @vec2 are sparse vectors containing term frequencies
    represented with python dictionaries (term_id => freq).
    '''
    def similarity(self, vec1, vec2):
        # FIXME: calculating TF*IDF everytime is slow
        # we should cache the TF*IDF of every docs
        w1 = dict()
        norm1 = 0
        for term_id in vec1:
            v = vec1[term_id] * self.terms[term_id].idf
            w1[term_id] = v
            norm1 += v * v

        w2 = dict()
        norm2 = 0
        for term_id in vec2:
            v = vec2[term_id] * self.terms[term_id].idf
            w2[term_id] = v
            norm2 += v * v

        if norm1 == 0 or norm2 == 0:
            return 0.0

        dot = 0
        # cosine similarity of two vectors w1 and w2
        for term_id in (set(w1.keys()) & set(w2.keys())):
            dot += w1[term_id] * w2[term_id]
        return dot / math.sqrt(norm1 * norm2)


    '''
    Query for documents containing the @text
    Returns a list of doc_ids sorted by ranking
    '''
    def query(self, text):
        # convert query text to terms
        doc_ids = set()
        query_terms = dict()
        for term in self.tokenizeText(text):
            if term in self.term_ids: # only accept terms in the collection
                term_id = self.term_ids[term]
                query_terms[term_id] = query_terms.get(term_id, 0) + 1
                doc_ids = doc_ids.union(self.terms[term_id].doc_ids)

        # handle ranking sorted by similarity
        return sorted(doc_ids, key = lambda doc_id: self.similarity(self.docs[doc_id].terms, query_terms), reverse = True)



def main():
    collection = Collection(".")
    '''
    for filename in sys.argv[1:]:
        print("Indexing:", filename)
        collection.addDoc(filename)
    '''
    if len(sys.argv) < 2:
        return 1

    # read a file-list
    f = open(sys.argv[1], "r")
    for line in f:
        # format of each line:
        # <dir_path> <url> <category> <num> <file1> <file2> <file3>....
        line = line.strip()
        parts = line.split(" ")
        dir_path = parts[0]
        if dir_path[0] != '/': # not full path, prepend the dirname of the filelist
            dir_path = "%s/%s" % (os.path.dirname(sys.argv[1]), dir_path)
        url = parts[1]
        category = parts[2]
        n = int(parts[3])
        for i in range(4, n + 4):
            filename = "%s/%s" % (dir_path, parts[i])
            print("Indexing:", filename, file=sys.stderr)
            collection.addDoc(filename, url, category)
    f.close()

    # re-calculate IDF for all terms since the collection is changed
    collection.updateIdf()

    # write the changed index to disk
    collection.save()

    # Test query
    '''
    i = 1
    for doc_id in collection.query("programming"):
        print(i, doc_id, collection.docs[doc_id].filename)
        i += 1
    '''
    return 0

if __name__ == '__main__':
    # cProfile.run("main()")
    main()

