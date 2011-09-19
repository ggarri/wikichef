from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.middleware.csrf import CsrfResponseMiddleware
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.files.uploadedfile import SimpleUploadedFile

import simplejson
from MagicController.models import *
from RecipeController.models import *

def checkCustomSentence(request, sentence, lan):
	mbs = request.session['processStep'].getMBs()
	for mb in mbs: # Using spaces to avoid cut-knife and any similar sentence
		if sentence.find(mb.getLabels(lan)) == -1: return False
	return True
	


def baseInitial(request):
	# request.session['msg_error'],request.session['msg_info'] = '',''
	if not 'lanList' in request.session :	request.session['lanList'] = XGDic.getLanguages().items() 
	if not 'lan' in request.session or not request.session['lan'] in XGDic.getLanguages().keys(): 
		request.session['lan'] = 'en'
	if not 'state' in request.session: request.session['state'] = 'initial'

def clearSession(request):
	if 'processStep' in request.session: del request.session['processStep']
	if 'usedSteps' in request.session: del request.session['usedSteps']
	if 'streamRecipe' in request.session: del request.session['streamRecipe']
	if 'state' in request.session: del request.session['state']
	return HttpResponse()

def starting(request):
	baseInitial(request)
	# if not 'state' in request.session : request.session['state'] = 'process'
	Ingredients = MagicIngredient.objects.filter(isStep=False)
	Utensils 	= MagicUtensil.objects.all()
	Actions 	= MagicAction.objects.all()
	result = {
		'MB_I':Ingredients,
		'MB_U':Utensils,
		'MB_A':Actions,
	}
	if 'streamRecipe' in request.session: 
		result['title'] = request.session['streamRecipe'].title + ' ('+str(request.session['streamRecipe'].nPerson)+' pers)'
	return render_to_response('recipes/addRecipe.html', result , context_instance=RequestContext(request) )

@csrf_exempt
def updateLabel(request):
	state = True
	if request.method=="POST" and request.is_ajax():
		id = int(request.POST['id'])
		label = request.POST['value'].strip()
		lan = request.session['lan']
		button = get_object_or_404(MagicButton, pk=id)
		# If we want to change the english button, also we have to update Template
		# if lan == 'en': Template.updateLabel(button.getLabels('en'),label)
		button.setLabel(label, lan)
	
	result = simplejson.dumps({'state': state})
	# return HttpResponse(result,mimetype='application/json')
	return HttpResponse(result,mimetype='application/json')


@csrf_exempt
def searchingMBI(request):
	if request.method=="POST" and request.is_ajax():
		threshold = 1 
		pattern = request.POST['pattern']
		category = 'I'
		lan = request.session['lan']
		buttons = MagicButton.searchByPattern(category, pattern, threshold,lan)
		dic = [{'id':b.pk, 'icon':str(b.icon), 'label':b.getLabels(lan)} for b in buttons]
		print dic
		result = simplejson.dumps(list(dic))
		
	return HttpResponse(result,mimetype='application/json')
	# return HttpResponse(result,mimetype='application/javascript')


@csrf_exempt
def getUnits(request):
	result = False
	if request.is_ajax():
		result = MagicIngredient.getMeasurement();
	result = simplejson.dumps(result)
	return HttpResponse(result,mimetype='application/json')


@csrf_exempt
def setState(request):
	if 'state' in request.GET:
		request.session['state'] = request.GET['state']
	return HttpResponse()


@csrf_exempt
def setNewMB(request):
	print "Adding new button"
	if request.method=="POST":
		# Every parameters are gotten from POST 
		cate = request.POST['category'] 
		mean = request.POST['label'] 
		lan = request.session['lan']
		desc = request.POST['description']
		if 'path' in request.FILES: icon =  request.FILES['path'] 
		else: icon = None
		temp =  True 
		if 'unit' in request.POST : unit = request.POST['unit']
		else: unit = '?'

		print cate,mean,lan,desc,icon,temp,unit
		# Check whether the button is already
		if cate   == 'A':	newButton = MagicAction.create(mean, lan, desc, icon, temp)
		elif cate == 'U':	newButton = MagicUtensil.create(mean, lan, desc, icon, temp)
		elif cate == 'I':	newButton = MagicIngredient.create(mean, lan, desc, icon, temp, unit)


	return HttpResponseRedirect(reverse('RecipeController.views.starting', kwargs={} ))


