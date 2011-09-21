from XGDic.models import XGDic
import sys
import fileinput
from django.utils.encoding import smart_str, smart_unicode

def locale(file,lan):
	msg = None
	print 'File :',file," lan: ",lan
	f = open(file,'r')
	str1 = f.read()
	f.close()

	f2 = open(file+'_','w')
	for line in str1.split('\n'):
		if line.find('msgid') != -1:
			fist = line.find('"') + 1; last = line.rfind('"')
			msg = line[fist:last]
			print 'got msg : ',msg
			msg = XGDic.translate(msg.encode('utf8'),'en',lan)
		elif line.find('msgstr') != -1:
			if msg != None:	
				line = 'msgstr "'+msg.capitalize()+'"'
				line = line.encode('utf8')
				# line.replace('""','"'+msg+'"')
				print 'New Line: ',line
				msg = None
		f2.write(line+'\n')
	f2.close()

	
				
