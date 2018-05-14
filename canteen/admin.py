from django.contrib import admin
from .models import Canteen, Dish, Menu, Conversation

class CanteenAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'address', 'phone_number')

# Register your models here.
admin.site.register(Canteen, CanteenAdmin)
admin.site.register(Menu)
admin.site.register(Dish)
admin.site.register(Conversation)