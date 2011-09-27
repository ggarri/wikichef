""" Models for managing of Magic-Buttons
	:author: Gabriel Garrido Calvo
	:version: 0.9 (Release)
	:licence: GNU
	:contact: ggarri@gmail.com
"""

__docformat__ = "restructuredtext"

from django.db import models
from django.db.models import Count
from collections import Iterable
from PIL import Image
from XGDic.models import *


####################################
#		AUXILIAR PROCEDURE SECTION
####################################


def searchDistance(pattern, word):
	"""
	Calculates the 'distance'(Levenshtein Distance) between two strings.
	:param pattern: The first string.
	:param word: The second string.
	"""
	def getDistance(str1, str2):
		dist = min( [calculateDistanceLevenshtein(str1 , subStr2) for subStr2 in str2.split()] )
		return dist

	# if pattern have 0 characters, returns distance 0
	if len(pattern) == 0 : return 0
	# Taking the same length for both words, so if pattern is only 'cad' and word 'cacao' we'll compare 'cad' vs 'cac'
	word = word[0:len(pattern)]
	dist = min( [getDistance(subpattern , word) for subpattern in pattern.split()] )
	return dist


def calculateDistanceLevenshtein(str1, str2):
	"""
	Calculates the Distance Levenshtein between two words.
	"""
	# print str1,'|',str2
	str1 = str1.lower(); str2 = str2.lower()
	d=dict()
	for i in range(len(str1)+1):
		d[i]=dict()
		d[i][0]=i
	for i in range(len(str2)+1):
		d[0][i] = i
	for i in range(1, len(str1)+1):
		for j in range(1, len(str2)+1):
			d[i][j] = min(d[i][j-1]+1, d[i-1][j]+1, d[i-1][j-1]+(not str1[i-1] == str2[j-1]))
	return d[len(str1)][len(str2)]

				
#####################################################
#	MAGIC COMBINATION MODEL
#####################################################


#----------------------------------------------
#		CLASS LABEL
#----------------------------------------------

class Label(models.Model):
	"""
	Class Label is used to label a MagicButtons instance and for that class Word is used.
	:ivar word: Word instance associated. This object keeps the same word/sentence in several languages.
	"""
	word = models.OneToOneField(Word)


	@staticmethod
	def create(meaning, lan='en', isVerb=False):
		"""
		Creates a instance of the class with the passed parameters.
		:param meaning: String used to identify the class.
		:type meaning: str
		:param lan: Used language to create it. Default 'en'
		:param isVerb: Indicate whether the label is a verb to make translation easier.
		:return : Create label object.
		"""
		meaning = meaning.lower()
		# Checking whether a label with the same meaning is already created.
		obj = Label.getObject(meaning,lan)
		if obj == None:	
			word = XGDic.getWordSentence(meaning, lan ,isVerb)
			obj = Label(word=word)
		obj.save()
		return obj
	
	@staticmethod
	def getObject(meaning,lan):
		"""
		Searches in the system whether there is a label already stored with the passed label parameter.
		:return: If there is a label already this is returned, else 'None'.
		"""
		meaning = meaning.lower()
		# Checking every languages
		if lan=='en': obj = Label.objects.filter(word__en=meaning)
		elif lan=='es': obj = Label.objects.filter(word__es=meaning)
		elif lan=='de': obj = Label.objects.filter(word__de=meaning)
		elif lan=='fr': obj = Label.objects.filter(word__fr=meaning)
		else : raise Exception("ERROR: Language doesn't exist")

		if len(obj) == 1: return obj[0]
		elif len(obj) > 1:
			# print "WARNING : It was found many LABEL with the same meaning : ",meaning
			return obj[0]
		else:	return None
	

	def getLabels(self,lan=None):
		"""
		Gets the label in a passed language.
		:return: The labels in the selected language. If it is None, then a tuple with every languages is returned.
		"""
		return self.word.getLabels(lan)
	

	def setLabel(self, label, lan='en'):
		"""
		Replaces a last label in the indicated language.
		:param label: New label to replace
		:type label: str
		:param lan : Used language to replace
		:type lan : Belongs ['en','es','de','fr']
		"""
		self.word.setLabel(label, lan)
	
	

	def __unicode__(self):
		"""
		Overload the UNICODE method.
		"""
		return self.word.getLabels('en')



#----------------------------------------------------------
#		CLASS MAGIC BUTTON
#----------------------------------------------------------


