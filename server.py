#!/usr/bin/env python3
import os
import sys
import time
import json
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

# FIXME: avoid using global variable here.
collection = Collection(".")
ir_rfmodel = IRTraining()

def add_new_file(nfile_path):
    text_path = '' # the text file
    collection.addDoc(text_path, nfile_path)
    collection.updateIdf()

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        bu = deepcopy(bar_urls)
        self.render("home.html", bar_urls=bu)

class ViewHandler(tornado.web.RequestHandler):
    def get(self):
        bu = deepcopy(bar_urls)
        bu["View"]["active"] = True
        data = {
            'Information Retrival': [
                "./PJCheng/1.wav",
                "./PJCheng/2.wav",
                "./PJCheng/3.wav",
                "./PJCheng/4.wav",
                "./PJCheng/5.wav",
            ],
            'Machine Learning': [
                "./HTLin/1.wav",
                "./HTLin/2.wav",
                "./HTLin/3.wav",
                "./HTLin/4.wav",
            ],
        }
        success = False
        try:
            tmp = self.get_query_argument("success")
            success = True
        except:
            pass
        self.render("view.html", bar_urls=bu, data=data, success=success)

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
        ret_str = []
        for x in ret:
            ret_str.append(collection.docs[x].filename)
        if len(ret_str) < 50:
            self.render("result.html", bar_urls=bu, re=ret_str)
        else:
            self.render("result.html", bar_urls=bu, re=ret_str[0:50])

class MonitorHandler(tornado.web.RequestHandler):
    def post(self):
        event_type = self.get_argument("type")
        dat = self.request.body
        print(dat, file=sys.stderr)
        filenames = json.loads(dat)
        if event_type == "changed":
            for filename in filenames:
                # when a document is changed, we remove it and re-add it again
                collection.removeDocByName(filename)
                collection.addDoc(filename)
        elif event_type == "removed":
            for filename in filenames:
                collection.removeDocByName(filename)
        elif event_type == "added":
            for filename in filenames:
                collection.addDoc(filename)
        collection.updateIdf() # recalculate IDF since the collection is changed.


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
    # ir_rfmodel.training(sys.argv[1], sys.argv[2], sys.argv[3])
    ir_server = tornado.web.Application(handler, **settings)
    ir_server.listen(port)
    tornado.ioloop.IOLoop.current().start()
