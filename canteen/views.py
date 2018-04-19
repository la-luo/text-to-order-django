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
import datetime
from django.utils import timezone
import pytz
import re

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

def menu_mobile(request, menu_ID):
    try:
        idx = int(menu_ID)
        menu = Menu.objects.get(id = idx)
    except ValueError:
        raise Http404()
    dish_list = Dish.objects.filter(menu_id=idx)
    return render(request, 'canteen/menu_mobile.html', {'canteen': menu.restaurant,'menu': menu, 'dish_list': dish_list})

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

def payment(request, conversation_id):
    conversation = Conversation.objects.get(id = conversation_id)
    total_money = conversation.total_money * 100
    data = {'restaurant_name': conversation.restaurant, 'total_money': total_money}
    return render(request, 'canteen/payment.html', data)

@csrf_exempt
def sms(request):
    content = request.POST.get('Body', '')
    income_number = request.POST.get('From')
    restaurant_number = request.POST.get('To')
    restaurant_requested = Canteen.objects.get(phone_number=restaurant_number)
    now = timezone.now() - datetime.timedelta(hours=7)
    border = now.replace(hour=2, minute=0, second=0, microsecond=0)

    try: 
        conversation = Conversation.objects.get(customer_phoneNum = income_number, restaurant_phoneNum=restaurant_number)
    except:
        conversation = Conversation.objects.create(customer_phoneNum = income_number, restaurant_phoneNum=restaurant_number, restaurant = restaurant_requested)

    resp = MessagingResponse()

    order = conversation.get_order()

    if now < border:
        menuType = 'noon'
    else:
        menuType = 'dinner'
    menu_requested = Menu.objects.get(menu_type = menuType, restaurant=restaurant_requested)

    add_pattern = re.compile('[Aa]dd(\s)#')

    if add_pattern.match(content) != None:
        p = re.compile('\d+')
        new_dish_num = int(p.findall(content)[0])
        try:
            new_dish = Dish.objects.get(num=new_dish_num, menu=menu_requested)
            conversation.total_money = conversation.total_money + new_dish.price
            order.append(new_dish.name)
            conversation.set_order(order)
            conversation.save()     # database would not be updated with .save()!
            ordered_list = ''
            for each in order:
                ordered_list += each + ', '
            ordered_list = ordered_list.strip(', ')
            mes_content = "You have successfully added it!" + " You have ordered " + ordered_list + " from " + str(conversation.restaurant) + ". Total: $" + "%.2f" % conversation.total_money + ". To remove, just type 'remove #" + str(new_dish_num) + "'" 
            msg = resp.message(mes_content)
            return HttpResponse(str(resp))
        except:
            mes_content = "Please text a valid dish number!" 
            msg = resp.message(mes_content)
            return HttpResponse(str(resp))
    
    remove_pattern = re.compile('[Rr]emove(\s)#')
    if remove_pattern.match(content) != None:
        p = re.compile('\d+')
        new_dish_num = int(p.findall(content)[0])
        try:
            new_dish = Dish.objects.get(num=new_dish_num, menu=menu_requested)
            conversation.total_money = conversation.total_money - new_dish.price
            order.remove(new_dish.name)
            conversation.set_order(order)
            conversation.save()
            ordered_list = ''
            for each in order:
                ordered_list += each + ', '
            ordered_list = ordered_list.strip(', ')
            mes_content = "You have successfully removed it!" + " You have ordered " + ordered_list + " from " + str(conversation.restaurant) + ". Total: $" + "%.2f" % conversation.total_money
            msg = resp.message(mes_content)
            return HttpResponse(str(resp))
        except:
            mes_content = "Please text a valid dish number!" 
            msg = resp.message(mes_content)
            return HttpResponse(str(resp))

    check_pattern = re.compile('[Cc]heck')
    if check_pattern.match(content) != None:
        link = "http://167.99.161.247:8000/payment/" + str(conversation.id)
        mes_content = "Awesome, your total is " + "%.2f" % conversation.total_money + ". Please pay via this link: " + link + ' Type anything to inform us when you finish.'
        msg = resp.message(mes_content)
        conversation.last_message = 'check out'
        conversation.save()
        return HttpResponse(str(resp))

    if conversation.last_message == 'check out':
        mes_content = "Thank you for paying, please give us your address for delivery. What is your street address:"
        msg = resp.message(mes_content)
        conversation.last_message = 'street address received'
        conversation.save()
        return HttpResponse(str(resp))

    if conversation.last_message == 'street address received':
        mes_content = "What is your city:"
        msg = resp.message(mes_content)
        conversation.last_message = 'city received'
        conversation.save()
        return HttpResponse(str(resp))

    if conversation.last_message == 'city received':
        mes_content = "What is your state:"
        msg = resp.message(mes_content)
        conversation.last_message = 'state received'
        conversation.save()
        return HttpResponse(str(resp))

    if conversation.last_message == 'state received':
        mes_content = "Thank you, your delivery order is submitted"
        msg = resp.message(mes_content)
        conversation.delete()
        return HttpResponse(str(resp))
        
    menu_link = 'http://167.99.161.247:8000/menu-mobile/' + str(menu_requested.id)
    msg = resp.message("Hi, thank you for texting " + str(restaurant_requested.name) + ". Here is a link to our "+ menuType + " menu:" + menu_link + ". Please order by texting back the orders you want, like 'add #1'. When you are finished, just text us 'check out'.")
    return HttpResponse(str(resp))

