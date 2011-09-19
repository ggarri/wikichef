from MagicController.models import MagicButton, MagicCombination,  Label
# from MagicController.models import MB_Ingredient, MB_Utensil, MB_Action
from django.contrib import admin


# # class LabelOrderInline(admin.StackedInline):
# #  	model = Label
# #  	# fk_name = "order_set"
# #  	fieldsets = [
# # 		('Labels', {'fields' : ['meaning_EN', 'meaning_ES']} ),
# # 	]

# class LabelMBInline(admin.StackedInline):
#  	model = Label
#  	# fk_name = "button_set"
#  	fieldsets = [
# 		('Labels', {'fields' : ['meaning_EN', 'meaning_ES']} ),
# 	]


# # class OrderInline(admin.TabularInline):
# # 	def formfield_for_foreignkey(self, db_field, request, **kwargs):
# # 		if db_field.name == "label":
# # 			kwargs['queryset'] = Label.objects.filter(meaning_EN__contains='|')
# # 		# if db_field.name == "endMBC":
# # 		# 	kwargs['queryset'] = MBC.objects.exclude(id)
# # 		return super(OrderInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

# # 	model = Order
# # 	fk_name = "beginCombination"
# # 	# inlines = [LabelOrderInline]
# # 	fieldsets = [
# # 		('Ordered', {'fields' : ['position']} ),
# # 		('Label', {'fields' : ['label']} ),
# # 		('MBC', {'fields' : ['endMBC']} ),
# # 	]
	
# # 	readonly_fields = ['position']
# # 	ordering = ['position']
# # 	search_fields = ['label__meaning']
# # 	extra = 0


# ###############################################################################


class LabelAdmin(admin.ModelAdmin):
 	model = Label
#  	# fk_name = "order_set"
#  	fieldsets = [
# 		('Labels', {'fields' : ['meaning_EN', 'meaning_ES']} ),
# 	]
# 	list_display = ['meaning_EN', 'meaning_ES', 'was_ppLabel']

# 	# def delete_model(self, request, obj):
# 	# 	if MagicButton.objects.filter(label__id=obj.id).count() > 0: return
# 	# 	if Order.objects.filter(label__id=obj.id).count() > 0: return
# 	# 	obj.delete()




class MagicButtonAdmin(admin.ModelAdmin):
# 	def formfield_for_foreignkey(self, db_field, request, **kwargs):
# 		if db_field.name == "label":
# 			kwargs['queryset'] = Label.objects.exclude(meaning_EN__contains='|')
# 		return super(MagicButtonAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

	model = MagicButton
# 	# inlines = [LabelMBInline, ]
# 	fieldsets = [
# 		('Type',	{'fields': ['category']} ),
# 		('Information',	{'fields': ['isTemporal', 'isStep', 'description', 'icon']} ),
# 		('Label',	{'fields': ['label']} ),
# 	]

# 	search_fields = ['title']
# 	list_filter = ['isTemporal','category']
	


class MagicCombinationAdmin(admin.ModelAdmin):
  	model = MagicCombination
# 	# inlines = [OrderInline]
# 	# search_fields = ['order__label__meaning']


# 	# def has_change_permission(request,self):
# 	# 	return True

# #--------------------------------------------



admin.site.register(Label,LabelAdmin)
admin.site.register(MagicButton,MagicButtonAdmin)
admin.site.register(MagicCombination,MagicCombinationAdmin)