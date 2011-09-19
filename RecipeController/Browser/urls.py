from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from django.views.generic.simple import redirect_to

# from RecipeController.models import Recipe

urlpatterns = patterns('',

	(r'^main', 'RecipeController.Browser.views.startingBrowser') ,
	(r'^get_brief_recipes', 'RecipeController.Browser.views.getBriefRecipes') ,
	(r'^get_ingredients_selected','RecipeController.Browser.views.getIngredientsSelected') ,
	(r'^add_ingredient','RecipeController.Browser.views.addIngredient') ,
	(r'^del_ingredient','RecipeController.Browser.views.delIngredient') ,
	(r'^get_recipe','RecipeController.Browser.views.getRecipe') ,
)
