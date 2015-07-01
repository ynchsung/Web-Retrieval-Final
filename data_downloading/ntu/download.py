import sys
import urllib
import os
from HTMLParser import HTMLParser

lec_url_list = []
materials_url_list = []

def findName(url):
	cut_position = url.rfind("/")
	name = url[cut_position + 1:]
	return name


class lecHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		if(tag == 'div'):
			key, value = attrs[0]
			if (key == "class" and value == "AccordionPanelTab"):
				key, value = attrs[2]
				lec_url_list.append(value[15:len(value) - 3])

			

class vidHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		if(tag == 'a' and len(attrs) == 2):
			key, value = attrs[0]
			if (key == "href" and value[26:35] == "ocw_files"):
					materials_url_list.append(value)
					print value



lecLinkParser = lecHTMLParser()
f = urllib.urlopen(str(sys.argv[1]))
lec_html = f.read()
lecLinkParser.feed(lec_html)
lecLinkParser.close()


for lec_url in lec_url_list:
	response = urllib.urlopen(lec_url)
	html = response.read()
	videoParser = vidHTMLParser()
	videoParser.feed(html)
	videoParser.close()

j=1
for material_url in materials_url_list:
	#print "Downloading Lecture " , j
	urllib.urlretrieve(material_url, "lec_" + str(j) + material_url[material_url.find(".", 36):])
	j = j + 1
