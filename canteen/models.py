from django.db import models
from django.contrib.auth.models import User
import json

class Canteen(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    manager = models.ForeignKey(User, related_name='manager', null=True)
    address = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=12, null=True)

    def __str__(self):
    	return self.name

    @property
    def get_menu(self):
        menu_list = Menu.objects.filter(restaurant=self)
        return menu_list

    class Meta:
    	ordering = ['name']

class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    info = models.CharField(max_length = 200, null=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    restaurant = models.ForeignKey(Canteen, null=True)
    dishtype_list = models.CharField(max_length=200, default='["food","drinks"]')

    def __str__(self):
        return self.name

    def set_list(self, updated_list):
        self.dishtype_list = json.dumps(updated_list)

    def get_list(self):
        return json.loads(self.dishtype_list)

    @property
    def get_dish(self):
        dish_list = Dish.objects.filter(menu = self)
        return dish_list

class Dish(models.Model):
    id = models.AutoField(primary_key=True)
    num = models.IntegerField(null=True)
    dish_type = models.CharField(max_length=20, default='food')
    name = models.CharField(max_length=100)
    price = models.FloatField(null=True)
    description = models.CharField(max_length=100, default='Add description for this dish')
    menu = models.ForeignKey(Menu, null=True)
    restaurant = models.ForeignKey(Canteen, null=True)

    def __str__(self):
    	return self.name

    class Meta:
        ordering = ['id']

class Conversation(models.Model):
    id = models.AutoField(primary_key=True)
    delivery = models.BooleanField(default=True)
    customer_phoneNum = models.CharField(max_length=15, null=True)
    restaurant_phoneNum = models.CharField(max_length=15, null=True)
    order = models.CharField(max_length=200,  default='[]')
    restaurant = models.ForeignKey(Canteen, null=True)
    total_money = models.FloatField(default = 0.0)
    name_address = models.CharField(max_length=50, default='')
    last_message = models.CharField(max_length=30, default='')

    def set_order(self, updated_order):
        self.order = json.dumps(updated_order)

    def get_order(self):
        return json.loads(self.order)

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=200, default='')

