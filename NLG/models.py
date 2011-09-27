""" Models for managing of Templates and generation of sentences.
	:author: Gabriel Garrido Calvo
	:version: 0.9 (Release)
	:licence: GNU
	:contact: ggarri@gmail.com
"""

from django.db import models
from XGDic.models import Word,XGDic
from MagicController.models import *
from django.utils.translation import ugettext as _


class Template(models.Model):
	"""
		This class controls the management of auto generation of sentences from stored templates.
		:ivar action: This element is used to define the behaviour of actions(verbs) in the sentences and to identify each template object.
		:ivar utensil: These elements are used to define the behaviour of utensils in the sentences.
		:ivar cc: These elements are used to define the behaviour of ingredients(which are used as complements) in the sentences.
	"""
	action = models.OneToOneField('TAction')	# PRIMARY KEY
	utensil = models.ManyToManyField('TUtensil')
	cc = models.ManyToManyField('TCC')
	
	@staticmethod
	def create(MB_A):
		"""
			Creates a new templace with a linked MagicAction.
			:param MB_A: MagicAction used to identify the new created template.
			:type MB_A: MaggicAction object.
			:return : The new created Template or if one already exists with the same MagicAction, then it will be.
		"""
		try:
			t = Template.objects.get(action__button=MB_A)
		except:
			t = Template()
			t.action = TAction.create(MB_A)
			t.save()
		return t

	@staticmethod
	def generator(A,LI=None,U=None):
		"""
			Generates one or more sentences in every available language using every stored Templates. For that a list of ingredients and one utensil is used.
			:param LI : List of MagicIngredients to generate the sentences.
			:param U : MagicUtensil uses to generates the sentece.
			:return : One set with each sentence generated in each available language.
			:rtype : [['en':sentence1,'es'...]['en'..]]
		"""
		if A == None:
			wError = XGDic.getWordSentence('ACTION is needed','en')
			return wError.getLabels()
		t = Template.create(A)
		return t.calculate(LI,U)
	

	@staticmethod
	def setTemplate(sentence, lan='en', only=False):
		"""
			Gets a new Template from the passed sentence. For that it is deffined the language and if the goal is replacing or creating a template. 
			:param sentence: Sentence analyzes to get the Template.
			:param lan: Language uses in the sentence.
			:param only: Define if the templase must be used in the original language(TRUE) or every language(FALSE).
		"""
		def standard(sentence):
			sentence = sentence.replace('&nbsp;',' ')
			sentence = sentence.lower()
			sentence2 = ''
			for w in sentence.split(): sentence2 += w + ' '
			return sentence2.strip()

		from operator import itemgetter, attrgetter

		sentence = standard(sentence)
		# Gather all the stored buttons
		listA,listU,listI,listCC = dict(),dict(),dict(),dict()
		for A in MagicAction.objects.all(): listA[A.getLabels(lan)] = A
		for U in MagicUtensil.objects.all(): listU[U.getLabels(lan)] = U
		for I in MagicIngredient.objects.all(): listI[I.getLabels(lan)] = I
		for CC in TCC.objects.all(): listCC[CC.button.getLabels(lan)] = CC.button
		
		A,posMB = None,list()
		for wordA in listA.keys():
			n = sentence.find(wordA)
			if n == 0: 
				A = listA[wordA]
				posMB.append( ( n,('A',A,wordA) ) )
		
		# Use just one ACTION
	 	if A == None:	return _("ERROR : A action must be in the first position of the sentence")
		else: t = Template.create(A)#; sentence.replace(A[0]['w'])
				
		for wordU in listU.keys():
			n = sentence.find(wordU)
			if n != -1: 
				posMB.append( (n,('U',listU[wordU],wordU) ) )

		for wordCC in listCC.keys():
			n = sentence.find(wordCC)
			if n != -1: posMB.append( (n,('CC',listCC[wordCC],wordCC) ) )
		
		for wordI in listI.keys():
			n = sentence.find(wordI)
			if n != -1 and not wordI in listCC.keys(): 
				posMB.append( (n,('I',listI[wordI],wordI) ) )

		# print sorted(posMB, key=itemgetter(0))
		

		for mark in sorted(posMB, key=itemgetter(0)): # step format is (pos,(type,mb))
			typ = mark[1][0]; mb = mark[1][1]; w = mark[1][2]
			pos = sentence.find(w)
			pre = sentence[:pos].strip()
			if typ   == 'U': t.addUtensil(mb,pre,lan,only)
			elif typ == 'CC': t.addCC(mb,pre,lan,only)
			elif typ == 'I' and pre != '' : t.addCC(mb,pre,lan,only)
			# Delete from start up to its position more itseft
			sentence = sentence[pos+len(w):].strip()	
			# print sentence
		# print 'Template : ',t


		# A   = [ {'mb':listA[wordA],'w':wordA}   for wordA in listA.keys() if sentence.find(wordA) != -1]
		# U   = [ {'mb':listU[wordU],'w':wordU}   for wordU in listU.keys() if sentence.find(wordU) != -1]
		# I   = [ {'mb':listI[wordI],'w':wordI}   for wordI in listI.keys() if sentence.find(wordI) != -1]
		# CC  = [ {'mb':listCC[wordCC],'w':wordCC} for wordCC in listCC.keys() if sentence.find(wordCC) != -1]

	def calculate(self,LI, U):
		"""
			Generates from the current template the chance sentences to this Ingredients and Utensil with own Action.
			:param LI: List of MagicIngredients
			:param U: MagicUtensil
			:return : One set with each sentence generated in each available language.
			:rtype : [['en':sentence1,'es'...]['en'..]]
		"""
		def listIngredients(wordsI,lan):
			"""
				Develops the ingredient list part of the sentence
			"""
			cad = ''
			w_and = XGDic.getWordSentence('and','en')
			for i,I in enumerate(LI):
				if i == 0 : cad = I.getLabels(lan)
				elif i==len(LI)-1 : cad += ' '+ w_and.getLabels(lan) + ' ' + I.getLabels(lan)
				else:	cad += ', ' + I.getLabels(lan)
			return cad

		#	UTENSILS TEMPLATE
		wordsU = list()
		if U != None:	# Checks if utensils is
			# Search if it was used in this template sometime.
			try: wordsU = [self.utensil.get(button=U)]	
			except:	# If it was used in any other template.
				wordsU = [tu for tu in TUtensil.objects.filter(button=U)]
			if len(wordsU) == 0: # Else, creates a list with default prefixs.
				# print 'Using default prefixs'
				wordsU.append(TUtensil.create(U,'in the'))
				wordsU.append(TUtensil.create(U,'with the'))
				wordsU.append(TUtensil.create(U,'onto'))

		#	COMPLEMENT INGREDIENTS
		wordsI = list()
		if LI.__class__ == list:	# Check if there is a list in the parameters
			# Here, just searchs if each ingredients was used anytime like complement.
			for I in LI[:]:
				try: # It was used in this template.
					wordsI.append([self.cc.get(button=I)]); LI.remove(I)
				except: # Or it was used for others.
					acum = [tcc for tcc in TCC.objects.filter(button=I)]
					if len(acum) : 	wordsI.append(acum); LI.remove(I)

		# Starts the chance list with the action
		sentencesMB = [[self.action]]
		# Join each current chance with each utensil chance.
		if len(wordsU): sentencesMB = [ (s+[wu]) for wu in wordsU for s in sentencesMB]
		# Join each current chance with each complement ingredient chance.
		if len(wordsI):
			for l1I in wordsI:
				sentencesMB = [ (s+[wi]) for wi in l1I for s in sentencesMB]

		# Creates dictionary with all the languages
		dic = dict()
		# print sentencesMB
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
		"""
			Adds a new Utensil to the current template to be used in the future.
			:param mb: MagicUtensil associated.
			:param pre: Prefix used to link the utensil in the sentence.
			:param lan: Language defines for the prefix.
			:param only: Define if the Utensil prefix must be created(False) or modified(True).
		"""
		try:
			u = self.utensil.get(button=mb)
			if not only: u.setPre(pre,lan)
			else: u.preposition.setLabel(pre,lan)
		except:
			# print 'Creating Utensil : ',pre,mb.getLabels('en')
			self.utensil.add(TUtensil.create(mb,pre,lan))
		
	def addCC(self, mb, pre,lan='en',only=False):
		"""
			Adds a new Ingredient complement to the current template to be used in the future.
			:param mb: MagicIngredient associated.
			:param pre: Prefix used to link the complement ingredient in the sentence.
			:param lan: Language defines for the prefix.
			:param only: Define if the Utensil prefix must be created(False) or modified(True).
		"""
		try:
			c = self.cc.get(button=mb)
			if not only: c.setPre(pre,lan)
			else: c.preposition.setLabel(pre,lan)
		except:
			# print 'Creating CC : ',pre,mb.getLabels('en')
			self.cc.add(TCC.create(mb,pre,lan))
	
	def getAction(self):
		"""
			:return : TAction object.
		"""
		return self.action
	
	def getUtensil(self):
		"""
			:return : TUtensil list of objects.
		"""
		return self.utensil.all()
	
	def getCC(self):
		"""
			:return : TCC list of objects.
		"""
		return self.cc.all()

	def __unicode__(self):
		"""The object is typed by its action in first place and the utensils and ingredients in the next ones."""
		labelA = self.action.getLabels('en')
		labelU = [tu.getLabels('en') for tu in self.utensil.all()]
		labelCC = [tcc.getLabels('en') for tcc in self.cc.all()]
		return labelA + '\n\t' + str(labelU) + '\n\t' + str(labelCC)

