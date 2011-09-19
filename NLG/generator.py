from models import Template
from XGDic.models import *

def linkListWord(lan, word1, word2):
	if word1 == None : return word2
	elif word1.__class__ == list and len(word1)==0 : return word2
	elif word1.__class__ != list: word1 = list([word1])

	if word2 == None : return word1
	elif word2.__class__ == list and len(word2)==0 : return word1
	elif word2.__class__ != list: word2 = list([word2])


	collec = list()
	for w1 in word1: 
		label1 = w1 if w1.__class__ != (Word) else w1.getLabels(lan)
		for w2 in word2:
			label2 = w2 if w2.__class__ != (Word)  else w2.getLabels(lan)
			collec.append((label1 + ' ' + label2).strip())
	return collec


class Generator:		

	template = None

	def __init__(self,A,lan='en'):
		if A == None:	self.template = Template()
		else:
			self.template = Template.objects.filter(action__key=A)
			if len(self.template) == 0:
				self.template = Template()
				self.template.addAction(A,A,lan)
				self.template.save()
			elif len(self.template) == 1:
				self.template = self.template[0]
			elif len(self.template) > 1:
				print "WARNING : Several TEMPLATES for the ACTION ", A
				self.template = self.template[0]
			else:
				raise Exception ("ERROR : Template was not created")
		
	
	def getTemplate(self):
		return self.template

	# def show(self):
	# 	for key in self.templates.keys():
	# 		print "(",key,")"
	# 		print "\t", self.templates[key].show()

	
	
	# def __possiblitiesCC(self,LI):

	# 	stringCC = ''
	# 	for template in self.templates.values():
	# 		for I in LI:
	# 			print template['CC']
	# 			if I in template['CC'].keys(): 
	# 				LI.remove(I)
	# 				stringCC = stringCC + ' ' + template['CC'][I]
	# 	return stringCC


	
	# def stringTime(self, time):
	# 	stringTime = ''

	# 	if time != None and time.__class__ == int:
	# 		if time == 1 : stringTime = "for " + str(time) + " minute"
	# 		if time <= 90 : stringTime = "for " + str(time) + " minutes"
	# 		elif time < 120 : stringTime = "for " + str(int(time/60) ) + " hour and " + str(int(time%60)) + " minutes"
	# 		else : stringTime = "for " + str(int(time/60) ) + " hours and " + str(int(time%60)) + " minutes"
	# 	return stringTime



	def __possiblitiesUtensil(self,U):
		wordsU = set()
		for template in Template.objects.all():
			# wordsU = set([utensil.word for utensil in template.getUtensil() if str(utensil.key) == U]) # DOES'T WORK

			for utensil in template.getUtensil():
				print "A: ",template.getAction().key
				print utensil.key,' : ',utensil.word
				if str(utensil.key) == U:	
					wordsU.add(utensil.word)	

		# DEFAULT VALUE
		if len(wordsU) == 0:
			print "WARNING : The utensil (" + U +") was not found for ANY ACTIONS"
			wordsU.add(XGDic.getWordSentence('in the ' + U, 'en'))
			wordsU.add(XGDic.getWordSentence('with the ' + U, 'en'))
			wordsU.add(XGDic.getWordSentence('by ' + U, 'en'))
			# wordsU.add(XGDic.getWordSentence('with ' + U, 'en'))

		return list(wordsU)

	def stringIngredientCombined(self, LI):
		if LI == None or len(LI) == 0: return ''
		ccs = self.template.getCC()
		# if ccs == None: return self.__possiblitiesCC(LI)
		if len(ccs) == 0 : return ''

		wordsCC = list()
		# FIRST: it is checked for the same ACTION given.
		for I in LI:
			for cc in ccs:
				if I == cc.key: 
					LI.remove(I)
					wordsCC.append(cc.word)
		return wordsCC
		# SECOND: looking for other possibilities for the lack actions.
		# if len(wordsCC) == '': return self.__possiblitiesCC(LI)
		
	
	def stringUtensil(self, U):
		if U == None : return None
		utensil = self.template.getUtensil()
		if utensil == None : return self.__possiblitiesUtensil(U)

		utensil = utensil.filter(key=U)
		if len(utensil) == 0: 
			print "WARNING : The utensil (" + U +") was not found for THIS ACTION"
			return self.__possiblitiesUtensil(U)
		elif len(utensil) == 1: return [utensil[0].word]
		elif len(utensil) > 1: 
			print "WARNING : The utensil (" + U +") was found several times"
			return [utensil[0].word]
		
	

	def stringIngredients(self, LI):
		stringI = ''
		if LI == None: return None
		for index,I in enumerate(LI):
			if index==0:		stringI = I
			elif index<len(LI)-1:	stringI = stringI + ', ' + I
			else: stringI = stringI + ' and ' + I
		return XGDic.getWordSentence(stringI,'en')


	def calculate(self, LI=None, U=None):
		def standard(string):
			if string == None: return None
			elif string.__class__ == str or string.__class__ == unicode:   return str(string.strip().lower())
			elif string.__class__ == list:	return [ str(s.strip().lower()) for s in string]
			else: raise Exception ("ERROR : Paramenters incorrect")
				
		LI = standard(LI); 	U = standard(U)
		if self.template.getAction() == None:	wordA = None
		else: 	wordA = self.template.getAction().word
		
		
		wordsU = self.stringUtensil(U) # -> list
		wordsCC = self.stringIngredientCombined(LI) # -> list
		wordsI = self.stringIngredients(LI) #-> word
		# stringTime = self.stringTime(time)
		dic = dict()
		for lan in XGDic.getLanguages().keys():
			sentences = linkListWord(lan, wordA, wordsCC)
			sentences = linkListWord(lan, sentences, wordsI)
			sentences = linkListWord(lan, sentences, wordsU)
			dic[lan] = sentences
		
		return dic
