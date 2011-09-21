""" Models for management of intenationalization of Recipes
	:author: Gabriel Garrido Calvo
	:version: 0.9 (Release)
	:licence: GNU
	:contact: ggarri@gmail.com
"""

__docformat__ = "restructuredtext"

from django.db import models
from django.db.models import Avg
from MagicController.models import *
from XGDic.models import XGDic

#############################
#		GLOBAL VARIABLE SECTION
#############################

"""
:cvar DIFFICULTY_VALUES : Define the level of difficulty of the recipes
:type DIFFICULTY_VALUES : enumerate
"""
DIFFICULTY_VALUES = (
	(u'HARD' , u'HARD'),
	(u'INTERMEDATE' , u'INTERMEDATE'),
	(u'EASY' , u'EASY'),
	)

################################################################
###		MODELS OF RECIPE MANAGING
###############################################################

# -------------------------------------
# CLASS RECIPE 
#--------------------------------------
from django import forms

class Recipe(models.Model):
	""" Recipe Class manages the main information refer to one recipe.
	:ivar title: Original title gave for the Recipe by a user.
	:ivar language: Language which was uploaded.
	:ivar description: Given description for the recipe.
	:ivar time: Time, in minutes, to make the recipe.
	:ivar difficult: Level of difficulty of the recipe.
	:ivar nPerson: Number of people for which was stored the Recipe.
	:ivar img: Recipe Thumb.
	:
	"""
	title = models.CharField(max_length=100)
	language = models.CharField(max_length=2,default='en')
	description = models.ForeignKey(Word, related_name="Recipe_description_set")
	time = models.PositiveIntegerField(blank=True, default=0)
	difficult = models.CharField(max_length=20,choices=DIFFICULTY_VALUES)
	nPerson = models.PositiveIntegerField(blank=True, default=0)
	img = models.ImageField(blank=True, upload_to="imgs/", default="imgs/defaultRecipe.png")


	@staticmethod
	def create(tit, lan, desc, t, diff, nPers, path=None):
		"""
		Creates a Recipe object
		:param tit: Title of recipe
		:type tit: String with size less tan 100 characters.
		:param lan: Language which was uploaded.
		:type lan: Belongs to ['en','es','de','fr']
		:param desc: Description of the recipe.
		:type desc: String with size less tan 500 characters.
		:param t: Needed time, in minutes, to make the recipe.
		:type t: Integer number.
		:param diff: Difficult assigned.
		:type diff: Belongs to ['HARD','INTERMEDIATE','EASY'].
		:param nPers: Number of people thought for this data recipe.
		:type nPers: Integer number.
		:param path: Image path to identify the recipe.
		:type path: Image File
		:return : Recipe instance with the passed datas.
		:rtype:	Recipe.
		"""
		wd = Word.create(desc,lan)
		recipe = Recipe(title=tit,language=lan, description=wd, time=t, nPerson = nPers, img=path)
		recipe.save()
		return recipe


	@staticmethod
	def searchByIngredient(levelSimilarity,ingredients):
		"""
		Searches in the database what recipes whose ingredients are passed and level difference percentage is lesser.
		:param levelSimilarity: Level difference percentage value.
		:type levelSimilarity: Float number in range [0.0-1.0]
		:param ingredients: List of IDs ingredients to search the recipes.
		:type ingredients: ID integer array.
		:return: List of Recipe Objects which achieve given features.
		:rtype: List of Recipe Objects.
		"""
		def getLevelSimilarity(recipe):
			from NLG.models import TCC
			right = 0
			noValid = [ cc.button.id for cc in TCC.objects.all() ]
			listI = [ I[0].id for I in recipe.getIngredients() if not I[0].id in noValid]
			if len(listI) == 0 : return -1.0
			for idsSend in ingredients:
				if idsSend in listI: right +=1
			return float(right) / float(len(listI))	
		
		if len(ingredients) == 0: return Recipe.objects.all()
		listRecipes = [recipe for recipe in Recipe.objects.all() if getLevelSimilarity(recipe) >= float(levelSimilarity)]
		print levelSimilarity,listRecipes
		return listRecipes

	# @staticmethod
	# def searchByPattern(pattern,threshold, lan='en'):
	# 	"""
	# 	Searches in the system recipes whose its title close of string given
	# 	:param pattern: String seeked to find the recipes
	# 	:type pattern: str
	# 	:param threshold: Distance between its title and the pattern
	# 	:type threshold: int
	# 	:param lan: Language used to search the recipe
	# 	:return: List of Recipe ObjectS which achieve features given
	# 	:rtype: List of Recipe Objects
	# 	"""
	# 	pairs = set()	# Keeps the pairs [distance, object]
	# 	for r in Recipe.objects.all():
	# 		# Covert the original to current language given
	# 		if r.language != lan:	title = XGDic.translate(r.title,r.language,lan)
	# 		else: title = r.title
	# 		dist = searchDistance( pattern, title )
	# 		pairs.add( (dist,r) )
	# 	# Using a dict to get the buttons and a set again to remove the repeting
	# 	resul = set( v[1] for v in list(pairs) if v[0] < threshold )
	# 	return list(resul)


	
	def getIngredients(self):
		"""
		Get the ingredients used in each step in the recipe.
		:return : List of ingredients with its amount and its linked measurement unit.
		:rtype : Array List Format is [MagicIngredient, Amount , Measurement Unit]
		"""
		steps = self.step_set.all()
		listI = list()	# List of Ingredients found
		listA = list()	# List of correspong Amount per Ingredient
		listU = list()	# Measure used in the amount
		listIA = list()	# Final list with [Ingredient,Amoung,Measure]

		for s in steps:
			for a in s.amount_set.all():
				if not a.ingredient.isStep:	# Checking that is not a STEP
					if listI.count(a.ingredient) > 0:
						index = listI.index(a.ingredient)
						listA[index] += a.amount
					else:
						listI.append(a.ingredient)
						listA.append(a.amount)
						listU.append(a.ingredient.getUnit())
		# Creating the return list
		for I,AM,UN in zip(listI,listA,listU):		listIA.append([I,AM,UN])
		return listIA
	
	def __unicode__(self):
		"""The object is typed by its title variable."""
		return self.title

	class Meta:
		"""The recipes are sorted on its title"""
		ordering = ['title']