class MagicButton(models.Model):
	"""
	This is the main class. It holds all the system elements which are used in the recipe execution.
	:ivar description : Description of the MagicButton
	:ivar isTemporal : TRUE when the MagicButton is uploaded by the user.
	:ivar icon: Image associates with the MagicButton
	:ivar label: Element tag.
	"""	
	description = models.ForeignKey(Word, related_name="MB_description_set")
 	isTemporal = models.BooleanField()
 	icon = models.ImageField(blank=True, upload_to="imgs/", default="imgs/default.png")
 	label = models.ForeignKey(Label, related_name="button_set")


	@staticmethod
	def spread(list_MB):
		"""
		Classifies list MagicButton in each one of categories [MagicIngredients,MagicActions,MagicUtensils]
		:param list_MB: List of MagicButton to classify.
		:return : Dictionary structure like ['I':Ingredients,'A':Actions,'U':Utensils]
		"""
		MB_A,MB_I,MB_U = None,[],None
		allI = MagicIngredient.objects.all().values_list('id',flat=True)
		allU = MagicUtensil.objects.all().values_list('id',flat=True)
		allA = MagicAction.objects.all().values_list('id',flat=True)
		for mb in list_MB:
			# tag = {'id':mb.id}
			if mb.id in allI : MB_I.append(MagicIngredient.objects.get(id=mb.id))
			elif mb.id in allA : MB_A = MagicAction.objects.get(id=mb.id)
			elif mb.id in allU : MB_U = MagicUtensil.objects.get(id=mb.id)

		dic = { 'A': MB_A, 'I': MB_I, 'U': MB_U, }

		return dic

	@staticmethod
	def searchByPattern(category, pattern,threshold, lan='en'):
		"""
		Searches a MagicButton which has the given label and language. Uses techniques of string distances.
		:param category: Selects the group of MagicButtons to search.
		:type category: ['I','U','A','all']
		:param pattern: Used pattern to seek in the buttons set.
		:type pattern: str
		:param threshold: Threshold selects whether a MagicButton must be included in the income.
		:type threshold: Integer number.
		:param lan: Used Language to search. Default value is 'en'(English)
		"""
		if category == 'all':  	buttons = MagicButton.objects.all()
		elif category == 'I':  	buttons = MagicIngredient.objects.filter(isStep=False)
		elif category == 'A':  	buttons = MagicAction.objects.all()
		elif category == 'U':  	buttons = MagicUtensil.objects.all()
		# Using a set to sort the pairs
		pairs = set( [(searchDistance(pattern, b.getLabels(lan)), b) for b in buttons] )
		# Using a dict to get the buttons and a set again to remove the repeting
		resul = set( v[1] for v in list(pairs) if v[0] < threshold )
		return list(resul)
	

 	def initial(self, meaning, lan, desc, icon, temp, isVerb=False):
 		"""
 		Initializes the MagicButton with a set of common variables.
 		:param meaning: Label assigned
 		:type meaning: str
 		:param lan: Language used. Default 'en'
 		:param desc: Description assigned to this MagicButton.
 		:type desc: str with less tan 500 characters.
 		:param icon: Icon image.
 		:param temp: Indicates whether the button was uploaded by the user
 		:type temp: Boolean
 		:param isVerb: 'TRUE' when the Button is a Action(it means a verb) so it uses correctly the translation.
 		"""
		self.label = Label.create(meaning, lan, isVerb)
		wd = Word.create(desc,lan)
		self.description = wd
		if icon != '' and icon != None:
			self.icon = icon
		self.isTemporal = temp
		# print 'INFO :',"CREATING BUTTON : ",meaning


	def getLabels(self, lan=None):
		"""
		Gets the label which indentifies the MagicButton.For that is used the associted word.
		:param lan: Selects the language used to get the label.
		:keyword lan: Range in ['es','en','de','fr']. Default value 'en'(English)
		"""
		return self.label.getLabels(lan)


	def setLabel(self, label, lan='en'):
		"""
		Changes the current label in the passed language to a new label passed for paramaters.
		"""
		self.label.setLabel(label, lan)


	def isUtensil(self):
		"""
		:return : TRUE if the object is a Magic Utensil, FALSE else.
		"""
		return MagicUtensil.objects.filter(id=self.id).count() > 0

	def isAction(self):
		"""
		:return : TRUE if the object is a Magic Action, FALSE else.
		"""
		return MagicAction.objects.filter(id=self.id).count() > 0
	
	def isIngredient(self):
		"""
		:return : TRUE if the object is a Magic Ingredient, FALSE else.
		"""
		return MagicIngredient.objects.filter(id=self.id).count() > 0

	def isStep(self):
		"""
		:return : TRUE if the object is a MagicIngredient and moreover a Step, FALSE else.
		"""
		if not self.isIngredient(): return False
		MI = MagicIngredient.objects.get(id=self.id);
		return MI.isStep

	def delete(self, *args,**kwargs):
		"""
		Overload of delete method to avoid that one label is unlinked
		"""
		if self.label != None:
			l = Label.objects.get(pk=self.label.id)
			if l.button_set.count() == 1: l.delete()
			else: super(MagicButton,self).delete(*args,**kwargs)
		else:
			raise Exception("(MAGICBUTTON 002) Error during the deleting ")


	def __unicode__(self):
		"""
		Overload Unicode Method.
		"""
		return self.getLabels('en')
		

	class Meta:
		"""
		Defines the Meta values. "Verbose"
		"""
		verbose_name = "Magic Button"
		verbose_name_plural = "Magic Buttons"



