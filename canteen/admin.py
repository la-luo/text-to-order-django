from django.contrib import admin
from .models import Canteen, Dish, Menu, Conversation, Customer

class CanteenAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'address', 'phone_number')
admin.site.register(Canteen, CanteenAdmin)

class MenuAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'info', 'last_updated', 'restaurant', 'dishtype_list')
admin.site.register(Menu, MenuAdmin)

class DishAdmin(admin.ModelAdmin):
	list_display = ('id', 'num', 'dish_type', 'name', 'price', 'description', 'menu','restaurant')
admin.site.register(Dish, DishAdmin)

class ConversationAdmin(admin.ModelAdmin):
	list_display = ('id', 'delivery', 'customer_phoneNum', 'order', 'restaurant', 'total_money', 'name_address', 'last_message')
admin.site.register(Conversation, ConversationAdmin)

class CustomerAdmin(admin.ModelAdmin):
	list_display = ('id', 'phone_number', 'address')
admin.site.register(Customer, CustomerAdmin)