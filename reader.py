#!/usr/bin/env python3
# Author: Hong Jen Yee (PCMan) <pcman.tw@gmail.com>
#

import zipfile
import sys
import subprocess
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


'''
Read *.srt files
'''
def readSrtFile(filename):
    state = 0
    f = open(filename, "r", errors="ignore")
    lines = []
    for line in f:
        if state == 0: # skip No. of subtitle
            state = 1
        elif state == 1: # skip time
            state = 2
        else: # subtitle
            line = line.strip()
            if line:
                lines.append(line)
            else: # end of subtitle
                state = 0
    f.close()
    return '\n'.join(lines)


'''
Read *.doc files
This requires "catdoc" command
'''
def readDocFile(filename):
    try:
        return subprocess.check_output(["catdoc", "-dutf-8", filename]).decode(encoding="utf-8", errors="ignore")
    except:
        print("error reading doc file", filename)
    return ''


'''
Read *.ppt files
This requires "catppt" command
'''
def readPptFile(filename):
    try:
        return subprocess.check_output(["catppt", "-dutf-8", filename]).decode(encoding="utf-8", errors="ignore")
    except:
        print("error reading ppt file", filename)
    return ''


'''
Read *.pdf files
This requires "pdftotext" command (provided by poppler-utils)
'''
def readPdfFile(filename):
    try:
        return subprocess.check_output(["pdftotext", filename, '-']).decode(encoding="utf-8", errors="ignore")
    except:
        print("error reading pdf file", filename)
    return ''


def extractTextFromFile(filename):
    # handle case insensitive filename matching here
    p = filename.rfind('.')
    if p == -1:
        return ""
    ext = filename[p:].lower()
    content = ""
    if ext == ".srt": # *.srt subtitle file
        content = readSrtFile(filename)
    elif ext == ".ppt":
        content = readPptFile(filename)   
    elif ext == ".pptx" or ext == ".docx":
        content = readOfficeXml(filename)
    elif ext == ".doc":
        content = readDocFile(filename)
    elif ext == ".pdf":
        content = readPdfFile(filename)
    elif ext == ".txt": # ordinary text file
        f = open(filename, "r")
        if f:
            content = f.read()
            f.close()
    else:
        pass
    return content

def main():
    if len(sys.argv) < 2:
        return 1
    print(extractTextFromFile(sys.argv[1]))

if __name__ == "__main__":
    main()
