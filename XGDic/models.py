from django.db import models
from xgoogle import *
from xbing import *

# Create your models here.

"""
:cvar languages : Define the languages avaiable.
:type language : Dicctionary of languages.
"""
languages = {
		'en': 'English',
		'es': 'Spanish',
		'de': 'German',
		'fr': 'French',
	}



def translateToTuple(label, lan_from, lan_to=None):
	"""
		
	"""
	import re
	# Checkin that the label is not empty or with spaces or whereever
	if re.match(r'^\s*$',label) != None:
		if lan_to == None:	return '','','',''
		else :	return ''


	try:
		if lan_to == None:
			en = XBing.translate(label,lan_from,'en')
			es = XBing.translate(label,lan_from,'es')
			de = XBing.translate(label,lan_from,'de')
			fr = XBing.translate(label,lan_from,'fr')
			if en == es and es == de and de == fr:	raise Exception ()
			return en.lower(),es.lower(),de.lower(),fr.lower()
		else:
			resul = XBing.translate(label,lan_from,lan_to)
			return resul
	except:			
		try:
			print "WARNING : XBing could not translate correctly : ",label
			if lan_to == None:
				en = XGoogle.translate(label,lan_from,'en')
				es = XGoogle.translate(label,lan_from,'es')
				de = XGoogle.translate(label,lan_from,'de')
				fr = XGoogle.translate(label,lan_from,'fr')
				return en.lower(),es.lower(),de.lower(),fr.lower()
			else:
				resul = XGoogle.translate(label,lan_from,lan_to)
				return resul
		except:
			print "ERROR connection with the translate server"
			if lan_to == None:	return label,label,label,label
			else:	return label


class XGDic():

	@staticmethod
	def __addWord(label, lan):
		return Word.create(label, lan)
	
	# @staticmethod
	# def __addSentence(label, lan):
	# 	return Sentence.create(label, lan)
		
	@staticmethod	
	def getWordSentence(label, lan_from='en', isVerb = False):
		lan_from = lan_from.lower()
		# label = label.encode('utf-8')
		label = label.strip().lower()
		if not lan_from in languages.keys():
			raise Exception ("ERROR: Language doesn't allowed")

		if len(label) < 500:
			w = Word.getObjects(label,lan_from)
			if len(w) > 0: return w[0]
			return Word.create(label, lan_from, isVerb)
		raise Exception ("ERROR: Word has more than 500 characters")
	
	@staticmethod	
	def translate(label, lan_from, lan_to='en', isVerb = False):
		if label == '' or label == ' ':	return ''

		lan_from = lan_from.lower()
		lan_to = lan_to.lower()
		label = label.strip().lower()
		if not lan_from in languages.keys() or not lan_to in languages.keys():
			raise Exception ("ERROR: Language doesn't allowed")
		if isVerb and lan_from == 'en': label = 'to ' + label
		resul = translateToTuple(label,lan_from,lan_to)
		print 'Translate : ',resul
		if isVerb and lan_from == 'en': resul = standard(resul)
		return resul


	@staticmethod
	def getLanguages():
		return languages



class Word(models.Model):

	en = models.CharField(blank=True, max_length=500)
	es = models.CharField(blank=True, max_length=500)
	de = models.CharField(blank=True, max_length=500)
	fr = models.CharField(blank=True, max_length=500)

	@staticmethod
	def create(label, lan, verb = False):
		def standard(cad):
			cad = cad.split()
			if len(cad) == 1: cad = cad[0]
			else: cad = cad[len(cad)-1]
			return cad

		if verb and lan == 'en': label = 'to ' + label
		en,es,de,fr = translateToTuple(label,lan)
		if verb and lan == 'en': en = standard(en); de = standard(de); es = standard(es); fr = standard(fr)

		if en == es == de == fr : print "WARNING : Possible mistake in the original word : ",en," ",es," ",de," ",fr
		print "CREATING WORD : ",en,' ',es,' ',de,' ',fr
		w = Word(en=en,es=es,de=de,fr=fr)
		w.save()
		return w
	
	@staticmethod
	def getObjects(label, lan):
		if lan == 'en': return Word.objects.filter(en=label)
		elif lan == 'es': return Word.objects.filter(es=label)
		elif lan == 'de': return Word.objects.filter(de=label)
		elif lan == 'fr': return Word.objects.filter(fr=label)
		else : raise Exception ('ERROR: Language does not supported')
	

	def getLabels(self,lan=None):
		if lan == None:
			dic = dict()
			dic['en'] = self.en.lower(); dic['es'] = self.es.lower(); dic['de'] = self.de.lower();	dic['fr'] = self.fr.lower()
			return dic
		else:
			if   lan == 'en' : return self.en.lower()
			elif lan == 'es' : return self.es.lower()
			elif lan == 'de' : return self.de.lower()
			elif lan == 'fr' : return self.fr.lower()

	def setLabel(self, label, lan='en'):	
		if lan == 'en' :  self.en = label.lower()
		elif lan == 'es' : self.es = label.lower()
		elif lan == 'de' : self.de = label.lower()
		elif lan == 'fr' : self.fr = label.lower()
		print 'Word Updated : ',self
		self.save()

	
	def hide(self,w):
		# for lan in XGDic.getLanguages().keys():
		# 	if   lan == 'en': self.en = self.en.replace(w.en,'').strip()
		# 	elif lan == 'es': self.es = self.es.replace(w.es,'').strip()
		# 	elif lan == 'de': self.de = self.de.replace(w.de,'').strip()
		# 	elif lan == 'fr': self.fr = self.fr.replace(w.fr,'').strip()
		self.en = self.en.rsplit(' ',1)[0]
		self.es = self.es.rsplit(' ',1)[0]
		self.de = self.de.rsplit(' ',1)[0]
		self.fr = self.fr.rsplit(' ',1)[0]
		self.save()
		
	def __unicode__(self):
		return self.en+','+self.es+','+self.de+','+self.fr

	

