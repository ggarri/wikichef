#!/usr/bin/python

import simplejson as json
from simplejson import JSONDecodeError
import urllib


class XBing:

	@staticmethod
	def call(url, params):
	    response = urllib.urlopen(
	        "%s?%s" % (url, urllib.urlencode(params))).read()
	    rv =  json.loads(response.decode("UTF-8-sig"))
	    return rv

	@staticmethod
	def translate(text, from_lang='en', to_lang='es', 
	        content_type='text/plain', category='general'):
	    params = {
	    	'appId' : 'BCE1B526458079A34625D8E8D9C762201BEA4B13',
	        'text': text.encode('utf8'),
	        'to': to_lang,
	        'from': from_lang,
	        'contentType': content_type,
	        'category': category,
	        }
	    return XBing.call("http://api.microsofttranslator.com/V2/Ajax.svc/Translate", params)
