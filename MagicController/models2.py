from django.db import models
from django.db.models import Count
from collections import Iterable
from PIL import Image

#-------------------------------------------------

# LANGUAGES_DEVELOPED = (
# 	(u'EN', u'ENGLISH'),
# 	(u'SP', u'SPANISH'),
# )

BUTTON_TYPES = (
	(u'I', u'INGREDIENT'),
	(u'U', u'UTENSIL'),
	(u'A', u'ACTION'),
)

# DICTIONATY OF PARTICLEs
PRE_LABEL = {
	"EN": {
		"I": ['', 'the'],
		"U": ['', 'in the', 'with the'],
		"A": [''],
	},
	"ES": { 
		"I": ['', 'el'],
		"U": ['en el', 'con el'],
		"A": [''],
	},
}


POST_LABEL = {
	"EN": {
		"I": ['','and'],
		"U": [''],
		"A": [''],
	},
	"ES": { 
		"I": ['','y'],
		"U": [''],
		"A": [''],
	},
}


def mergeChain(list1, list2):
	merge = []
	# print "l1: ",list1
	# print "l2: ",list2
	for l1 in list1:
		tupla = []
		if isinstance(l1,Iterable) : tupla.extend(l1)
		else: tupla.append(l1)
		for l2 in list2:
			tupla2 = []
			tupla2.extend(tupla)
			if isinstance(l2,Iterable) : tupla2.extend(l2)
			else: tupla2.append(l2)
			merge.append(tupla2)
		# print "merge: ",merge
	return merge


				
##############################################################################
###		MODELS OF MAGIC BUTTOS
##############################################################################

class Label(models.Model):
	meaning_EN = models.CharField(blank=False, max_length=100)
	meaning_ES = models.CharField(blank=True, max_length=100)

	@staticmethod
	def create(lan, meaning):
		if lan == 'EN': return Label(meaning_EN = meaning)
		elif lan == 'ES': return Label(meaning_ES = meaning)
		raise Exception("(LABEL 001) This language doesn't ")
		

	@staticmethod
 	def getObject(lan,meaning):
 		try :
			if lan=='EN': return Label.objects.get(meaning_EN=meaning)
			elif lan=='ES': return Label.objects.get(meaning_ES=meaning)
		except:
			raise Exception("(LABEL 003) There aren't any label with meaning = " + meaning)

	@staticmethod
	def check(lan,meaning):
		if lan == 'EN':	return Label.objects.filter(meaning_EN=meaning).count() > 0
		elif lan == 'ES':	return Label.objects.filter(meaning_ES=meaning).count() > 0
		raise Exception("(LABEL 002) This language doesn't ")	


	@staticmethod
	def getLanguages():
		return ['ES','EN']

	@staticmethod
	def getPreLabels(lan, type):
		# return PRE_LABEL[lan][type]
		tags = PRE_LABEL[lan][type]
		labels = []
		if tags == None : return None
		for tag in tags :
			labels.append(Label.create(lan,tag))
		return labels
	
	@staticmethod
	def getPostLabels(lan, type):
		# return POST_LABEL[lan][type]
		tags = POST_LABEL[lan][type]		
		labels = []
		if tags == None : return None
		for tag in tags :
			labels.append(Label.create(lan,tag))
		return labels


	def was_ppLabel(self):
		return self.meaning_EN.find('|') == -1
	

	def getLabel(self, lan):
		if lan == 'EN': return str(self.meaning_EN)
		elif lan == 'ES': return str(self.meaning_ES)
		raise Exception("(LABEL 004) This language doesn't ")

	def getPre(self, lan):
		if lan == 'EN': return self.meaning_EN.split('|')[0]
		elif lan == 'ES': return self.meaning_ES.split('|')[0]
		raise Exception("(LABEL 005) This language doesn't ")
	
	def getPost(self, lan):
		if lan == 'EN': return self.meaning_EN.split('|')[1]
		elif lan == 'ES': return self.meaning_ES.split('|')[1]
		raise Exception("(LABEL 006) This language doesn't ")

	def setLabel(self,lan,cad):
		if lan == 'EN': self.meaning_EN = cad
		elif lan == 'ES': self.meaning_ES = cad
		raise Exception("(LABEL 004) This language doesn't ")

	def setPre(self, lan, cad):
		if lan == 'EN':    self.meaning_EN = cad + "|" + self.meaning_EN.split('|')[1]
		elif lan == 'ES':  self.meaning_ES = cad + "|" + self.meaning_ES.split('|')[1]
		raise Exception("(LABEL 007) This language doesn't ")

	def setPost(self, lan, cad):
		if lan == 'EN':  self.meaning_EN = self.meaning_EN.split('|')[0] + "|" + cad
		elif lan == 'ES': self.meaning_ES = self.meaning_ES.split('|')[0] + "|" + cad
		raise Exception("(LABEL 008) This language doesn't ")
	
	
	# def delete(self,*args,**kwargs):
	# 	# If the LABEL object has any relationship with other object, DON'T DELETE
	# 	if MagicButton.objects.filter(label__id=self.id).count() > 0: return
	# 	if Order.objects.filter(label__id=self.id).count() > 0: return
	# 	super(Label,self).delete(*args,**kwargs)

	
	def save(self,*args,**kwargs):
		if self.meaning_EN != None: self.meaning_EN = self.meaning_EN.upper()
		if self.meaning_ES != None: self.meaning_ES = self.meaning_ES.upper()
		super(Label,self).save(*args,**kwargs)

	def __unicode__(self):
		return self.meaning_EN


