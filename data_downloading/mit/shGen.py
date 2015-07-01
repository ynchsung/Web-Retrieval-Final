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
			if (key == "rel" and value == "coursePreview"):
					key, value = attrs[1]
					course_url_list.append(base_url + value + "/video-lectures/")
					course_name_list.append(value[9:value.find("/", 9)] + "_" + value[value.find("/", 9) + 1:])



#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)

lecLinkParser = lecHTMLParser()
f = urllib.urlopen(str(sys.argv[1]))
lec_html = f.read()
lecLinkParser.feed(lec_html)
lecLinkParser.close()

i=0
for duplicate in course_name_list:
	i = i + 1
	if(i%3 == 1):
		print "mkdir " + course_name_list[i]
		print 'cp download.py ./'  + course_name_list[i]
		print 'cd ./'  + course_name_list[i]
		print "python download.py " + course_url_list[i]
		print "rm -f ./download.py"
		print "cd .."