#----------------------------------------------------------
#		CLASS MAGIC UTENSIL
#----------------------------------------------------------

class MagicUtensil(MagicButton):
	"""
	MagicButton Inheritance Instance, which it implements the specific method for the MagicUtensils.
	"""

	@staticmethod
 	def create(meaning, lan='en', desc='', icon='', temp=False):
 		"""
 		Creates a object of Magic Utensil with these parameters.
 		:param meaning: Label of Button.
 		:param lan: Language of uploading.
 		:param desc: Description of Button.
 		:param icon: Path of image icon of Button.
 		:param temp: Defines whether the Button was uploaded by user.
 		"""
 		mb = MagicUtensil.getObject(meaning,lan)
 		if mb == None:
			mb = MagicUtensil()
			mb.initial(meaning, lan, desc, icon, temp)
			mb.save()
 		return mb
 	
 	@staticmethod
 	def getObject(meaning,lan='en'):
 		"""
 		Ckecks whether there is a Button in the database already store with the same label.
 		:param lan: Language to check.
 		"""
 		meaning = meaning.lower()
 		mb = [b for b in MagicUtensil.objects.all() if b.getLabels(lan) == meaning]
 		if len(mb) == 0: return None
 		return mb[0]

#----------------------------------------------------------
#		CLASS MAGIC ACTION
#----------------------------------------------------------	


class MagicAction(MagicButton):
	"""
	MagicButton Inheritance Instace, which it implement the specific method for the MagicUtensils.
	"""


	@staticmethod
 	def create(meaning, lan='en', desc='', icon='', temp=False) :
 		"""
 		Creates a object of Magic Utensil with these parameters.
 		:param meaning: Label of Button.
 		:param lan: Language of uploading.
 		:param desc: Description of Button.
 		:param icon: Path of image icon of Button.
 		:param temp: Defines whether the Button was uploaded by user.
 		"""
 		mb = MagicAction.getObject(meaning,lan)
 		if mb == None:
			mb = MagicAction()
			mb.initial(meaning, lan, desc, icon, temp, True)
			mb.save()
 		return mb

 	@staticmethod
 	def getObject(meaning,lan='en'):
 		"""
 		Ckecks whether there is a Button in the database already store with the same label.
 		:param lan: Language to check.
 		"""
 		meaning = meaning.lower()
 		mb = [b for b in MagicAction.objects.all() if b.getLabels(lan) == meaning]
 		if len(mb) == 0: return None
 		return mb[0]
#----------------------------------------------------------
#		CLASS MAGIC INGREDIENT
#----------------------------------------------------------


"""
:cvar UNIT_MEASUTEMENT: Defines the measurament units for the ingredient amounts
"""
UNIT_MEASUREMENT = (
	(u'gr',u'Grams') ,
	(u'kg',u'KiloGrams') ,
	(u'l',u'Liters') ,
	(u'dl',u'DeciLiters') ,
	(u'u',u'Units') ,
	(u'?',u'Unknown') ,
	)


class MagicIngredient(MagicButton):
	"""
	MagicButton Inheritance Instace, which it implement the specific method for the MagicUtensils.
	:ivar unit: Measurement Unit is used to measure this Ingredient.
	:ivar isStep: Classifies whether Ingredient belong a Step or not.
	"""
 	unit = models.CharField(blank=True, max_length=2, choices=UNIT_MEASUREMENT)
 	isStep = models.BooleanField(default=False)

	@staticmethod
 	def create(meaning, lan='en', desc='', icon='', temp=False, unit='?', isStep = False) :
 		"""
 		Creates a object of Magic Ingredient with these parameters.
 		:param meaning: Button Label.
 		:param lan: Uploading Language.
 		:param desc: Button Description.
 		:param icon: Button image icon.
 		:param temp: Defines whether the Button was uploaded by user.
 		:param unit: Measurement Unit
 		:param isStep: TRUE when Ingredient belongs to a Step.
 		"""
 		mb = MagicIngredient.getObject(meaning,lan)
 		if mb == None:
			mb = MagicIngredient()
			mb.initial(meaning, lan, desc, icon, temp)
			mb.isStep = isStep
			mb.unit = unit
			mb.save()
		return mb
	
	@staticmethod
 	def getObject(meaning,lan='en'):
 		"""
 		Ckecks whether there is a Button in the database already store with the same label.
 		:param lan: Language to check.
 		"""
 		meaning = meaning.lower()
 		mb = [b for b in MagicIngredient.objects.all() if b.getLabels(lan) == meaning]
 		if len(mb) == 0: return None
 		return mb[0]
 		

	@staticmethod
	def getMeasurement():
		"""
		:return : List of available Mesurements.
		"""
		return list ( {'short':unit[0],'long':unit[1]} for unit in UNIT_MEASUREMENT )
	
	def getUnit(self):
		"""
		:return : Measurement of this Ingredient.
		"""
		if self.isStep == True: return '%'
		for measure in UNIT_MEASUREMENT:
			if measure[0] == self.unit:	return measure[0]
		return 'Unknown'



