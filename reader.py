#!/usr/bin/env python3
# Author: Hong Jen Yee (PCMan) <pcman.tw@gmail.com>
#

import zipfile
import sys
from lxml import etree

def readOfficeXml(filename, xmlname):
    try:
        f = zipfile.ZipFile(filename, "r")
        xml = f.read(xmlname)
        f.close()
        xml = etree.fromstring(xml)
        notags = etree.tostring(xml, encoding='utf8', method='text')
        return notags.decode("utf8", errors="ignore")
    except:
        print ("Error reading:", filename)
    return ""

def readDocxFile(filename):
    return readOfficeXml(filename, "word/document.xml")


def main():
    if len(sys.argv) < 2:
        return 1
    print(readDocxFile(sys.argv[1]))

if __name__ == "__main__":
    main()
