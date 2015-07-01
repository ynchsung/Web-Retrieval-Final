import sqlite3 as sql
import os
import sys
from DownloadSubtitle import fetchurl,download

def subtitle(url,base):
	if not(os.path.exists("database.db")):
		con=sql.connect("database.db")
		urls=fetchurl(url,base)
		cur=con.cursor()
		cur.execute("create table course (url text)")
		for link in urls:
			cur.execute("insert into course values(?)",(link,))
			con.commit()
			print "%s inserted" % (link)
		con.close()
		print "Database created"

	else:
		con=sql.connect("database.db")
		cur=con.cursor()
		cur.execute("select url from course")
		urls=cur.fetchall()
		for link in urls:
			download(link[0])
			cur.execute("delete from course where url=?",(link[0],))
			con.commit()

if __name__=="__main__":
	course = str(sys.argv[1])
	base="https://class.coursera.org/" + course + "/lecture"
	url="https://class.coursera.org/" + course +"/lecture/subtitles?q="	
	subtitle(url,base)