#_-------------------------------------------------------

class MBC(models.Model):
	
	@staticmethod
	def spread(list):
		# Clasify depend of category and type of object
		MB_A,MB_I,MB_U,MC = [],[],[],[]
		for mbc in list:
			try:
				if mbc.magicbutton.category == 'A': MB_A.append(mbc)
				elif mbc.magicbutton.category == 'I': MB_I.append(mbc)
				elif mbc.magicbutton.category == 'U': MB_U.append(mbc)
			except:
				MC.append(mbc)

		dic = {
			'A': MB_A,
			'I': MB_I,
			'U': MB_U,
			'C': MC,
		}
		return dic


	def getLabel(self, lan):
		try:
			b = MagicButton.objects.get(pk=self.id)
			label = b.getLabel(lan)
		except:
			mc = MagicCombination.objects.get(pk=self.id)
			label = mc.getLabel(lan)
		return label
	
	
	def __unicode__(self):
		return self.getLabel('EN')



class MagicButton(MBC):
	
	description = models.CharField(blank=True, max_length=500)
 	temporal = models.BooleanField()
 	icon = models.ImageField(blank=True, upload_to="imgs/",)
 	category = models.CharField(max_length=20, choices = BUTTON_TYPES)
 	label = models.ForeignKey(Label, related_name="button_set")


 	@staticmethod
 	def create(desc, temp, icon, cat, lan, mean):	
		# If label not exist, it is created. In other way It is gotten from DB.
		if not Label.check(lan,mean): 
			label = Label.create(lan, mean)
			label.save()
		else: 
			label = Label.getObject(lan, mean)
		
		mb = MagicButton(description=desc, temporal=temp, icon=icon, category=cat, label=label)
		return mb
		

 	@staticmethod
 	def check(lan, meaning,cat):
 		if lan=='EN' : return MagicButton.objects.filter(label__meaning_EN=meaning,category=cat).count() > 0
 		elif lan=='ES' : return MagicButton.objects.filter(label__meaning_ES=meaning,category=cat).count() > 0
 		raise Exception("(MAGICBUTTON 001) This language doesn't ")


	def getLabel(self, lan):
		return self.label.getLabel(lan)

	def __calculateDistanceLevenshtein(self, str1, str2):
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

	def getDistanceTitle(self, str1, threshold):
		dist = []
		title = self.getLabel('EN')
		if title == None : return 1000
		for substr in title.split(): 
			if len(substr) > threshold:
				dist.append(self.__calculateDistanceLevenshtein(str1.lower(), substr.lower()) )
 		if len(dist) == 0 : return 1000
 		return min(dist)
 	
 	def getDistanceDescription(self, str1, threshold):
 		dist = []
		for substr in self.description.split(): 
			if len(substr) > threshold:
				dist.append(self.__calculateDistanceLevenshtein(str1.lower(), substr.lower()) )
		if len(dist) == 0 : return 1000
 		return min(dist)
		

	def delete(self, *args,**kwargs):
		# When the label is deleted, the button as well
		if self.label != None:
			l = Label.objects.get(pk=self.label.id)
			if l.button_set.count() == 1: l.delete()
			else: super(MagicButton,self).delete(*args,**kwargs)
		else:
			raise Exception("(MAGICBUTTON 002) Error during the deleting ")
		

	def __unicode__(self):
		tag = self.getLabel('EN')
		# if label == None:	label = self.getLabel('ES')
		if self.category == 'I' : return 'I\' ' + tag
		if self.category == 'U' : return 'U\' ' + tag
		if self.category == 'A' : return 'A\' ' + tag
		return label

	class Meta:
		verbose_name = "Magic Button"
		verbose_name_plural = "Magic Buttons"




