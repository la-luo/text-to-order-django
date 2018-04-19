from django.db import models
from django.contrib.auth.models import User
import json

class Canteen(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    manager = models.ManyToManyField(User, related_name='manager')
    address = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=12, null=True)
    nums_stars = models.IntegerField()

    def __str__(self):
    	return self.name

    @property
    def get_menu(self):
        menu_list = Menu.objects.filter(restaurant = self)
        return menu_list

    class Meta:
    	ordering = ['-nums_stars']

class Menu(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    info = models.CharField(max_length = 200)
    last_updated = models.DateTimeField(auto_now_add=True)
    restaurant = models.ForeignKey(Canteen)
    menu_type = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.name

    @property
    def get_dish(self):
        dish_list = Dish.objects.filter(menu = self)
        return dish_list

class Dish(models.Model):
    id = models.IntegerField(primary_key=True)
    num = models.CharField(max_length=10, null=True)
    name = models.CharField(max_length=100)
    price = models.FloatField(null=True)
    menu = models.ForeignKey(Menu, null=True)
    restaurant = models.ForeignKey(Canteen, null=True)
    nums_stars = models.IntegerField(null=True, blank=True)

    def __str__(self):
    	return self.name

    class Meta:
        ordering = ['id']

class Conversation(models.Model):
    id = models.IntegerField(primary_key=True)
    customer_phoneNum = models.CharField(max_length=15)
    restaurant_phoneNum = models.CharField(max_length=15, null=True)
    order = models.CharField(max_length=200,  default='[]')
    restaurant = models.ForeignKey(Canteen, null=True)
    total_money = models.FloatField(default = 0.0)
    street_address = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=20, null=True)
    State = models.CharField(max_length=15, null=True)
    last_message = models.CharField(max_length=30, null=True)


    def set_order(self, updated_order):
        self.order = json.dumps(updated_order)

    def get_order(self):
        return json.loads(self.order)
