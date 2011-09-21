from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.utils import translation

def languageChooser(request):
	request.session['msg_error'],request.session['msg_info'] = '',''
	url = request.POST['next']
	request.session['lan'] = request.POST['lanSelect']
	request.session['django_language'] = request.session['lan']
	print request.session['django_language']
	return HttpResponseRedirect(url)
	# return render_to_response( reverse(url, {}, context_instance=RequestContext(request))