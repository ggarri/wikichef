from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.middleware.csrf import CsrfResponseMiddleware
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.utils.translation import ugettext as _

import simplejson
from MagicController.models import *
from RecipeController.models import *

def baseInitial(request):
	# request.session['msg_error'],request.session['msg_info'] = '',''
	if not 'lanList' in request.session :	request.session['lanList'] = XGDic.getLanguages().items() 
	if not 'lan' in request.session or not request.session['lan'] in XGDic.getLanguages().keys():
		request.session['lan'] = 'en'
		request.session['django_language'] = 'en'
	else:	request.session['django_language'] = request.session['lan']
	if not 'ingredientsSelected' in request.session: request.session['ingredientsSelected'] = list()

def startingBrowser(request):
	baseInitial(request)
	Ingredients = MagicIngredient.objects.filter(isStep=False)
	return render_to_response('browser/searchRecipe.html', {'MB_I':Ingredients},context_instance=RequestContext(request) )	

def getBriefRecipes(request):
	state = True; msg=''	
	if request.is_ajax() and request.method == 'GET':
		lan = request.session['lan']
		recipes = Recipe.objects.all()
		ids = [ I.id for I in request.session['ingredientsSelected'] ]
		level = request.GET['level']
		# print 'this:',level,ids
		msg = list()
		# print Recipe.searchByIngredient(level,ids)
		for r in Recipe.searchByIngredient(level,ids):
			acum = {'id':r.id,'title':r.title,'path':str(r.img)}
			acum['title'] = r.title.capitalize()
			if r.language != lan:
				 wt = XGDic.getWordSentence(r.title, r.language)
				 acum['title'] = wt.getLabels(lan).capitalize()+ ' ('+acum['title']+')'
			# wd = XGDic.getWordSentence(r.description, r.language)
			acum['desc'] = r.description.getLabels(lan)
			acum['LI'] = [ {'id':I[0].id,'label':I[0].getLabels(lan),'amount':I[1],'unit':I[2]} for I in r.getIngredients()]
			msg.append(acum);
	else: state = False; msg = _('Session is not ajax.')
	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')


def getIngredientsSelected(request):
	state = True; msg=''
	if 'ingredientsSelected' in request.session and request.is_ajax():
	 	lan = request.session['lan']
	 	# print request.session['ingredientsSelected']
	 	msg = [ {'id':I.id,'label':I.getLabels(lan),'icon':str(I.icon)} for I in request.session['ingredientsSelected'] ]
	else: state=False; msg=_('Session error.')

	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')


@csrf_exempt
def addIngredient(request):
	state = True; msg=''
	if 'ingredientsSelected' in request.session and request.is_ajax() and request.method=='GET':
		id = request.GET['id']
		try:
			mb = MagicIngredient.objects.get(id=id)
			request.session['ingredientsSelected'].append(mb)
			request.session.modified = True
		except:
			state=False; msg = _('Ingredients did not find in the system.')
	else: state=False; msg=_('Session error.')

	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')


def delIngredient(request):
	state = True;msg=''
	if 'ingredientsSelected' in request.session and request.is_ajax() and request.method=='GET':
		id = request.GET['id']
		try:
			mb = MagicIngredient.objects.get(id=id)
			if not mb in request.session['ingredientsSelected']:
				state=False; msg=_('This ingredient was not selected.')
			else: 
				request.session['ingredientsSelected'].remove(mb)
				request.session.modified = True
		except:
			state=False; msg = _('Ingredients did not find in the system.')
	else: state=False; msg=_('Session error.')

	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')


def getRecipe(request):
	baseInitial(request)
	state = True; msg=''
	if request.method == 'GET':
		lan = request.session['lan']
		id = request.GET['id']
		recipe = get_object_or_404(Recipe, pk=id)

		dic = dict()
		if recipe.language != lan:
			wt = XGDic.getWordSentence(recipe.title, recipe.language)
			dic['title'] = wt.getLabels(lan).capitalize()+ ' ('+recipe.title+')'
		else: dic['title'] = recipe.title.capitalize()
		dic['desc'] = recipe.description.getLabels(lan)

		dic['LI'] = [ {'id':I[0].id,'label':I[0].getLabels(lan),'amount':I[1],'unit':I[2]} for I in recipe.getIngredients()]
		dic['time'] = recipe.time
		dic['difficulty'] = recipe.difficult
		# To use i18n
		if dic['difficulty'] == 'EASY' : dic['difficulty'] = _('EASY')
		elif dic['difficulty'] == 'HARD' : dic['difficulty'] = _('HARD')
		elif dic['difficulty'] == 'INTERMEDIATE' : dic['difficulty'] = _('INTERMEDIATE')
		dic['img'] = str(recipe.img)
		dic['steps'] = list()
		# print 'steps :',recipe.step_set.all()
		for step in recipe.step_set.all():
			subdic = dict()
			subdic['label'] = step.getLabels(lan)
			# if subdic['label'].__class__ == list: subdic['label'][0]
			
			# if recipe.language != lan: 
			# 	# wc = XGDic.getWordSentence(step.comments,recipe.language)
			# else: subdic['comments'] = step.comments
			subdic['comments'] = step.comments.getLabels(lan)

			subdic['LI'] = [ {'label':A.ingredient.getLabels(lan),'amount':A.amount, 'unit':A.ingredient.getUnit()} for A in step.amount_set.all()]
			dic['steps'].append(subdic)
		msg = dic
		# print msg
	else: state = False; msg=_('Session incorrect')
	result = simplejson.dumps({'state':state,'msg':msg})
	return HttpResponse(result,mimetype='application/json')