""" Models for managing of Recipes
	:author: Gabriel Garrido Calvo
	:version: 0.6
"""

from django.db import models
from XGDic.models import Word,XGDic
from MagicController.models import *


class Template(models.Model):
	action = models.OneToOneField('TAction')	# PRIMARY KEY
	utensil = models.ManyToManyField('TUtensil')
	cc = models.ManyToManyField('TCC')
	
	@staticmethod
	def create(MB_A):
		try:
			t = Template.objects.get(action__button=MB_A)
		except:
			t = Template()
			t.action = TAction.create(MB_A)
			t.save()
		return t

	@staticmethod
	def generator(A,LI=None,U=None):
		if A == None:
			wError = XGDic.getWordSentence('ACTION is needed','en')
			return wError.getLabels()
		t = Template.create(A)
		return t.calculate(LI,U)
	

	@staticmethod
	def setTemplate(sentence, lan='en', only=False):
		from operator import itemgetter, attrgetter

		# sentence = standard(sentence)
		sentence = sentence.lower()
		# Gather all the stored buttons
		listA,listU,listI,listCC = dict(),dict(),dict(),dict()
		for A in MagicAction.objects.all(): listA[A.getLabels(lan)] = A
		for U in MagicUtensil.objects.all(): listU[U.getLabels(lan)] = U
		for I in MagicIngredient.objects.all(): listI[I.getLabels(lan)] = I
		for CC in TCC.objects.all(): listCC[CC.button.getLabels(lan)] = CC.button
		
		A,posMB = list(),list()
		for wordA in listA.keys():
			n = sentence.find(wordA)
			if n != -1: 
				A.append(listA[wordA])
				posMB.append( ( n,('A',listA[wordA],wordA) ) )

		for wordU in listU.keys():
			n = sentence.find(wordU)
			if n != -1: posMB.append( (n,('U',listU[wordU],wordU) ) )

		for wordCC in listCC.keys():
			n = sentence.find(wordCC)
			if n != -1: posMB.append( (n,('CC',listCC[wordCC],wordCC) ) )
		
		for wordI in listI.keys():
			n = sentence.find(wordI)
			if n != -1 and not wordI in listCC.keys(): 
				posMB.append( (n,('I',listI[wordI],wordI) ) )

		print sorted(posMB, key=itemgetter(0))
		# Use just one ACTION
	 	if len(A) == 0:	print "ERROR : There aren't action in the sentence";return None
	 	elif len(A) > 1:	print "ERROR : There are more than one action in the sentence";return None
		else: t = Template.create(A[0])#; sentence.replace(A[0]['w'])

		for mark in sorted(posMB, key=itemgetter(0)): # step format is (pos,(type,mb))
			typ = mark[1][0]; mb = mark[1][1]; w = mark[1][2]
			pos = sentence.find(w)
			pre = sentence[:pos].strip()
			if typ   == 'U': t.addUtensil(mb,pre,lan,only)
			elif typ == 'CC': t.addCC(mb,pre,lan,only)
			# Delete from start up to its position more itseft
			sentence = sentence[pos+len(w):].strip()	
		print 'Template : ',t


		# A   = [ {'mb':listA[wordA],'w':wordA}   for wordA in listA.keys() if sentence.find(wordA) != -1]
		# U   = [ {'mb':listU[wordU],'w':wordU}   for wordU in listU.keys() if sentence.find(wordU) != -1]
		# I   = [ {'mb':listI[wordI],'w':wordI}   for wordI in listI.keys() if sentence.find(wordI) != -1]
		# CC  = [ {'mb':listCC[wordCC],'w':wordCC} for wordCC in listCC.keys() if sentence.find(wordCC) != -1]

	def calculate(self,LI, U):
		def listIngredients(wordsI,lan):
			cad = ''
			for i,I in enumerate(LI):
				if i == 0 : cad = I.getLabels(lan)
				elif i==len(LI)-1 : cad += ' and ' + I.getLabels(lan)
				else:	cad += ', ' + I.getLabels(lan)
			return cad

		#	UTENSILS TEMPLATE
		wordsU = list()
		if U != None:
			try: wordsU = [self.utensil.get(button=U)]
			except:
				wordsU = [tu for tu in TUtensil.objects.filter(button=U)]
			if len(wordsU) == 0:
				print 'Using default prefixes'
				wordsU.append(TUtensil.create(U,'in the'))
				wordsU.append(TUtensil.create(U,'with the'))
				wordsU.append(TUtensil.create(U,'onto'))
		#	UTENSILS COMPLEMENT INGREDIENTS
		wordsI = list()
		if LI.__class__ == list:
			for I in LI[:]:
				try: 
					wordsI.append([self.cc.get(button=I)]); LI.remove(I)
				except: 
					acum = [tcc for tcc in TCC.objects.filter(button=I)]
					if len(acum) : 	wordsI.append(acum); LI.remove(I)


			
		
		sentencesMB = [[self.action]]
		if len(wordsU): sentencesMB = [ (s+[wu]) for wu in wordsU for s in sentencesMB]
		if len(wordsI):
			for l1I in wordsI:
				sentencesMB = [ (s+[wi]) for wi in l1I for s in sentencesMB]
		# Creates dictionary with all the languages
		dic = dict()
		print sentencesMB
		for lan in XGDic.getLanguages().keys():
			dic[lan],acum = list(),set()
			for sentence in sentencesMB:
				chance = ''
				for tw in sentence: chance += ' ' + tw.getLabels(lan)
				chance += ' ' + listIngredients(wordsI,lan)
				acum.add(chance)
			dic[lan].extend( list(acum) )
		return dic

	
	def addUtensil(self, mb, pre,lan='en',only=False):
		try:
			u = self.utensil.get(button=mb)
			if not only: u.setPre(pre,lan)
			else: u.preposition.setLabel(pre,lan)
		except:
			print 'Creating Utensil : ',pre,mb.getLabels('en')
			self.utensil.add(TUtensil.create(mb,pre,lan))
		
	def addCC(self, mb, pre,lan='en',only=False):
		try:
			c = self.cc.get(button=mb)
			if not only: c.setPre(pre,lan)
			else: c.preposition.setLabel(pre,lan)
		except:
			print 'Creating CC : ',pre,mb.getLabels('en')
			self.cc.add(TCC.create(mb,pre,lan))
	
	def getAction(self):
		return self.action
	
	def getUtensil(self):
		return self.utensil.all()
	
	def getCC(self):
		return self.cc.all()

	def __unicode__(self):
		labelA = self.action.getLabels('en')
		labelU = [tu.getLabels('en') for tu in self.utensil.all()]
		labelCC = [tcc.getLabels('en') for tcc in self.cc.all()]
		return labelA + '\n\t' + str(labelU) + '\n\t' + str(labelCC)

