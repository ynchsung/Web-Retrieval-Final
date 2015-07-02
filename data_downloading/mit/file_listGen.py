count = 0
label = ""
dirname = ""
flag = True

while True:
	a = raw_input()

	if a[:7] == "http://":
		if count == 0:
			print
			label = ""
			dirname = ""
		count += 1
		if flag:
			tmp = a.find("/", 28)
			label = a[27:tmp]
			tmp2 = a.find("/", tmp + 1)
			dirname = a[tmp+1:tmp2]
			flag = False
			print dirname + " http://ocw.mit.edu/courses/" + label + "/" + dirname + " " + label,
	elif count != 0:
		if not flag:
			print count,
			flag = True
		count -= 1
		print a + ".srt",