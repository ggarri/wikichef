""" Models for managing of Magic-Buttons
	:author: Gabriel Garrido Calvo
	:version: 0.9
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
	:param pattern: String number one.
	:param word: String number two.
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
	Calculates the Distance Levenshtein between two strings.
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
	Labels the class MagicButtons through the 'word', which allows the use of several language to label.
	:ivar word: Word instance associated. This object keeps the same word in several languages.
	"""
	word = models.OneToOneField(Word)


	@staticmethod
	def create(meaning, lan='en', isVerb=False):
		"""
		Creates a instance of the class.
		:param meaning: Original label used.
		:type meaning: str
		:param lan: Label's language. Default 'en'
		:param isVerb: Indicate whether the label is a verb to indicate to translate.
		:return : Label with this meaning. If the label is already created, it is returned.
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
		Searching in the system whether there is a label already stored with this meaning. 
		:return: If if there is a label already it is returned else 'None'.
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
			print "WARNING : It was found many LABEL with the same meaning : ",meaning
			return obj[0]
		else:	return None
	

	def getLabels(self,lan=None):
		"""
		Method to get the label in a selected language.
		:return: The labels in the selected language.
		"""
		return self.word.getLabels(lan)
	
	def setLabel(self, label, lan='en'):
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
	Holds whole the system of elements which are used in the recipe execution.
	:ivar description : Description of the MagicButton
	:ivar isTemporal : TRUE when the MagicButton is uploaded by the user.
	:ivar icon: Image associates with the MagicButton
	:ivar label: Meaning of the element keeps in the MagicButton.
	"""	
	description = models.CharField(blank=True, max_length=500)
 	isTemporal = models.BooleanField()
 	icon = models.ImageField(blank=True, upload_to="imgs/", default="imgs/default.png")
 	label = models.ForeignKey(Label, related_name="button_set")


	@staticmethod
	def spread(list_MB):
		"""
		Classified a MagicButton list in each one of categories [MagicIngredients,MagicActions,MagicUtensils].
		:param list_MB: List of MagicButton to classify.
		:return : Dictionary structures as ['I':Ingredients,'A':Actions,'U':Utensils]
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
		Searches a MagicButton which has the given label and language. Using techniques of string distances.
		:param category: Selects the group of MagicButtons
		:type category: ['I','U','A']
		:param pattern: Label used to seek.
		:type pattern: str
		:param threshold: Threshold selects whether a MagicButton must be included.
		:type threshold: Integer
		:param lan: Language use to search. Default value is 'en'(English)
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
 		:param meaning: Label is assigned
 		:type meaning: str
 		:param lan: Language used. Default 'en'
 		:param desc: Description assigned to this MagicButton.
 		:type desc: str < 500
 		:param icon: Path icon image.
 		:param temp: Indicate whether the button was uploaded by the user
 		:type temp: Boolean
 		:param isVerb: TRUE when the Button is a ACTION to use correctly the translate.
 		"""
		self.label = Label.create(meaning, lan, isVerb)
		self.description = desc
		if icon != '' and icon != None:
			self.icon = icon
		self.isTemporal = temp
		print "CREATING BUTTON : ",meaning


	def getLabels(self, lan=None):
		"""
		Returns the label with selected language.
		:param lan: Language selected. Default value NONE.
		:type lan: 'en','es','de','fr', None
		:return : The label in the selected language or if lan is NONE a tuple with the label in all languages.
		"""
		return self.label.getLabels(lan)

	def setLabel(self, label, lan='en'):
		self.label.setLabel(label, lan)


	def isUtensil(self):
		"""
		:return : TRUE is the object is a Magic Utensil and FALSE in other case.
		"""
		return MagicUtensil.objects.filter(id=self.id).count() > 0

	def isAction(self):
		"""
		:return : TRUE is the object is a Magic Action and FALSE in other case.
		"""
		return MagicAction.objects.filter(id=self.id).count() > 0
	
	def isIngredient(self):
		"""
		:return : TRUE is the object is a Magic Ingredient and FALSE in other case.
		"""
		return MagicIngredient.objects.filter(id=self.id).count() > 0

	def isStep(self):
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
	MagicButton Inheritance Instace, which it implement the specific method for the MagicUtensils.
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
 		Creates a object of Magic Utensil with these parameters.
 		:param meaning: Label of Button.
 		:param lan: Language of uploading.
 		:param desc: Description of Button.
 		:param icon: Path of image icon of Button.
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
			if measure[0] == self.unit:	return measure[1]
		return 'Unknown'