#---------------------------------------------------
#		CLASS STEP
#---------------------------------------------------


class Step(models.Model):
	"""
	Step class which consist on the description of one phase to carry a Recipe out.
	:ivar pk2 : Auxiliar primary key variable. It is used to hold the compose key (IDrecipe-IDmagiccombination).
	:ivar phase: Indicates the step order in the process to make the recipe.
	:ivar combination: MagicCombination assigned to this phase of the process.
	:ivar recipe: Recipe which this step belongs.
	:ivar ingredients: Indicates the amount to each ingredients used in this Step.
	:ivar time: Time to make this Step.
	:ivar comments: Some comments about how the Step must be carried out.
	"""
	pk2 = models.CharField(max_length=20, primary_key=True)
	phase = models.IntegerField()
	combination = models.ForeignKey(MagicCombination)
	recipe = models.ForeignKey(Recipe)
	ingredients = models.ManyToManyField(MagicIngredient , through='Amount')
	time = models.PositiveIntegerField(default=0)
	comments = models.ForeignKey(Word, related_name="Step_comment_set")

	@staticmethod
	def create(rec, comb, p, time, comment):
		""" 
		Create instance of Step via to passed parameters. 
		:param rec: Recipe which the step belongs.
		:type rec: Recipe Object.
		:param comb: MagicCombination used in the Step.
		:type comb: MagicCombination Object.
		:param p: Phase of the whole Recipe's process.
		:type phase: Integer > 0
		:param time: Determined time in the Step.
		:type time: Integer >= 0
		:param comments: Comments used to guide the correct execution of the Step.
		:type comments: String of less than 500 characters.
		:return: Recipe's saved Step.
		:rtype: Step Obj.
		"""
		wc = Word.create(comment,rec.language)
		step = Step(recipe=rec, combination = comb, phase = p, time=time, comments=wc)
		step.save()
		return step

	
	def addIngredient(self,ingr, amount):
		"""
		Add a ingredient with its corresponding ingredient amount to this Step.
		:param ingr: Ingredient added.
		:type ingr: MagicIngredient Object.
		:param amount: Amount of this Ingredient used, depending on ingredient measurement unit.
		:type amount: Float number.
		:return : Amount object created.
		"""
		obj = Amount.create(self, ingr, amount)
		obj.save()
		return obj


	def getLabels(self, lan='en'):
		"""
		Gets the label which indentifies the step. For that is used MagicCombination label + 'for Time minutes'
		:param lan: Selects the language used to get the label.
		:keyword lan: Default value 'en'(English)
		"""
		def stringTime(time):
			stringTime = ''
			if time != None and time.__class__ == long and time != 0:
				if time == 1 : stringTime = "for " + str(time) + " minute"
				if time <= 90 : stringTime = "for " + str(time) + " minutes"
				elif time < 120 : stringTime = "for " + str(int(time/60) ) + " hour and " + str(int(time%60)) + " minutes"
				else : stringTime = "for " + str(int(time/60) ) + " hours and " + str(int(time%60)) + " minutes"
			return stringTime
		stringTime = stringTime(self.time)
		# Get the string to determine the time used.
		wordT = XGDic.getWordSentence(stringTime, 'en')	
		# MagicCombination Label (selected language) + Time String
		label = self.combination.getLabels(lan)[0] + ' ' + wordT.getLabels(lan)
		return label


	def __unicode__(self):
		"""
		Returns a string which refers to the tag of the Step
		"""
	 	return self.getLabels('en')[0]

	
	def save(self,*args,**kwargs):
		"""
		Overload of the process of saving in the datebase. So the auxiliar primary will be calculated.
		"""
		# The step needs to have a correponding Recipe and Combination.
		if self.recipe != None and self.combination != None :
			# The compose key is create from the Recipe ID and Combination ID.
			self.pk2 = str(self.recipe.id) + '-' + str(self.combination.id)
			super(Step,self).save(*args,**kwargs)
			#	The ingredients are got from the combination used in the Step.
			listIngredient = self.combination.getIngredients()
			if listIngredient != None:
				for i in listIngredient:
					ingr = MagicIngredient.objects.get(pk=i.id)
					# Intialized amount to 0 
					newAmount = Amount.create(self,ingr,0)
					newAmount.save()
			
	class Meta:
		"""
		Overload the Class private variable.
		"""
		unique_together = (('phase','recipe'), )
		ordering = ['phase']