####################################################

#####################################################

class TAction(models.Model):
	"""
		This class stores a MagicAction and the chance suggestions associated with it.
		:ivar button: MagicAction used to identify it.
		:ivar suggestion: List of words with the suggestions.
	"""
	button = models.OneToOneField(MagicAction)
	suggestion = models.ManyToManyField(Word)

	@staticmethod
	def create(mb):
		"""
			Creates a new object with the passed MagicAction and if this already exists, it don't do any.
			:param mb: MagicAction object.
			:return : The new object created or the object previously stored.
		"""
		try:
			obj = TAction.objects.get(button=mb)
		except:
			obj = TAction(button=mb)
			obj.save()
		return obj

	def getLabels(self,lan='en'):
		"""
			Gets the label gave for this object which is corresponded with the label of its MagicAction.
			:param lan: Language to get the label.
			:return : The label of its MagicAction in the given language.
		"""
		return self.button.getLabels(lan)
	
	def getSuggestion(self,lan='en'):
		"""
			Gets the list of suggestion in the given language.
			:param lan: Language used to get the label.
			:return : A list of the suggestion in the passed language.
		"""
		return [s.getLabels(lan) for s in self.suggestion.all()]

	def addSuggestion(self, sug, lan='en'):
		"""
			Adds a new suggestion.
			:param sug: String with the suggestion.
			:param lan: Language in that the suggestion is given.
		"""
		w_sug = XGDic.getWordSentence(sug,lan)
		self.suggestion.add(w_sug)
		self.save()

	def __unicode__(self):
		""" Typed the label of TAction from the MagicAcction stored."""
		return self.getLabels('en')

