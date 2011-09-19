# from RecipeController.models import Recipe, Amount, Step
# #from MagicController.models import MagicCombination
# from django.contrib import admin

# class StepInline(admin.TabularInline):
# 	model = Step
# 	extra = 0
# 	readonly_fields = ['phase','pk2']

# class AmountInline(admin.TabularInline):
# 	model = Amount
# 	extra = 0
# 	# list_filter = ['ingredient']
# 	readonly_fields = ['ingredient']

# class RecipeAdmin(admin.ModelAdmin):

# 	model = Recipe
# 	fieldsets = [
# 		(None,	{'fields': ['title']} ),
# 		('Information',	{'fields': ['description', 'scoreAverage']} ),
# 		('Minutes',	{'fields': ['time']} ),
# 		('Level of Dificult',	{'fields': ['difficult']} ),
# 		('Number of People',	{'fields': ['nPerson']} ),
# 		]

# 	search_fields = ['title']
# 	list_filter = ['scoreAverage']
# 	readonly_fields = ['scoreAverage']

# 	# def save_model(self, request, obj, form, change):
        

# admin.site.register(Recipe, RecipeAdmin)
# #admin.site.register(Recipe)

