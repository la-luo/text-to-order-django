from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from canteen.models import Canteen, Dish, Menu


class SignUpForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    username = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(max_length=254, help_text=_('Required. Inform a valid email address.'), widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), 
    	help_text=_("Your password must contain at least 8 characters."))
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ('username','email','password1', 'password2',)

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'password_tooshort': _("This password must contain at least 8 characters."),
    }

    def clean_password(self, user = None):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 8:
            raise forms.ValidationError(
                self.error_messages['password_tooshort'],
                code='password_tooshort',
            )
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password2"])
        if commit:
            user.save()
        return user

class resForm(forms.ModelForm):
    res_name = forms.CharField(max_length=30, required=True,  widget=forms.TextInput(attrs={'placeholder': 'Restaurant name', 'style': 'width:400px'}))
    res_number = forms.CharField(max_length=12, required=True,  widget=forms.TextInput(attrs={'placeholder': 'Restaurant number', 'style': 'width:200px'}))
    res_address = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Restaurant address', 'style': 'width:400px'}))

    class Meta:
        model = Canteen
        fields = ('res_name', 'res_number', 'res_address')

    def add_restaurant(self, user):
        res_name = self.cleaned_data['res_name']
        res_number = self.cleaned_data['res_number']
        res_address = self.cleaned_data['res_address']

        res_object = Canteen.objects.create(name=res_name, manager=user, address=res_address, phone_number=res_number)
        new_menu = Menu.objects.create(restaurant = res_object)
        
        return res_object

class menuForm(forms.ModelForm):
    menu_name = forms.CharField(max_length=30, required=True,  widget=forms.TextInput(attrs={'placeholder': 'Menu name', 'style': 'width:200px'}))
    info = forms.CharField(max_length=12, required=True,  widget=forms.TextInput(attrs={'placeholder': 'Menu description', 'style': 'width:400px'}))

    class Meta:
        model = Menu
        fields = ('menu_name', 'info')

    def add_menu(self, user, res):
        menu_name = self.cleaned_data['menu_name']
        info = self.cleaned_data['info']

        try:
            menu_object = Menu.objects.get(name=menu_name, manager=user, restaurant = res, info = info)
        except:
            menu_object = Menu.objects.create(name=menu_name, manager=user, restaurant = res, info = info)

        return menu_object


class dishForm(forms.ModelForm):

    def __init__(self, list=None, *args, **kwargs):
        super(dishForm, self).__init__(*args, **kwargs)
        self.fields["dish_type"]=forms.CharField(label="Type", widget=forms.Select(attrs={'style': 'width:100px'}, choices=list))

    subtype = (('food','food'), ('drinks','drinks'))

    dish_name = forms.CharField(max_length=100, required=True,  widget=forms.TextInput(attrs={'placeholder': 'Dish name', 'style': 'width:400px'}))
    dish_price = forms.FloatField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Dish price', 'style': 'width:400px'}))
    dish_type = forms.CharField(required=True, label="Type", widget=forms.Select(attrs={'style': 'width:100px'}, choices=subtype))

    class Meta: 
        model = Dish
        fields = ('dish_type', 'dish_name', 'dish_price',)

    def add_dish(self, menu):
        dish_name = self['dish_name']
        dish_price = self['dish_price']
        dish_type = self['dish_type']
        dish_num = len(menu.get_dish) + 1
        restaurant = menu.restaurant

        dish_object = Dish.objects.create(num=dish_num, name=dish_name, price=dish_price, menu=menu, restaurant=restaurant)

        return dish_object

        # dish_name = self.cleaned_data['dish_name']
        # dish_price = self.cleaned_data['dish_price']
        # dish_type = self.cleaned_data['dish_type']

        # try:
        #     dish_object = Dish.objects.get(dish_type=dish_type, num=dish_num, name=dish_name, price=dish_price, menu=menu, restaurant=restaurant)
        # except:
        #     dish_object = Dish.objects.create(dish_type=dish_type, num=dish_num, name=dish_name, price=dish_price, menu=menu, restaurant=restaurant)
