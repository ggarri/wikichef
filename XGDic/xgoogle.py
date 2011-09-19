#!/usr/bin/python

import os
import urllib
import simplejson
from time import sleep, ctime


url_detech = 'http://ajax.googleapis.com/ajax/services/language/detect?'
url_translate = 'http://ajax.googleapis.com/ajax/services/language/translate?'
detect_params = {'v':'1.0', 'q':'',}
translate_params = {'v':'1.0', 'q':'', 'langpair':'',}



class InputError(Exception):

    def __init__(self, text, status):
        self.text = text
        self.status = status
        

class XGoogle:
    @staticmethod
    def detect_language(text):
        detect_params['q'] = text

        url = url_detech + urllib.urlencode(detect_params)
        response = simplejson.load(urllib.urlopen(url))    

        data = response['responseData']
        
        return data

    @staticmethod
    def translate(text, source_lang="", dest_lang=""):
        text = text.encode('utf8')
        translate_params['q'] = text
        translate_params['langpair'] = source_lang + '|' + dest_lang
        url = url_translate + urllib.urlencode(translate_params)
        response = simplejson.load(urllib.urlopen(url))
        
        if response['responseStatus'] != 200:
            raise Exception(text, response['responseStatus'])
        
        data = response['responseData']
        return data.values()[0]