#----------------------------------------------------------
#		CLASS MAGIC COMBINATION
#----------------------------------------------------------


class MagicCombination(models.Model):
	"""
	This class has a list of MagicButtons to compose a whole step in one or many recipes.
	:ivar description : Description of the combination.
	:ivar time: The neccesary time to make the task of this combination.
	"""
	MBs = models.ManyToManyField(MagicButton)

	@staticmethod
	def create():
		"""
		Creates MagicCombination empty.
		:return : Created MagicCombination Object.
		"""
		mc = MagicCombination()
		mc.save()
		return mc
	

	# def replaceDelete(self):
	# 	"""
	# 	Checks whether there is other MagicCombination with the same MagicButtons, in this case we delete
	# 	the current Object and return the found MagicCombination and other case we return the current object.
	# 	"""
	# 	# DOESN'T WORK
	# 	mbsO = set(self.MBs.all())
	# 	for mc in MagicCombination.objects.all():
	# 		mbs = set(mc.MBs.all())
	# 		if len(mbsO.difference(mbs)) == 0:
	# 			print "FOUND OTHER MAGIC COMBINATION WITH SAME MAGIC BUTTONS"
	# 			self.delete()
	# 			self = mc
	# 			break


	def getStep(self, recipe):
		"""
		Gets the possition of this MagicCombination in the a process of the passed Recipe.
		:return : Integer number with the corresponding possition. If this MagicCombination is not in the given recipe, then it is returned '-1'.
		"""
		for n,step in enumerate(recipe.step_set):
			if step.combination == self:
				return n
		return -1

	def getLabels(self,lan=None):
		"""
		Returns the label with selected language via stored Templates.
		:param lan: Used language.
		:type lan: Range is ['es','en','de','fr'].Default is None.
		:return : The label in the selected language.If lan is NONE, then it is returned a tuple with every languages.
		"""
		from NLG.models import Template

		# Classifies the MagicButton in differents categories ['I','U','A']
		dic = MagicButton.spread(self.MBs.all())
		# Using the stored template we generate all the sentences possible with this MagicButtons, considering Templates.
		resul = Template.generator(dic['A'], dic['I'], dic['U'])
		if lan == None: return resul
		else: return resul[lan]

	def getIngredients(self):
		"""
		:return : Returns the list of Ingredients of this MagicCombination.
		:rtype : List of MagicIngredients.
		"""
		dic = MagicButton.spread(self.MBs.all())
		return dic['I']
	
	def addTemplate(self, key, lan='en',only=False):
		"""
		Adds a new Template in the dababase through the given 'sentence'.
		So the next time when it is used the same buttons, we will get just this result(sentence) via Templates.
		:param key: Used Sentence to create the Template.
		:param lan: Selected Language uses to check Templates.
		:param only: Determines if the template will be created or just modified from last one.
		"""
		from NLG.models import Template
		
		if key.__class__ == int:
			labels = self.getLabels(lan)
			sentence = labels[key]
		else: 	sentence = key
		# print 'INFO : ','Saving template: ' + sentence
		return Template.setTemplate(sentence,lan,only)

	def addMB(self,MB):
		"""
		Adds a new MagicButton in the MagicCombination
		:param MB: MagicButton Object.
		"""
		self.MBs.add(MB)
		self.save()
	
	def getMBs(self,cat=None):
		"""
		Gets a list of the MagicButtons belong to this MagicCombination.
		:param cat: Filter the MagicButtons by this category.
		:type cat: Between ['I','A','U',None]
		:return : Returns a list of MagicButtons filter.
		"""
		if cat == None: return self.MBs.all()
		else:	return MagicButton.spread(self.MBs.all())[cat]

	def isMB(self,mb):
		"""
			Checks if a MagicButton already belongs to.
			:param  mb: MagicButton to check.
			:return : Returns TRUE if the MagicButton belongs, FALSE in other way.
		"""
		for b in self.MBs.all():
			if b.id == mb.id: return True
		return False

	def __unicode__(self):
		"""
		Overload UNICODE method
		"""
		label = self.getLabels('en')
		if label.__class__ == list:
			return label[0]
		return label
		

	class Meta:
		verbose_name = "Magic Combination"
		verbose_name_plural = "Magic Combinations"