@csrf_exempt
def addMBtoStep(request):
	if not 'processStep' in request.session: request.session['processStep'] = MagicCombination.create('')
	state = True
	if not 'id' in request.GET :
		msg = 'Could not get id button'
		state = False
	
	if 'processStep' in request.session and state:
		id = int(request.GET['id'])
		lan = request.session['lan']

		# if mb == None: 	mb = get_object_or_404(MagicButton, pk=id)
		mb = get_object_or_404(MagicButton, pk=id)

		# Checking whether was already selected
		mbA = request.session['processStep'].getMBs('A')
		mbU = request.session['processStep'].getMBs('U')
		mbsI = request.session['processStep'].getMBs('I')
		if request.session['processStep'].isMB(mb): msg = 'This element is already added.';state=False
		elif not mb.isAction() and mbA == None : msg = "The first button must be a ACTION";state=False
		elif mb.isAction() and mbA != None: msg = "One ACTION was already selected";state=False
		elif mb.isUtensil() and mbU != None: msg = "One UTENSIL was already selected";state=False
		elif mb.isIngredient() and mb in mbsI : msg = "This INGREDIENT was already selected";state=False
		else: # SUCCESS
			request.session['processStep'].addMB(mb)
			request.session.modified = True
			labels = request.session['processStep'].getLabels(lan)
			if labels.__class__ != list: labels = [labels]
			print 'labels',labels
			msg = labels
	else: 	msj = 'The session is incorrect'; state=False

	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')

@csrf_exempt
def delMBtoStep(request):
	state = True
	msg=''
	print request.GET
	if not 'id' in request.GET :
		state = False
		msg = 'Could not get id button'
	elif 'processStep' in request.session:
		id = request.GET['id']
		mb = get_object_or_404(MagicButton, pk=id)
		if mb == None: msg = 'Button does not exist';state=False
		elif mb.isAction() and len(request.session['processStep'].MBs.all()) > 1 : msg = 'ACTION must be deleted last one';state=False
		else:	request.session['processStep'].MBs.remove(mb)
	else: msg='Session Incorrect'; state = False

	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')


@csrf_exempt
def getCurrentStep(request):
	state = True
	msg = ''
	if 'processStep' in request.session:
		lan = request.session['lan']
		if len(request.session['processStep'].MBs.all()) == 0: state = False
		else:
			labels = request.session['processStep'].getLabels(lan)
			if labels.__class__ != list: labels = [labels]
			msg = labels
	else: state = False; msg='There is not process in performance'
	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')

@csrf_exempt
def setCurrentStep(request):
	state = True;msg=''
	if 'processStep' in request.session and request.method=="GET":
		if len(request.session['processStep'].MBs.all()) == 0: msg='There are not elements'; state = False
		else:
			if not 'sentence' in request.GET: msg='Session error';state = False
			else:
				sentence = request.GET['sentence']
				mc = request.session['processStep']
				lan = request.session['lan']
				if checkCustomSentence(request, sentence, lan):
					mc.addTemplate(sentence,lan,True) # Just for this language
				else:
					msg = 'The new sentece must use all used elements'; state=False
	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')	



@csrf_exempt
def getSelectedButtons(request):
	state = True
	ids = None
	if 'processStep' in request.session:
		mbs = request.session['processStep'].getMBs()
		if len(mbs) == 0: state=False
		else: ids = [mb.id for mb in mbs]
	else: state=False

	result = simplejson.dumps({'state':state,'msg':ids})
	return HttpResponse(result,mimetype='application/json')


def getCurrentIngredient(request):
	state = True
	ids = None
	if 'processStep' in request.session:
		lan = request.session['lan']
		mbs = request.session['processStep'].getMBs('I')
		if len(mbs) == 0: state=False
		else: ids = [{'id':mb.id,'name':mb.getLabels(lan),'unit':mb.getUnit(),'isStep':mb.isStep} for mb in mbs]
	else: state=False
	result = simplejson.dumps({'state':state,'msg':ids})
	return HttpResponse(result,mimetype='application/json')


@csrf_exempt
def saveStreamStep(request):

	state = True
	msg = ''
	# if request.is_ajax():
	if 'key' in request.GET and 'processStep' in request.session:
		key = int(request.GET['key'])
		mc = request.session['processStep']
		lan = request.session['lan']
		if key == -1:	
			sentence = str(request.GET['custom']).lower()
			if checkCustomSentence(request, sentence, lan):
				mc.addTemplate(sentence,lan)
			else:
				msg = 'Custom Sentece must use all used elements'; state=False
		else:
			mc.addTemplate(key,lan)
	else:	msg = 'Option was not selected.'; state=False
	# else:	msg = 'Request incorrect.'; state=False 

	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')



