""" Models for managing of tranlations.
	:author: Gabriel Garrido Calvo
	:version: 0.9 (Release)
	:licence: GNU
	:contact: ggarri@gmail.com
"""

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
		Translates a string of characters using XBing or XGoogle API from a determined language to other passed.
		:param label: String to translate
		:type label: unicode
		:param lan_from: Language of passed string.
		:paran lan_to : Language to translate the string.
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
			# print "WARNING : XBing could not translate correctly : ",label
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
			# print "ERROR connection with the translate server"
			if lan_to == None:	return label,label,label,label
			else:	return label


class XGDic():
	"""
		This class has the differents methods to manage the string translation.
	"""

	# @staticmethod
	# def __addWord(label, lan):
	# 	"""
	# 		Creates a new intance of Word object in the DB from a label and associated language.
	# 		:param label: Label to create the new Word object.
	# 		:param lan: Original language with which label is given.
	# 	"""
	# 	return Word.create(label, lan)
	
	# @staticmethod
	# def __addSentence(label, lan):
	# 	return Sentence.create(label, lan)
		
	@staticmethod	
	def getWordSentence(label, lan_from='en', isVerb = False):
		"""
			Get or creates, if it is not yet, a Word object with the passed label and language.
			:param label: Label to create the new Word object.
			:type label: String less than 500 characters.
			:param lan_from: Original language with which label is given.
			:param isVerb: It is marked if the string to translate is a verb, so this makes the translation easier.
			:type isVerb: [True,False]. Default False.
			:return : One Word object with the given label.
		"""
		lan_from = lan_from.lower()
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
		"""
			Translate a string from a given language to other language without saving anything.
			:param label: Label to create the new Word object.
			:type label: String less than 500 characters.
			:param lan_from: Original language with which label is given.
			:param lan_to: Detination language with which label will be translated.
			:param isVerb: It is marked if the string to translate is a verb, so this makes the translation easier.
			:type isVerb: [True,False]. Default False.
			:return : A tuple with the label translated in ['en','es','de','fr']
		"""
		if label == '' or label == ' ':	return ''

		lan_from = lan_from.lower()
		lan_to = lan_to.lower()
		label = label.strip().lower()
		if not lan_from in languages.keys() or not lan_to in languages.keys():
			raise Exception ("ERROR: Language doesn't allowed")
		if isVerb and lan_from == 'en': label = 'to ' + label
		resul = translateToTuple(label,lan_from,lan_to)
		# print 'Translate : ',resul
		if isVerb and lan_from == 'en': resul = standard(resul)
		return resul


	@staticmethod
	def getLanguages():
		"""
			:return : Tuple with the avaiable languages in the system.
		"""
		return languages



class Word(models.Model):
	"""
		This class manages the string using 4 different languages. Spanish, French, English and German.
		:ivar en: String in English language. Max 500 characters.
		:ivar es: String in Spanish language. Max 500 characters.
		:ivar de: String in German language. Max 500 characters.
		:ivar fr: String in French language. Max 500 characters.
	"""

	en = models.CharField(blank=True, max_length=500)
	es = models.CharField(blank=True, max_length=500)
	de = models.CharField(blank=True, max_length=500)
	fr = models.CharField(blank=True, max_length=500)

	@staticmethod
	def create(label, lan, verb = False):
		"""
			Creates a new Word object using the passed paramenters.
			:param label: Main string to create a new Word object. No more than 500 characters.
			:param lan: Language which label is given.
			:param verb: Define if the string is a Verb, so that it makes the translation easier.
		"""
		def standard(cad):
			cad = cad.split()
			if len(cad) == 1: cad = cad[0]
			else: cad = cad[len(cad)-1]
			return cad

		if verb and lan == 'en': label = 'to ' + label
		en,es,de,fr = translateToTuple(label,lan)
		if verb and lan == 'en': en = standard(en); de = standard(de); es = standard(es); fr = standard(fr)

		# if en == es == de == fr : print "WARNING : Possible mistake in the original word : ",en," ",es," ",de," ",fr
		# print "CREATING WORD : ",en,' ',es,' ',de,' ',fr
		w = Word(en=en,es=es,de=de,fr=fr)
		w.save()
		return w
	
	@staticmethod
	def getObjects(label, lan):
		"""
			Gets a Word object from the database with the label and language gave in the parameters.
			:param label: String of characters that defines the Word object.
			:param lan : Language used to search it.
			:return : One list with the found Words with passed label.
		"""
		if lan == 'en': return Word.objects.filter(en=label)
		elif lan == 'es': return Word.objects.filter(es=label)
		elif lan == 'de': return Word.objects.filter(de=label)
		elif lan == 'fr': return Word.objects.filter(fr=label)
		else : raise Exception ('ERROR: Language does not supported')
	

	def getLabels(self,lan=None):
		"""
			Gets a string of the Word in the passed language.
			:param lan : Language to get the word.
			:return : Word in the passed language or a tuple with every language if lan is None
		"""
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
		"""
			Modifies the a string to another in a given language.
			:param label : String to replace.
			:param lan: Language that wants to replace.
		"""
		if lan == 'en' :  self.en = label.lower()
		elif lan == 'es' : self.es = label.lower()
		elif lan == 'de' : self.de = label.lower()
		elif lan == 'fr' : self.fr = label.lower()
		# print 'Word Updated : ',self
		self.save()

	
	# def hide(self,w):
	# 	"""
	# 		Deletes the last word in every language in the way that the string has more than two words.
	# 	"""
	# 	# for lan in XGDic.getLanguages().keys():
	# 	# 	if   lan == 'en': self.en = self.en.replace(w.en,'').strip()
	# 	# 	elif lan == 'es': self.es = self.es.replace(w.es,'').strip()
	# 	# 	elif lan == 'de': self.de = self.de.replace(w.de,'').strip()
	# 	# 	elif lan == 'fr': self.fr = self.fr.replace(w.fr,'').strip()
	# 	self.en = self.en.rsplit(' ',1)[0]
	# 	self.es = self.es.rsplit(' ',1)[0]
	# 	self.de = self.de.rsplit(' ',1)[0]
	# 	self.fr = self.fr.rsplit(' ',1)[0]
	# 	self.save()
		
	def __unicode__(self):
		"""
			Overload of print method.
		"""
		return self.en+','+self.es+','+self.de+','+self.fr

	

