import urllib2

def fetchurl(url,base):
	f=urllib2.urlopen(base)
	s=f.read()
	links=[]

	while True:
		start=s.find(url)
		if (start==-1):
			break
		else:
			end=s.find('"',start)
			print "%s fetched" % (s[start:end])
			links.append(s[start:end])
			s=s[end:]

	return links

def download(url):
	lec_no = url[url.find('=')+1:url.find('_')]
	lec_type=url.split('=')[-1]

	file_name = ("Lecture%s.%s") %(lec_no,lec_type) 

	u = urllib2.urlopen(url)
	f = open(file_name, 'wb')

	file_size_dl = 0
	block_sz = 8192

	while True:
		buf = u.read(block_sz)
		if not buf:
			break

		file_size_dl += len(buf)
		f.write(buf)	
	f.close()
	print "%s downloaded" % (url)
