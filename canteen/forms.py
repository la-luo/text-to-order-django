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

    username = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'size':'30', 'class':'inputText'}))
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.', widget=forms.TextInput(attrs={'size':'30', 'class':'inputText'}))
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.', widget=forms.TextInput(attrs={'size':'30', 'class':'inputText'}))
    email = forms.EmailField(max_length=254, help_text=_('Required. Inform a valid email address.'), widget=forms.TextInput(attrs={'size':'30', 'class':'inputText'}))
    phone_numbner = forms.CharField(max_length=12, required=True)
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, 
    	help_text=_("Your password must contain at least 8 characters."))
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email','phone_numbner', 'password1', 'password2', )

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


class menuForm(forms.ModelForm):
    dish_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'size':'30', 'class':'inputText'}))
    dish_number = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'size':'30', 'class':'inputText'}))
    dish_price = forms.FloatField(required=True, widget=forms.TextInput(attrs={'size':'30', 'class':'inputText'}))

    class Meta:
        model = Dish
        fields = ('dish_number', 'dish_name', 'dish_price',)

    def add_dish(self, menu):
        dish_number = self.cleaned_data['dish_number']
        dish_name = self.cleaned_data['dish_name']
        dish_price = self.cleaned_data['dish_price']

        try:
            dish_object = Dish.objects.get(name=dish_name, price=dish_price, num=dish_number, menu=menu, restaurant=menu.restaurant)
        except:
            dish_object = Dish.objects.create(name=dish_name, price=dish_price, menu=menu, num=dish_number, restaurant=menu.restaurant)

        return dish_object


