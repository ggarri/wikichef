import os
import sys

path = '/virtual/wikichef/lib/python2.7/site-packages/'
if path not in sys.path:
    sys.path.insert(0,path)

path = '/srv/http'
if path not in sys.path:
    sys.path.insert(0,path)

path = '/srv/http/wikichef'
if path not in sys.path:
    sys.path.insert(0,path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'wikichef.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

