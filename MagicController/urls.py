from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from django.views.generic.simple import redirect_to

# from MagicController.models import MagicButton

urlpatterns = patterns('',
	# (r'^clearSessionMB', 'MagicController.views.clearSessionMB') ,
	(r'^clearSession', 'MagicController.views.clearSession') ,

	# GET[recipe_id] and getRecipe is called
	(r'^MB/$', 'MagicController.views.getAllMagicButtons') ,
	(r'^MB/(?P<buttonID>\d+)/$', 'MagicController.views.getMagicButton') ,
	(r'^MB/delete/(?P<buttonID>\d+)/$', 'MagicController.views.deleteMagicButton') ,
	(r'^MB/insert', 'MagicController.views.insertMagicButton') ,
	(r'^MB/search', 'MagicController.views.searchMagicButton') ,

	#(r'^MC/$', 'MagicController.views.getAllMagicCombination') ,
	(r'^MC/addMB/(?P<MB_ID>\d+)', 'MagicController.views.addMBToSelected') ,
	(r'^MC/addMC/(?P<MC_ID>\d+)', 'MagicController.views.addMCToSelected') ,
	(r'^MC/generate', 'MagicController.views.generateMC') ,
	# (r'^MC/add', 'MagicController.views.addMagicCombination') ,
	

	# (r'^rank', 'RecipeController.views.rankRecipe') ,
	# (r'^(?P<urls>\w*).html', redirect_to, {'url': '/recipes/%(url).html'}),
)
