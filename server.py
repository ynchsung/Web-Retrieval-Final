#!/usr/bin/env python3
import os
import sys
import time
import json
import random
from copy import deepcopy
import tornado.ioloop
import tornado.web
from config import *
from indexing import *
from ir_training import *

bar_urls = {
    "View": {"active": False, "url": "/view"},
    "Search": {"active": False, "url": "/search"},
}

collection = Collection(".")
ir_rfmodel = IRTraining()

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        bu = deepcopy(bar_urls)
        self.render("home.html", bar_urls=bu)

class ViewHandler(tornado.web.RequestHandler):
    def get(self):
        bu = deepcopy(bar_urls)
        bu["View"]["active"] = True
        data = {}
        docset = collection.doc_ids_without_url
        for doc_id in docset:
            doc_obj = collection.docs[doc_id]
            label_name = doc_obj.category
            if not label_name in data:
                data[label_name] = []
            data[label_name].append((doc_obj.filename, []))
            idx = len(data[label_name]) - 1

            cnt = 0
            get_doc = [d_id for d_id in collection.categories[label_name]]
            get_set = set()
            while cnt < 10:
                r_idx = random.randint(0, len(get_doc) - 1)
                d_id = get_doc[r_idx]
                if not collection.docs[d_id].associated_url in get_set and \
                                    collection.docs[d_id].associated_url != "":
                    data[label_name][idx][1].append(collection.docs[d_id].associated_url)
                    get_set.add(collection.docs[d_id].associated_url)
                    cnt += 1

            del get_doc
            del get_set
        self.render("view.html", bar_urls=bu, data=data)

class AddHandler(tornado.web.RequestHandler):
    def get(self):
        bu = deepcopy(bar_urls)
        bu["Add"]["active"] = True
        retry = False
        try:
            tmp = self.get_query_argument("retry")
            retry = True
        except:
            pass
        self.render("add.html", bar_urls=bu, retry=retry)

    def post(self):
        path = self.get_argument("path")
        add_new_file(path)
        self.redirect("/view?success")

class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        bu = deepcopy(bar_urls)
        bu["Search"]["active"] = True
        self.render("search.html", bar_urls=bu)

    def post(self):
        bu = deepcopy(bar_urls)
        bu["Search"]["active"] = True
        query_word = self.get_argument("query")
        ret = collection.query(query_word)
        ret_file = []
        ret_course = []

        for x in ret:
            if collection.docs[x].associated_url == "":
                ret_file.append(collection.docs[x].filename)

        idx = 0
        course_set = set()
        while idx < len(ret) and len(ret_course) < 50:
            file_id = ret[idx]
            if collection.docs[file_id].associated_url != "" and \
                    not collection.docs[file_id].associated_url in course_set:
                ret_course.append(collection.docs[file_id].associated_url)
                course_set.add(collection.docs[file_id].associated_url)
            idx += 1

        self.render("result.html", bar_urls=bu, ret_file=ret_file, ret_course=ret_course)

class MonitorHandler(tornado.web.RequestHandler):
    def post(self):
        event_type = self.get_argument("type")
        dat = self.request.body
        print(dat, file=sys.stderr)
        filenames = json.loads(dat.decode("utf-8"))
        if event_type == "changed":
            print("changed", file=sys.stderr)
            for filename in filenames:
                # when a document is changed, we remove it and re-add it again
                collection.removeDocByName(filename)
                file_id = collection.addDoc(filename)
                if file_id == -1:
                    continue
                doc_obj = collection.docs[file_id]
                new_label = ir_rfmodel.predict(doc_obj.terms)
                collection.setDocCategory(file_id, new_label)
        elif event_type == "removed":
            print("removed", file=sys.stderr)
            for filename in filenames:
                collection.removeDocByName(filename)
        elif event_type == "added":
            print("added", file=sys.stderr)
            for filename in filenames:
                file_id = collection.addDoc(filename)
                if file_id == -1:
                    continue
                doc_obj = collection.docs[file_id]
                new_label = ir_rfmodel.predict(doc_obj.terms)
                collection.setDocCategory(file_id, new_label)
        collection.updateIdf() # recalculate IDF since the collection is changed.
        collection.save()
        print("done", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: ./server.py [file_list_file] [inverted_file] [vocabulary_file]", file=sys.stderr)
        sys.exit(1)

    handler = [
        (r"/", HomeHandler),
        (r"/view", ViewHandler),
        (r"/add", AddHandler),
        (r"/search", SearchHandler),
        (r"/monitor", MonitorHandler),
    ]
    script_path = os.path.realpath(os.path.dirname(__file__))
    settings = {
        'static_path': os.path.join(script_path, 'static'),
        'template_path': os.path.join(script_path, 'template'),
    }
    ir_rfmodel.training(sys.argv[1], sys.argv[2], sys.argv[3])
    ir_server = tornado.web.Application(handler, **settings)
    ir_server.listen(port)
    tornado.ioloop.IOLoop.current().start()