#----------------------------------------------------------
#		CLASS MAGIC COMBINATION
#----------------------------------------------------------


class MagicCombination(models.Model):
	"""
	Keeps a list of MagicButtons which compose a whole step in one or many recipes.
	:ivar description : Description of the combination.
	:ivar time: The neccesary time to make the task of this combination.
	"""
	description = models.CharField(blank=True, max_length=500)
	MBs = models.ManyToManyField(MagicButton)

	@staticmethod
	def create(desc):
		"""
		Creates MagicCombination empty, only with a description and default primary key.
		:param desc: Description of MagicCombination.
		:type desc: str < 500
		"""
		mc = MagicCombination(description=desc)
		mc.save()
		return mc
	
	# @staticmethod
	# def isButton(button):
	# 	for MC in MagicCombination.objects.all():
	# 		if button in MC.MBs.all():
	# 			return True
	# 	return False
	

	def replaceDelete(self):
		"""
		Checks whether there is other MagicCombination with the same MagicButtons, in this case we delete
		the current Object and return the found MagicCombination and other case we return the current object.
		"""
		# DOESN'T WORK
		mbsO = set(self.MBs.all())
		for mc in MagicCombination.objects.all():
			mbs = set(mc.MBs.all())
			if len(mbsO.difference(mbs)) == 0:
				print "FOUND OTHER MAGIC COMBINATION WITH SAME MAGIC BUTTONS"
				self.delete()
				self = mc
				break

	def getStep(self, recipe):
		"""
		Gets the possition of this MagicCombination in the process of a Recipe.
		:return : The step possition which belongs this MagicCombination in the Recipe. 
		Returns '-1' when this MagicCombination don't belong at the Recipe
		"""
		for n,step in enumerate(recipe.step_set):
			if step.combination == self:
				return n
		return -1

	def getLabels(self,lan=None):
		"""
		Returns the label with selected language via stored Templates.
		:param lan: Language selected. Default value NONE.
		:type lan: 'en','es','de','fr', None
		:return : The label in the selected language or if lan is NONE a tuple with the label in all languages.
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
		:return : Returns one list of Ingredient which belong to MagicCombination.
		:rtype: List of MagicIngredients.
		"""
		dic = MagicButton.spread(self.MBs.all())
		return dic['I']
	
	def addTemplate(self, key, lan='en',only=False):
		"""
		Adds a new Template in the dababase through the relation between 'sentence' and the MagicButtons belongs of MagicCombination.
		So the next time when it is used the same buttons, we will get this one result(sentence) by Templates.
		:param sentence: Used Sentence to link these MagicCombination.
		:param lan: Selected Language uses to check Templates.
		"""
		from NLG.models import Template
		
		if key.__class__ == int:
			labels = self.getLabels(lan)
			sentence = labels[key]
		else: 	sentence = key
		print 'saving : ' + sentence
		Template.setTemplate(sentence,lan,only)

	def addMB(self,MB):
		"""
		Adds a new MagicButton in the MagicCombination
		"""
		self.MBs.add(MB)
		self.save()
	
	def getMBs(self,cat=None):
		"""
		:param cat: Category of Magic Button to return
		:type cat: 'I','A','U',None
		:return : Returns a list of Magic Button. If 'cat' is None, all of them if not only the category selected.
		"""
		if cat == None: return self.MBs.all()
		else:	return MagicButton.spread(self.MBs.all())[cat]

	def isMB(self,mb):
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




