#!/usr/bin/env python

import sys
import urllib
import os
from HTMLParser import HTMLParser

base_url = 'http://ocw.mit.edu'
lec_url_list = []
video_url_list = []
course_name_list = []
course_url_list = []

def findName(url):
	cut_position = url.rfind("/")
	name = url[cut_position + 1:]
	return name


class lecHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		if(tag == 'a'):
			key, value = attrs[0]
			if (key == "class" and value == "coursepic"):

		elif(tag == 'img'):
			key, value = attrs[1]
			print value


lecLinkParser = lecHTMLParser()
f = urllib.urlopen(str(sys.argv[1]))
lec_html = f.read()
lecLinkParser.feed(lec_html)
lecLinkParser.close()