#-------------------------------------------------------------------------
#-------------------------------------------------------------------------

# class MB_Utensil(MagicButton):
# 	def __unicode__(self):
# 		return "UTENSIL : " + self.title

# class MB_Action(MagicButton):
# 	def __unicode__(self):
# 		return "ACTION : " + self.title

# class MB_Ingredient(MagicButton):
# 	def __unicode__(self):
# 		return "INGREDIENT : " + self.title






##############################################################################
###		MODELS OF MAGIC COMBINATION
##############################################################################

class MagicCombination(MBC):
	description = models.CharField(blank=True, max_length=500)
	time = models.PositiveIntegerField(default= 0)

	@staticmethod
	def create(desc, ti):
		mc = MagicCombination(description=desc, time=ti)
		return mc

	@staticmethod
	def checkButton(button):
		return MagicCombination.objects.filter(order_set__beginCombination__id=button.id).count() > 0


	@staticmethod
	def searchCombination(MB_A, MB_I, MB_U, MC,lan):
		# FIRST, It's checked whether the buttons are the same
		mcs = MagicCombination.objects.filter(order_set__endMBC=MB_A)
		num_order = 1
		if MB_U != None :	
			mcs = MagicCombination.objects.filter(order_set__endMBC=MB_U)
			num_order += 1
		if MB_I != None :
			for i in MB_I: 
				mcs = mcs.filter(order_set__endMBC=i)
				num_order += 1
		if MC != None :
			for c in MC: 
				mcs = mcs.filter(order_set__endMBC=c)
				num_order += 1
		
		if len(mcs) == 1 and mcs[0].order_set.count() == num_order: return mcs[0]
		return None

	
	@staticmethod
	def generate(MB_A, MB_I, MB_U, MC, lan):
		if MB_A == None: raise Exception("(MAGIC COMBINATION 010) The combination needs a ACTION at least")
		if MB_I == None and MC == None: raise Exception("(MAGIC COMBINATION 011) The combination needs ingredient or previous steps")

		return MagicCombination.__executeMagic(MB_A, MB_I, MB_U, MC, lan)
		


	@staticmethod
	def __executeMagic(MB_A, MB_I, MB_U, MC, lan):

		chainList = []
		# ACTION
		if MB_A != None: 
			chainList = mergeChain(Label.getPreLabels(lan,'A'), [MB_A])
			chainList = mergeChain(chainList, Label.getPostLabels(lan,'A'))
		# INGREDIENT AND COMBINATION
		if MB_I != None: 
			for cont,I in enumerate(MB_I):
				chainList = mergeChain(chainList,Label.getPreLabels(lan,'I'))
				chainList = mergeChain(chainList,[I])
				if cont < len(MB_I)-1 or MC != None:
					chainList = mergeChain(chainList,Label.getPostLabels(lan,'I'))
				else :	chainList = mergeChain(chainList,[Label.getPostLabels(lan,'I')[0]])
		elif MC != None: 
			for cont,C in enumerate(MC):
				chainList = mergeChain(chainList,Label.getPreLabels(lan,'I'))
				chainList = mergeChain(chainList,[C])
				if cont < len(MC)-1: chainList = mergeChain(chainList,Label.getPostLabels(lan,'I'))
				else: chainList = mergeChain(chainList,[Label.getPostLabels(lan,'I')[0]])
		# UTENSIL
		if MB_U != None: 
			chainList = mergeChain(chainList,Label.getPreLabels(lan,'U'))
			chainList = mergeChain(chainList,[MB_U])
			chainList = mergeChain(chainList,Label.getPostLabels(lan,'U'))
		return chainList
		
			
	def getLabel(self, lan):
		label = ""
		# Reads every linked Buttons and its labels are chained.
		for order in self.order_set.order_by('position'):
			label += " " + order.getLabel(lan)
		return label;

	def getIngredients(self):
		orders = self.order_set.all()
		mbs = []
		for order in orders: mbs.append(order.endMBC)
		return MBC.spread(mbs)['I']

	def addOrder(self,preLabel,mbc,postLabel,lan):
		mean = str(preLabel.getLabel(lan) + '|' + postLabel.getLabel(lan))
		if not Label.check(lan,mean): 
			label = Label.create(lan, mean)
			label.save()
		else: 
			label = Label.getObject(lan, mean)

		order = Order.create(self,mbc,label)
		order.save()


	def __unicode__(self):
		label = self.getLabel('EN')
		return label

	class Meta:
		verbose_name = "Magic Combination"
		verbose_name_plural = "Magic Combinations"