class TUtensil(models.Model):
	"""
		This class stores the MagicUtensil and its prefix which is used to execute the sentences in the templates.
		:ivar button: MagicUtensil linked.
		:ivar preposition: Word object with the prefix uses in the sentence.
	"""
	button = models.ForeignKey(MagicUtensil)
	preposition = models.ForeignKey(Word)

	@staticmethod
	def create(mb, pre='', lan='en'):
		"""
			Creates a new TUtensil object with the passed parameters.
			:param mb : Used MagicUtensil.
			:param pre: Prefix of the MagicUtensil in the sentences.
			:param lan: Language used in the given prefix.
		"""
		# w_pre = Word.create(pre+' '+mb.getLabels(lan),lan)
		# w_pre.hide(mb.label.word)
		w_pre = Word.create(pre,lan)
		obj = TUtensil(button=mb, preposition=w_pre)
		obj.save()
		return obj

	def getLabels(self,lan='en'):
		"""
			Returns the labels of the MagicUtensil plus its prefix.
			:param lan: Language defines the obtained label.
			:return : Label that defines the TUtensil.
		"""
		return self.preposition.getLabels(lan) + ' ' + self.button.getLabels(lan)

	def setPre(self,pre,lan='en'):
		"""
			Updates the current prefix to another one.
			:param pre: New prefix to hook.
			:param lan: Language of the new prefix.
		"""
		w_pre = XGDic.getWordSentence(pre,lan)
		self.preposition = w_pre
		self.save()
	
	def __unicode__(self):
		return self.getLabels('en')
	

class TCC(models.Model):
	"""
		This class stores the MagicIngredients used as complements in the sentences and its prefix.
		:ivar button: MagicIngredient linked.
		:ivar preposition: Word object with the prefix uses in the sentence.
	"""
	button = models.ForeignKey(MagicIngredient)
	preposition = models.ForeignKey(Word)

	@staticmethod
	def create(mb, pre='', lan='en'):
		"""
			Creates a new TCC object with the passed parameters.
			:param mb : Used MagicIngredient.
			:param pre: Prefix of the MagicIngredient in the sentences.
			:param lan: Language used in the given prefix.
		"""
		# w_pre = Word.create(pre+' '+mb.getLabels(lan),lan)
		# w_pre.hide(mb.label.word)
		w_pre = Word.create(pre,lan)
		obj = TCC(button=mb, preposition=w_pre)
		obj.save()
		return obj
	
	def getLabels(self,lan='en'):
		"""
			Returns the labels of the MagicIngredient plus its prefix.
			:param lan: Language defines the obtained label.
			:return : Label that defines the TCC.
		"""
		return self.preposition.getLabels(lan) + ' ' + self.button.getLabels(lan)

	def setPre(self,pre,lan='en'):
		"""
			Updates the current prefix to another one.
			:param pre: New prefix to hook.
			:param lan: Language of the new prefix.
		"""
		w_pre = XGDic.getWordSentence(pre,lan)
		self.preposition = w_pre
		self.save()
	
	def __unicode__(self):
		return self.getLabels('en')



# Read a template file with the buttons and sentences
def LoadFileTemplate(path):
	"""
		Loads a file which has in plain text several MagicButtons with its corresponding complements is stored in the DB.
		For that a speficic syntax is used.
	"""
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
			