#!/usr/bin/env python3
# Author: Hong Jen Yee (PCMan) <pcman.tw@gmail.com>
#

import zipfile
import sys
from lxml import etree

def extractTextFromXml(xml):
    if xml:
        xml = etree.fromstring(xml)
        notags = etree.tostring(xml, encoding='utf8', method='text')
        return notags.decode("utf8", errors="ignore")
    return ""


def readOfficeXml(filename):
    content = ""
    try:
        f = zipfile.ZipFile(filename, "r")
        xml = None
        if filename.endswith(".docx"):
            xml = f.read("word/document.xml")
            content = extractTextFromXml(xml)
        elif filename.endswith(".pptx"):
            files = f.namelist()
            slides = []
            i = 1
            while True:
                slide_name = "ppt/slides/slide%d.xml" % (i)
                if slide_name not in files:
                    break
                xml = f.read(slide_name)
                slides.append(extractTextFromXml(xml))
                i += 1
            content = ''.join(slides)
        f.close()
    except:
        print ("Error reading:", filename, sys.exc_info())
    return content


def main():
    if len(sys.argv) < 2:
        return 1
    print(readOfficeXml(sys.argv[1]))

if __name__ == "__main__":
    main()