class Order(models.Model):
	pk2 = models.CharField(max_length=20,primary_key=True)
	beginCombination = models.ForeignKey(MagicCombination, related_name="order_set")
	endMBC = models.ForeignKey(MBC, related_name="end_order_set")
	position = models.PositiveIntegerField(default= 0)
	label = models.ForeignKey(Label)

	@staticmethod
	def create(begin, end, lab):
		try :
			o = Order(beginCombination=begin, endMBC=end, position=0, label=lab)
			return o
		except :
			raise Exception("(ORDER 001) Error while the object is created")

	def getLabel(self, lan):
		label = ''
		nodeLabel = self.label.getLabel(lan).split('|')
		if len(nodeLabel) != 2 : label += self.endMBC.getLabel(lan)
		else :
			if nodeLabel[0] != '' : label += nodeLabel[0]
			if self.endMBC != None:  label += " " + self.endMBC.getLabel(lan)
			if nodeLabel[1] != '': label += " " + nodeLabel[1]

		return label

	def addPreLabel(self,lan, cad):
		self.label.setPre(lan,cad)

	def addPosLabel(self,lan, cad):
		self.label.setPos(lan,cad)

	def save(self,*args,**kwargs):
		if self.beginCombination.id == self.endMBC.id: return
		self.pk2 = str(self.beginCombination.id) + '-' + str(self.endMBC.id)
		try:
			# SORT the 'orders'
			orders = self.beginCombination.order_set.order_by('position').reverse()
			if orders.count() :	self.position = orders[0].position+1
			else: self.position = 0
			super(Order,self).save(*args,**kwargs)
		except:
			super(Order,self).save(*args,**kwargs)

	def __unicode__(self):
		label = self.getLabel('EN')
		return label

	class Meta:
	 	ordering = ['position']
	 	unique_together = (('beginCombination','position'), )