@csrf_exempt
def uploadStreamStep(request):
	state = True
	msg = ''
	if not 'usedSteps' in request.session: request.session['usedSteps'] = list()
	if request.is_ajax() and 'processStep' in request.session and request.method=='POST':
		mc = request.session['processStep']
		LI = mc.getMBs('I'); U  = mc.getMBs('U'); A  = mc.getMBs('A')
		if A == None:
			msg = 'A Action is needed by Step.';state=False
		elif len(LI) == 0 and U == None:
			msg = 'Ingredients or Utensil are needed by Step.';state=False
		else:
			time = request.POST['time']
			desc = request.POST['desc']
			amounts = dict()
			for I in LI : amounts[str(I.id)] = int(request.POST['I'+str(I.id)])
			request.session['usedSteps'].append({'mc':mc,'time':time,'amounts':amounts,'desc':desc})
			print 'usedStep : ',request.session['usedSteps']
			tag = 'Step'+str(len(request.session['usedSteps']))
			MagicIngredient.create(tag,'en','',None,False,'?',True)

			del request.session['processStep']
	elif not 'processStep' in request.session: msg = 'Step is not created'; state=False
	else: msg = 'Session Incorrect'; state=False

	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')


@csrf_exempt
def getUsedSteps(request):
	lan = request.session['lan']
	if 'usedSteps' in request.session:
		icon = 'imgs/default.png'
		steps = MagicIngredient.objects.filter(isStep=True)
		# msg = [{'id':mc.pk,'label':mc.getLabels(lan)[0].capitalize(),'tag':'Step'+str(n+1),'icon':icon} for n,mc in enumerate(request.session['usedSteps']) ]
		msg = list()
		for n,mc in enumerate(request.session['usedSteps']):
			msg.append({'id':steps[n].pk,'tag':steps[n].getLabels(lan).capitalize(),'label':mc['mc'].getLabels(lan)[0].capitalize(),'icon':icon})
		state=True
	else:
		msg = None;state=False
	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')	


@csrf_exempt
def deleteLastStep(request):
	if 'usedSteps' in request.session and request.is_ajax():
		print request.session['usedSteps']
		if len(request.session['usedSteps']) > 0: 
			request.session['usedSteps'].pop(); state = True
			request.session.modified = True
		else:state = False
	else: state = False
	result = simplejson.dumps({'state':state})
	return HttpResponse(result,mimetype='application/json')	


@csrf_exempt
def setRecipeData(request):
	from django.forms.models import modelformset_factory

	state = True
	msg = ''
	if request.method=="POST":
		FormRecipe = modelformset_factory(Recipe)
		datas = {'form-TOTAL_FORMS':u'1','form-INITIAL_FORMS':u'0','form-MAX_NUM_FORMS':u''}
		request.POST.update(datas)
		request.POST.update({'form-0-language':request.session['lan']})
		formset = FormRecipe(request.POST,request.FILES)
		if formset.is_valid():
			r = formset.save(commit=True)[0] #Just to upload image and after delete it
			request.session['streamRecipe'] = formset.save(commit=False)[0]
			request.session['streamRecipe'].img = str(r.img)
			r.delete()
			request.session['state'] = 'process'
			request.session.modified = True
		else: 
			msg = str(formset.errors[0]); state = False

	return HttpResponseRedirect(reverse('RecipeController.views.starting', kwargs={} ))


@csrf_exempt
def uploadRecipe(request):
	state = True; msg=''
	# request.is_ajax() and 
	if 'usedSteps' in request.session and 'streamRecipe' in request.session:
		if len(request.session['usedSteps']) < 2: state = False; msg='There are not enough steps'
		else:
			newRecipe = request.session['streamRecipe']
			newRecipe.save()
			for phase,stepData in enumerate(request.session['usedSteps']):
				mc = stepData['mc']
				time = stepData['time']
				comment = stepData['desc']
				step = Step.create(newRecipe, mc, phase, time, comment)
				for I in mc.getMBs('I') : 
					print mc.getMBs('I'),stepData['amounts'],I.id
					step.addIngredient(I,stepData['amounts'][str(I.id)] )
	else: state = False; msg='Session incorrect'

	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')	