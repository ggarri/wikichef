from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from django.views.generic.simple import redirect_to

# from RecipeController.models import Recipe

urlpatterns = patterns('',
	
	(r'^main', 'RecipeController.views.starting') ,
	(r'^instant_searching_ingredient', 'RecipeController.views.searchingMBI') ,
	
	(r'^set_state/$','RecipeController.views.setState'),
	(r'^set_new_mb','RecipeController.views.setNewMB'),
	(r'^set_current_step','RecipeController.views.setCurrentStep'),
	(r'^set_recipe_data','RecipeController.views.setRecipeData'),

	(r'^add_mb_to_step','RecipeController.views.addMBtoStep'),
	(r'^del_mb_to_step','RecipeController.views.delMBtoStep'),

	(r'^clear_session','RecipeController.views.clearSession'),
	(r'^get_current_step','RecipeController.views.getCurrentStep'),
	(r'^get_current_ingredient','RecipeController.views.getCurrentIngredient'),
	(r'^get_selected_buttons','RecipeController.views.getSelectedButtons'),
	(r'^get_used_steps','RecipeController.views.getUsedSteps'),
	(r'^get_units','RecipeController.views.getUnits'),
		
	(r'^save_stream_step','RecipeController.views.saveStreamStep'),
	(r'^delete_last_step','RecipeController.views.deleteLastStep'),
	
	(r'^update_label', 'RecipeController.views.updateLabel') ,
	(r'^upload_stream_step','RecipeController.views.uploadStreamStep'),
	(r'^upload_recipe','RecipeController.views.uploadRecipe'),

	(r'^browser/', include('RecipeController.Browser.urls')),
)
