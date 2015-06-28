#!/usr/bin/env python3
import os
import sys
import time
from copy import deepcopy
import tornado.ioloop
import tornado.web
from config import *

bar_urls = {
    "View": {"active": False, "url": "/view"},
    "Add": {"active": False, "url": "/add"},
    "Search": {"active": False, "url": "/search"},
}

def add_new_record(path):
    pass

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
        # TODO:
        # add_new_record(path)
        # if success:
        self.redirect("/view?success")
        # else:
        # self.redirect("/add?retry")

class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        bu = deepcopy(bar_urls)
        bu["Search"]["active"] = True
        self.render("search.html", bar_urls=bu)

    def post(self):
        query_word = self.get_argument("query")
        # TODO:
        # query_record(query_word)
        self.write("POST: server get %s"%(query_word,))

if __name__ == "__main__":
    handler = [
        (r"/", HomeHandler),
        (r"/view", ViewHandler),
        (r"/add", AddHandler),
        (r"/search", SearchHandler),
    ]
    script_path = os.path.realpath(os.path.dirname(__file__))
    settings = {
        'static_path': os.path.join(script_path, 'static'),
        'template_path': os.path.join(script_path, 'template'),
    }
    ir_server = tornado.web.Application(handler, **settings)
    ir_server.listen(port)
    tornado.ioloop.IOLoop.current().start()
