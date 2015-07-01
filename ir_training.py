#!/usr/bin/env python3
import os
import sys
import math
import numpy as np
from scipy.sparse import csc_matrix
from sklearn import ensemble

class IRTraining():
    def __init__(self):
        self.rf = ensemble.RandomForestClassifier()
        self.label_inv = []

    def training(self, label_file, flist_file, iv_file, v_file):
        v_dict = {}             # vocabulary map: (string word, int vocab_id)
        file_list = []          # file array: idx(file_id) -> string file_name
        label_dict = {}         # label map: (string word, int label_id)
        label_table = {}        # label map: (string dir_name, string word)
        labels = []             # label list: idx(file_id) -> string word
        self.label_inv[:] = []  # label inv_list: idx(label_id) -> string word

        row = []
        col = []
        data = []
        v_size = 0
        label_size = 0
        doc_size = 0

        with open(label_file, "rt") as fp:
            for line in fp:
                spt = line.rstrip().split(" ")
                assert(len(spt) == 2)
                if not spt[1] in label_dict:
                    label_dict[spt[1]] = label_size
                    self.label_inv.append(spt[1])
                    label_size += 1
                label_table[spt[0]] = label_dict[spt[1]]

        with open(flist_file, "rt") as fp:
            for line in fp:
                spt = line.rstrip("\n").split("/")
                assert(len(spt) >= 2)
                assert(spt[1] in label_table)
                labels.append(label_table[spt[1]])
                doc_size += 1

        with open(v_file, "rt") as fp:
            for line in fp:
                spt = line.rstrip("\n").split(" ")
                assert(len(spt) == 3 and not spt[0] in v_dict)
                v_dict[spt[0]] = v_size
                v_size += 1

        with open(iv_file, "rt") as fp:
            idx = 0
            for line in fp:
                spt = line.rstrip("\n").split(" ")
                assert(len(spt) >= 2 and int(spt[1]) + 2 == len(spt))
                idf = math.log(doc_size / float(spt[1]), 10)
                for i in range(int(spt[1])):
                    t = spt[i + 2]
                    sp = t.split(":")
                    assert(len(sp) == 2)
                    # tf-idf
                    row.append(int(sp[0]))
                    col.append(idx)
                    data.append(float(sp[1]) * idf)
                idx += 1

        print("Finish reading inverted file", file=sys.stderr)
        csc_mat = csc_matrix((data, (np.array(row), np.array(col))), \
                                                    shape=(doc_size, v_size))
        self.rf.fit(csc_mat, labels)
        print("Finish fitting into RandomForest", file=sys.stderr)

    def predict(self, vec):
        return self.label_inv[self.rf.predict(vec)[0]]

if __name__ == "__main__":
    test = IRTraining()

    test.training("/tmp2/b02902083/file.label", "/tmp2/p03922004/file-list", \
                    "/tmp2/p03922004/inverted-file", "/tmp2/p03922004/terms")
