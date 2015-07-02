#!/usr/bin/env python3
import os
import sys
import math
import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse import csr_matrix
from sklearn import ensemble

class IRTraining():
    def __init__(self):
        self.rf = ensemble.RandomForestClassifier()
        self.v_dict = {}        # vocabulary map: (string word, int vocab_id)
        self.v_list = []        # v_id -> string vocabulary
        self.v_idf = []

        self.file_dict = {}     # file map: (string file_name, file_id for file_list)
        self.file_list = []     # file_id -> (path, url, label)
        self.label_dict = {}    # label map: (string label_name to label_id)
        self.label_data = []    # label_id -> [file_id whose label is label_id]
        self.label_to_str = []  # label_id -> string label

    def training(self, flist_file, iv_file, v_file):
        labels = []
        row = []
        col = []
        data = []
        v_size = 0
        label_size = 0
        doc_size = 0

        with open(flist_file, "rt") as fp:
            for line in fp:
                spt = line.rstrip("\n").split("\t")
                assert(len(spt) == 3)
                # spt[0]: filename
                # spt[1]: course_url for this file
                # spt[2]: label of this file
                assert(not spt[0] in self.file_dict)
                self.file_list.append((spt[0], spt[1], spt[2]))
                self.file_dict[spt[0]] = doc_size

                if not spt[2] in self.label_dict:
                    self.label_dict[spt[2]] = label_size
                    self.label_to_str.append(spt[2])
                    self.label_data.append([])
                    now_label_id = label_size
                    label_size += 1
                else:
                    now_label_id = self.label_dict[spt[2]]

                labels.append(now_label_id)
                self.label_data[now_label_id].append(doc_size)
                doc_size += 1

        with open(v_file, "rt", encoding="utf-8") as fp:
            for line in fp:
                spt = line.rstrip("\n").split(" ")
                assert(len(spt) == 3 and not spt[0] in self.v_dict)
                self.v_dict[spt[0]] = v_size
                self.v_list.append(spt[0])
                self.v_idf.append(0.0)
                v_size += 1

        with open(iv_file, "rt") as fp:
            idx = 0
            for line in fp:
                spt = line.rstrip("\n").split(" ")
                assert(len(spt) >= 2 and int(spt[1]) + 2 == len(spt))
                if int(spt[1]) == 0:
                    idf = 0
                else:
                    idf = math.log(doc_size / float(spt[1]), 10)
                self.v_idf[int(spt[0])] = idf
                for i in range(int(spt[1])):
                    t = spt[i + 2]
                    sp = t.split(":")
                    assert(len(sp) == 2)
                    # tf-idf
                    row.append(int(sp[0]))
                    col.append(idx)
                    data.append(float(sp[1]) * idf)
                idx += 1

        # print(self.v_dict, end="\n\n")
        # print(self.v_list, end="\n\n")
        # print(self.file_dict, end="\n\n")
        # print(self.file_list, end="\n\n")
        # print(self.label_dict, end="\n\n")
        # print(self.label_data, end="\n\n")
        # print(self.label_to_str, end="\n\n")

        print("Finish reading file", file=sys.stderr)
        csc_mat = csc_matrix((data, (np.array(row), np.array(col))), \
                                                    shape=(doc_size, v_size))
        self.rf.fit(csc_mat, labels)
        print("Finish fitting into RandomForest", file=sys.stderr)

    def predict(self, vec_dict):
        v_size = len(self.v_list)
        doc_size = len(self.file_list)
        row = []
        col = []
        data = []
        for x, y in vec_dict.items():
            if x >= v_size:
                continue
            row.append(0)
            col.append(x)
            data.append(float(y) * self.v_idf[x])

        csr_mat = csr_matrix((data, (np.array(row), np.array(col))), \
                                                            shape=(1, v_size))
        return self.label_to_str[self.rf.predict(csr_mat)[0]]

if __name__ == "__main__":
    test = IRTraining()

    test.training("file-list", "inverted-file", "terms")
    # test.training("/tmp2/p03922004/file-list", "/tmp2/p03922004/inverted-file", \
    #                                            "/tmp2/p03922004/terms")
    a = {}
    a[2] = 3.0
    a[3] = 1.0
    a[11] = 2.0
    a[16] = 10.0
    print(test.predict(a))
