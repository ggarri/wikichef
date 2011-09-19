from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
	# Add the local recipe urls
    (r'^recipes/', include('RecipeController.urls')),
    # Add the local recipe urls
    # (r'^magic/', include('MagicController.urls')),
    (r'^language', 'XGDic.views.languageChooser'),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
