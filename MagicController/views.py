from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from MagicController.models import *
from NLG.generator import Generator
from NLG.models import Template
from XGDic.models import XGDic


def baseInitial(request):
	# request.session['msg_error'],request.session['msg_info'] = '',''
	if not 'lanList' in request.session :	request.session['lanList'] = XGDic.getLanguages().items() 
	if not 'lanCurrent' in request.session or not request.session['lanCurrent'] in XGDic.getLanguages().keys(): 
		request.session['lanCurrent'] = 'en'
	if not 'measurement' in request.session: request.session['measurement'] = MagicIngredient.getMeasurement()
	if not 'StreamMC' in request.session: request.session['StreamMC'] = MagicCombination.create('')

def clearSession(request):
	if 'lanList' in request.session : del request.session['lanList']
	if 'lanCurrent' in request.session : del request.session['lanCurrent']
	if 'measurement' in request.session : del request.session['measurement']
	if 'StreamMC' in request.session: del request.session['StreamMC']
	if 'selectedSteps' in request.session : del request.session['selectedSteps']

	url = request.POST['next']
	return HttpResponseRedirect(url)

def getAllMagicButtons(request):
	baseInitial(request)
	listButtons = list()
	listButtons.extend(MagicIngredient.objects.all())
	listButtons.extend(MagicUtensil.objects.all())
	listButtons.extend(MagicAction.objects.all())

	if len(listButtons) == 0:  request.session['msg_info'] = "There are not Magic Buttons"
	return render_to_response('magic/index.html', {'list_buttons':listButtons}, context_instance=RequestContext(request))

def getMagicButton(request, buttonID):
	button = get_object_or_404(MagicButton, pk=buttonID)
	return render_to_response('magic/details.html', {'button': button} )

def deleteMagicButton(request, buttonID):
	button = get_object_or_404(MagicButton, pk=buttonID)
	button.delete()
	return HttpResponseRedirect(reverse('MagicController.views.getAllMagicButtons', kwargs={} ))
		

def insertMagicButton(request):
	baseInitial(request)

	if request.method == 'POST':
		# Every parameters are gotten from POST 
		desc = request.POST['description'];	cate = request.POST['category']; lan = request.POST['language']
		mean = request.POST['meaning'] ; unit = request.POST['measurement']

		if 'temporal' in request.POST: temp =  True 
		else: temp = False
		if 'path' in request.FILES: icon =  request.FILES['path'] 
		else: icon = ''
		

		# Check whether the button is already
		if cate   == 'A':	newButton = MagicAction.create(mean, lan, desc, icon, temp)
		elif cate == 'U':	newButton = MagicUtensil.create(mean, lan, desc, icon, temp)
		elif cate == 'I':	newButton = MagicIngredient.create(mean, lan, desc, icon, temp, unit)

		if newButton != None:	request.session['msg_info'] = "MAGIC BUTTON ADDED CORRECTLY"
		else:	request.session['msg_error'] = "SOME MAGIC BUTTON ALREADY ADDED WITH THE SAME MEAN AND CATEGORY"

	return render_to_response('magic/insertMB.html', {} , context_instance=RequestContext(request) )



def searchMagicButton(request):
	baseInitial(request)

	lan = request.session['lanCurrent']
	if request.method == 'POST' :
		# BY PATTERN
		if "pattern" in request.POST:
			threshold, pattern, category = 1, request.POST['pattern'],request.POST['category']
			request.session['searchedButtons'] = MagicButton.searchByPattern(category, pattern, threshold,lan)
			print 'buttons', request.session['searchedButtons']
		else: 	request.session['msg_error'] = "ERROR: SENT FORM WAS CORRUPT"
	
	sentencesMC,buttons,selectedSteps = list(),list(),list()
	if 'searchedButtons' in request.session : 
		buttons = [ (b.id,b.getLabels(lan)) for b in request.session['searchedButtons'] ]

	if 'StreamMC' in request.session :
		labels = request.session['StreamMC'].getLabels(lan)
		print 'labels',labels
		if labels.__class__ != list: labels = [labels]

	if 'selectedSteps' in request.session :
		for step in request.session['selectedSteps']:
			selectedSteps.append([step.id,step.getLabels(lan)[0]] )

	return render_to_response('magic/searchMB.html', {'buttons': buttons,'sentencesMC':labels,'selectedSteps':selectedSteps}, context_instance=RequestContext(request) )



