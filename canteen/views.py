from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect
from canteen.models import Canteen, Dish, Menu, Conversation
from django.contrib.auth import authenticate, login
from canteen.forms import SignUpForm, menuForm
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from django.conf import settings


def search(request):
    errors = []
    all_canteen = Canteen.objects.all()
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            errors.append('Enter a search term.')
        elif len(q) > 20:
        	errors.append('Please enter at most 20 characters.')
        else:
            canteen = Canteen.objects.filter(name__icontains=q)
            return render(request, 'canteen/search_results.html', {'canteen': canteen, 'query': q})
    return render(request, 'canteen/search_form.html', {'errors': errors, 'all_canteen': all_canteen})

def restaurant(request, res_id):
    try:
        idx = int(res_id)
        res = Canteen.objects.get(id = idx)
    except ValueError:
        raise Http404()
    return render(request, 'canteen/restaurant.html', {'res': res})

def menu(request, menu_ID):
    try:
        idx = int(menu_ID)
        menu = Menu.objects.get(id = idx)
    except ValueError:
        raise Http404()
    dish_list = Dish.objects.filter(menu_id=idx)
    return render(request, 'canteen/menu.html', {'canteen': menu.restaurant,'menu': menu, 'dish_list': dish_list})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            valid_password = form.clean_password()
            user = authenticate(username=username, password=valid_password)
            if user:
                user = form.save()
                user.groups.add(Group.objects.get(name='restaurant manager'))
            login(request, user)
            return redirect(account)
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def account(request):
    current_user = request.user
    user_id = current_user.id
    name = current_user.username
    user = User.objects.get(id= user_id)
    restaurant_list = Canteen.objects.filter(manager = user)
    menu_list = []
    num = restaurant_list.count()
    for each in restaurant_list:
        menu = Menu.objects.filter(restaurant = each)
        menu_list.append(menu)
    #data = {'restaurant_list': restaurant_list, 'menu_list': menu_list}
    data = {'restaurant_list': restaurant_list}

    return render(request, 'registration/myAccount.html', data)

def edit_menu(request, menu_id):
    try:
        idx = int(menu_id)
        menu = Menu.objects.get(id = idx)
    except ValueError:
        raise Http404()
    dish_list = Dish.objects.filter(menu=menu)
    if request.method == 'POST':
        form = menuForm(request.POST)
        if form.is_valid():
            dish = form.add_dish(menu)
            if dish:
                dish = form.save()
        return HttpResponseRedirect("")
    else:
        form = menuForm()
    data = {'canteen': menu.restaurant,'menu': menu, 'dish_list': dish_list, 'form': form}
    return render(request, 'registration/edit_menu.html', data)

def delete_dish(request,dish_id =None):
    dish = Dish.objects.get(id=dish_id)
    dish.delete()
    menu = dish.menu
    menu_id = menu.id
    return redirect(edit_menu, menu_id= menu_id)

@csrf_exempt
def sms(request):
    content = request.POST.get('Body', '')
    income_number = request.POST.get('From')
    restaurant_number = request.POST.get('To')
    restaurant_requested = Canteen.objects.get(phone_number=restaurant_number)

    try: 
        conversation = Conversation.objects.get(customer_phoneNum = income_number, restaurant_phoneNum=restaurant_number)
    except:
        conversation = Conversation.objects.create(customer_phoneNum = income_number, restaurant_phoneNum=restaurant_number, restaurant = restaurant_requested)

    resp = MessagingResponse()

    order = conversation.get_order()

    if 'add' in content and '#' in content:
        new_dish_num = int(content[-1])
        new_dish = Dish.objects.get(id = new_dish_num)
        conversation.total_money = conversation.total_money + new_dish.price
        order.append(new_dish.name)
        conversation.set_order(order)
        conversation.save()     # database would not be updated with .save()!
        mes_content = "You have successfully added it!" + " You have ordered " + str(order) + " from " + str(conversation.restaurant) + ". Total: $" + str(conversation.total_money)
        msg = resp.message(mes_content)
        return HttpResponse(str(resp))
    
    if 'remove' in content and '#' in content:
        new_dish_num = int(content[-1])
        new_dish = Dish.objects.get(id = new_dish_num)
        conversation.total_money = conversation.total_money - new_dish.price
        order.remove(new_dish.name)
        conversation.set_order(order)
        conversation.save()
        mes_content = "You have successfully removed it!" + " You have ordered " + str(order) + " from " + str(conversation.restaurant) + ". Total: $" + str(conversation.total_money)
        msg = resp.message(mes_content)
        return HttpResponse(str(resp))

    if 'check out' in content:
        mes_content = "Awesome, your total is " + str(conversation.total_money) + ". Please pay via this link:+link" 
        msg = resp.message(mes_content)
        conversation.last_message = 'check out'
        conversation.save()
        return HttpResponse(str(resp))

    if conversation.last_message == 'check out':
        conversation.delete()

    res_menu_link = 'https://mygoodcanteen/restaurant/' + str(restaurant_requested.id)
    msg = resp.message("Hi, thank you for texting " + str(restaurant_requested.name) + ". Here is a link to our menu: " + res_menu_link + ". Please order by texting back the orders you want, like 'add #1'. When you are finished, just text us 'check out'.")
    return HttpResponse(str(resp))