####################################################

#####################################################

class TAction(models.Model):
	# key = models.CharField(max_length=20)
	button = models.OneToOneField(MagicAction)
	suggestion = models.ManyToManyField(Word)

	@staticmethod
	def create(mb):
		try:
			obj = TAction.objects.get(button=mb)
		except:
			obj = TAction(button=mb)
			obj.save()
		return obj

	def getLabels(self,lan='en'):
		return self.button.getLabels(lan)
	
	def getSuggestion(self,lan='en'):
		return [s.getLabels(lan) for s in self.suggestion.all()]

	def addSuggestion(self, sug, lan='en'):
		w_sug = XGDic.getWordSentence(sug,lan)
		self.suggestion.add(w_sug)
		self.save()

	def __unicode__(self):
		return self.getLabels('en')

class TUtensil(models.Model):
	# key = models.CharField(max_length=20)
	button = models.ForeignKey(MagicUtensil)
	preposition = models.ForeignKey(Word)

	@staticmethod
	def create(mb, pre='', lan='en'):
		w_pre = Word.create(pre+' '+mb.getLabels(lan),lan)
		w_pre.hide(mb.label.word)
		obj = TUtensil(button=mb, preposition=w_pre)
		obj.save()
		return obj

	def getLabels(self,lan='en'):
		return self.preposition.getLabels(lan) + ' ' + self.button.getLabels(lan)

	def setPre(self,pre,lan='en'):
		w_pre = XGDic.getWordSentence(pre,lan)
		self.preposition = w_pre
		self.save()
	
	def __unicode__(self):
		return self.getLabels('en')
	

class TCC(models.Model):
	# key = models.CharField(max_length=20)
	button = models.ForeignKey(MagicIngredient)
	preposition = models.ForeignKey(Word)

	@staticmethod
	def create(mb, pre='', lan='en'):
		w_pre = Word.create(pre+' '+mb.getLabels(lan),lan)
		w_pre.hide(mb.label.word)
		obj = TCC(button=mb, preposition=w_pre)
		obj.save()
		return obj
	
	def getLabels(self,lan='en'):
		return self.preposition.getLabels(lan) + ' ' + self.button.getLabels(lan)

	def setPre(self,pre,lan='en'):
		w_pre = XGDic.getWordSentence(pre,lan)
		self.preposition = w_pre
		self.save()
	
	def __unicode__(self):
		return self.getLabels('en')



# Read a template file with the buttons and sentences
def LoadFileTemplate(path):
	try:
		f = open(path,'r')
	except:
		raise Exception('File is not exists.')
	text = f.read()
	f.close()
	for line in text.split('\n'):
		# print 'line : ',line
		if len(line) == 0: continue
		# print line[0],line[1:]
		type = line[0]
		mb,desc,icon,label,unit=None,'',None,'','?'
		for index,piece in enumerate(line[1:].split('|')):
			piece = piece.strip()
			# LABEL
			if index == 0 : label = piece
			# DESCRIPTION
			elif index == 1:
				if type == 'I':	unit = piece
				else: desc = piece
			# ICON and it is the last one
			elif index == 2: 
				icon = piece
				if type == 'A': mb = MagicAction.create(label,'en',desc,icon);
				elif type == 'U': mb = MagicUtensil.create(label,'en',desc,icon);
				elif type == 'I': mb = MagicIngredient.create(label,'en','',icon,False,unit);
				print label,desc,icon,mb
				mb.save()
			# COMPLEMENTS
			elif index > 2:
				if piece == 'BLANK': piece = ''
				elif piece == 'NONE' : continue
				elif mb == None: continue
				
				if type == 'A':
					TA = TAction.create(mb)
					TA.addSuggestion(piece)
				elif type == 'U':	TUtensil.create(mb,piece)
				elif type == 'I':	TCC.create(mb,piece)
			