def addMBToSelected(request, MB_ID):
	baseInitial(request)

	mb = get_object_or_404(MagicButton, pk=MB_ID)
	lan = request.session['lanCurrent']
	if 'StreamMC' in request.session:
		# Checking whether was already selected
		mbA = request.session['StreamMC'].getMBs('A')
		mbU = request.session['StreamMC'].getMBs('U')
		mbsI = request.session['StreamMC'].getMBs('I')
		if not mb.isAction() and len(mbA) == 0 : request.session['msg_error'] = "The first button must be a ACTION"
		elif mb.isAction() and len(mbA) != 0: request.session['msg_error'] = "One ACTION was already selected"
		elif mb.isUtensil() and len(mbU) != 0: request.session['msg_error'] = "One UTENSIL was already selected"
		elif mb.isIngredient() and mb in mbsI : request.session['msg_error'] = "This INGREDIENT was already selected"
		else: # SUCCESS
			request.session['StreamMC'].addMB(mb)
			request.session.modified = True
			if 'searchedButtons' in request.session: del request.session['searchedButtons']
	else: 	request.session['msg_error'] = "The session is incorrect"

	return HttpResponseRedirect('/magic/MB/search')
	# return render_to_response('magic/searchMB.html', {}, context_instance=RequestContext(request) )	


def addMCToSelected(request, MC_ID):
	mc = get_object_or_404(MagicCombination, pk=MC_ID)	
	
	if 'selectedSteps' in request.session:
		# Convert MC to Button_Step
		index  = request.session['selectedSteps'].index(mc) + 1
		tag = 'STEP '+str(index);
		mb = MagicIngredient.getObject(tag)
		if mb == None: mb = MagicIngredient.create(tag,'en','','',False,'?',True)

		# ... AND CALLING TO NORMAL PROCESS TO ADD THE MB
		return HttpResponseRedirect(reverse('MagicController.views.addMBToSelected',args=(mb.pk,) ))
	else:
		return render_to_response('magic/searchMB.html', {}, context_instance=RequestContext(request) )	



def generateMC(request):
	baseInitial(request)
	if not 'selectedSteps' in request.session :  request.session['selectedSteps'] = list()
	lan = request.session['lanCurrent']
	if request.method == 'POST' :
		if 'mc_key' in request.POST and 'StreamMC' in request.session:
			LI = [ mb.getLabels('en') for mb in request.session['StreamMC'].getMBs('I')]
			U = [ mb.getLabels('en') for mb in request.session['StreamMC'].getMBs('U')]
			A = [ mb.getLabels('en') for mb in request.session['StreamMC'].getMBs('A')]
			if len(A) != 1 and (len(LI) > 0 or len(U) > 0):
				request.session['msg_error'] = "ERROR: No enough buttons"
				return HttpResponseRedirect(reverse('MagicController.views.searchMagicButton', args=() ))
			
			key = request.POST['mc_key']
			mc = request.session['StreamMC']
			# IMPORTANT: Tengo que comprobar si hay otro MagicCombination con los mismos botones y replazarla por este, borrando la actual
			#asi evitar que el numero de MagicCombination crezca infinitamente.
			#mc.replaceDelete()
			mc.addTemplate(key,lan)
			request.session['selectedSteps'].append(mc)
			del request.session['StreamMC']
		else: 		request.session['msg_error'] = "Form was not sent correctly"		
	
	request.session.modified = True
	return HttpResponseRedirect('/recipes/upload')
	# return render_to_response('recipes/upload.html', {}, context_instance=RequestContext(request) ) 	