#--------------------------------------------------------
#		CLASS AMOUNT
#--------------------------------------------------------

class Amount(models.Model):
	"""
	Each included Step Ingredient must have a Amount object. This provides the amount per of ingredient in the step.
	:ivar pk2: Auxiliar variable used to get a composed primary key (MagicIngredientID-StepID)
	:ivar amount: Defines the quantity requiered
	:ivar ingredient: The Ingredient refered to.
	:ivar step: The Step refered to.
	"""	
	pk2 = models.CharField(max_length=20, primary_key=True)
	amount = models.FloatField(blank=True, default=0.0)
	ingredient = models.ForeignKey(MagicIngredient)
	step = models.ForeignKey(Step)

	
	@staticmethod
	def create(step, ingre, amount):
		"""
		Creates a Amount instance with the information about how many quantity of the ingredient is used.
		:param step : The step where belongs.
		:type step : Step Object.
		:param ingre : The measured Ingredient.
		:type ingre: MagicIngredient Object.
		:param amount : Quantity of this Ingredient.
		:type amount : Float number.
		"""
		newAmount = Amount(ingredient=ingre, step=step, amount=amount)
		return newAmount

	def save(self,*args,**kwargs):
		"""
		Steps need to have got a correponding Recipe and Combination.
		"""
		if self.ingredient != None and self.step != None :
			# The compose key is create from the Step ID and MagicIngredient ID.
			self.pk2 = str(self.step.pk2) + '-' + str(self.ingredient.id)
			super(Amount,self).save(*args,**kwargs)
			

	def __unicode__(self):
		"""
		Tag used for the class
		"""
		return str(self.ingredient) + " : " + str(self.amount) + " " + str(self.ingredient.unit) + ";"

	
	class Meta:	
		"""
		Overload the private variables.
		"""
		unique_together = (('ingredient','step'), )
