from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect
from canteen.models import Canteen, Dish, Menu, Conversation
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from canteen.forms import SignUpForm, menuForm, dishForm, resForm, ContactForm
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import datetime
from django.utils import timezone
import pytz
import re
import stripe
import json
from twilio.rest import Client
from django.core.mail import send_mail, BadHeaderError
from django.contrib import messages


def search(request):
    errors = []  
    username = ''
    if request.user.is_authenticated:   
        username = request.user.username
    all_canteen = Canteen.objects.all()
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            errors.append('Enter a search term.')
        elif len(q) > 20:
        	errors.append('Please enter at most 20 characters.')
        else:
            canteen = Canteen.objects.filter(name__icontains=q)
            return render(request, 'canteen/search_results.html', {'canteen': canteen, 'query': q, 'username':username})
    return render(request, 'canteen/search_form.html', {'errors': errors, 'all_canteen': all_canteen, 'username':username})

def restaurant(request, res_id):
    try:
        idx = int(res_id)
        res = Canteen.objects.get(id = idx)
    except ObjectDoesNotExist:
        raise Http404()
    return render(request, 'canteen/restaurant.html', {'res': res})

def menu(request, menu_ID):
    try:
        idx = int(menu_ID)
        menu = Menu.objects.get(id = idx)
    except ObjectDoesNotExist:
        raise Http404()
    dish_list = Dish.objects.filter(menu_id=idx)
    subtype_list = menu.get_list()
    return render(request, 'canteen/menu.html', {'canteen': menu.restaurant,'menu': menu, 'dish_list': dish_list, 'subtype': subtype_list})

def menu_mobile(request, menu_ID):
    try:
        idx = int(menu_ID)
        menu = Menu.objects.get(id = idx)
    except ObjectDoesNotExist:
        raise Http404()
    dish_list = Dish.objects.filter(menu_id=idx)
    subtype_list = menu.get_list()
    res = menu.restaurant
    return render(request, 'canteen/menu_mobile.html', {'canteen': res, 'menu': menu, 'dish_list': dish_list, 'subtype': subtype_list})

def login_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            request.session.set_expiry(86400)
            login(request, user)
        return redirect(account)
        # Redirect to a success page.
        # Return an 'invalid login' error message.
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)  
    return redirect(login_view)

def join_us(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                send_mail(name, message, from_email, ['rola.uiuc@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            messages.success(request, 'Your enquiry was sent successfully!')  
        else:
            messages.warning(request, 'Please fill the form correctly.') 
    return render(request, 'registration/join_us.html', {'form': form})

def success_view(request):
    return HttpResponse('Success! Thank you for your message.')


@login_required
def account(request):
    current_user = request.user
    user_id = current_user.id
    name = current_user.username
    user = User.objects.get(id= user_id)
    restaurant_list = Canteen.objects.filter(manager = user)
    for each in restaurant_list:
        if len(each.get_menu) == 0:
            newmenu = Menu(name = 'addnewname', info='addinfo', restaurant = each)
            newmenu.save()
    num = restaurant_list.count()
    if request.method == 'POST':
        resname = request.POST.get('resname', '')
        resnumber = request.POST.get('resnumber', '')
        resaddress = request.POST.get('resaddress', '')
        new_res = Canteen(name=resname, phone_number=resnumber, manager = user, address = resaddress)
        new_res.save()
        return redirect(account)
    data = {'restaurant_list': restaurant_list}
    return render(request, 'registration/myAccount.html', data)

@login_required
def edit_restaurant(request, res_id):
    res = Canteen.objects.get(id = res_id)
    if request.method == 'POST':
        form = menuForm(request.POST)
        if form.is_valid():
            menu = form.add_menu(user, res)
            if menu:
                menu = form.save()
        return HttpResponseRedirect("")
    else:
        form = menuForm()
    data = {'restaurant': res, 'form':form}
    return render(request, 'registration/edit_restaurant.html', data)

@login_required
def edit_res(request, res_id):
    res = Canteen.objects.get(id = res_id)
    if request.method == "POST":
        newname = request.POST.get('newname', '')
        newaddress = request.POST.get('newaddress', '')
        newphone = request.POST.get('newphone', '')
        if newname is not '':
            res.name = newname
            res.save()
            return redirect(account)
        if newaddress is not '':
            res.address = newaddress
            res.save()
            return redirect(account)
        if newphone is not '':
            res.phone_number = newphone
            res.save()
            return redirect(account)
    return redirect(account)

@login_required
def edit_menu_info(request, menu_id):
    menu = Menu.objects.get(id = menu_id)
    if request.method == "POST":
        menuName = request.POST.get('menuname', '')
        menuInfo = request.POST.get('menudes', '')
        if menuName is not '':
            menu.name = menuName
            menu.save()
            return redirect(edit_menu, menu_id= menu.id)
        if menuInfo is not '':
            menu.info = menuInfo
            menu.save()
            return redirect(edit_menu, menu_id= menu.id)
    return redirect(edit_menu, menu_id= menu.id)

@login_required
def delete_res(request,res_id =None):
    res = Canteen.objects.get(id=res_id)
    res.delete()
    return redirect(account)

@login_required
def edit_menu(request, menu_id):
    try:
        idx = int(menu_id)
        menu = Menu.objects.get(id = idx)
    except ObjectDoesNotExist:
        raise Http404()
    dish_list = Dish.objects.filter(menu=menu)
    type_list = menu.get_list()
    type_choice = []
    for each in type_list:
        type_tuple = (each, each)
        type_choice.append(type_tuple)
    dishtype_list = menu.get_list()
    data = {'canteen': menu.restaurant,'menu': menu, 'dish_list': dish_list,'dishtype_list': dishtype_list}
    return render(request, 'registration/edit_menu.html', data)

@login_required
def add_dishtype(request, menu_id):
    menu = Menu.objects.get(id = menu_id)
    dishtype_list = menu.get_list()
    if request.method=="POST":
        newtype = request.POST.get('newtype', '')
        if newtype is not '':
            dishtype_list.append(newtype)
            menu.set_list(dishtype_list)
            menu.save()
    return redirect(edit_menu, menu_id= menu.id)

@login_required
def delete_dishtype(request, menu_id, dishtype):
    menu = Menu.objects.get(id = menu_id)
    dishtype_list = menu.get_list()
    dishtype_list.remove(dishtype)
    menu.set_list(dishtype_list)
    menu.save()
    return redirect(edit_menu, menu_id= menu.id)

@login_required
def edit_dish(request, dish_id):
    dish = Dish.objects.get(id=dish_id)
    menu = dish.menu
    if request.method=="POST":
        newname = request.POST.get('newname', '')
        newprice = request.POST.get('newprice', '')
        newdes = request.POST.get('newdes', '')
        if newname is not '':
            dish.name = newname
            dish.save()
            return redirect(edit_menu, menu_id= menu.id)
        if newprice is not '':
            dish.price = newprice
            dish.save()
            return redirect(edit_menu, menu_id= menu.id)
        if newdes is not '':
            dish.description = newdes
            dish.save()
            return redirect(edit_menu, menu_id= menu.id)
    return redirect(edit_menu, menu_id= menu.id)

@login_required
def add_dish(request, menu_id):
    try:
        idx = int(menu_id)
        menu = Menu.objects.get(id = idx)
    except ObjectDoesNotExist:
        raise Http404()
    dish_list = Dish.objects.filter(menu=menu)
    type_list = menu.get_list()
    dish_num = len(dish_list) + 1
    if request.method=="POST":
        dishname = request.POST.get('dishname', '')
        dishprice = request.POST.get('dishprice', '')
        dishtype = request.POST.get('dropdown', '')
        dishdes = request.POST.get('dishdes', '')
        dish_id = Dish.objects.count() + 1
        Dish.objects.create(id = dish_id, num = dish_num, dish_type=dishtype, name=dishname, price=dishprice, menu = menu, description = dishdes, restaurant = menu.restaurant)
    return redirect(edit_menu, menu_id= menu_id)

@login_required
def delete_dish(request,dish_id =None):
    dish = Dish.objects.get(id=dish_id)
    menu = dish.menu
    menu_id = menu.id
    dish_list = Dish.objects.filter(menu = menu)
    dish_num = dish.num
    dish.delete()
    for each in dish_list:
        if each.num > dish_num:
            each.num = each.num - 1
            each.save()
    return redirect(edit_menu, menu_id= menu_id)

def payment(request, conversation_id):
    conversation = Conversation.objects.get(id = conversation_id)
    total_money = conversation.total_money * 100
    data = {'restaurant_name': conversation.restaurant, 'total_money': total_money, 'conversation': conversation_id}
    return render(request, 'canteen/payment.html', data)

@csrf_exempt
def sms(request):
    content = request.POST.get('Body', '')
    income_number = request.POST.get('From')
    restaurant_number = request.POST.get('To')
    restaurant_requested = Canteen.objects.get(phone_number=restaurant_number)

    resp = MessagingResponse()
    
    try: 
        conversation = Conversation.objects.get(customer_phoneNum = income_number)
    except:
        con_id = Conversation.objects.count() + 1
        conversation = Conversation.objects.create(id= con_id, customer_phoneNum = income_number, restaurant_phoneNum=restaurant_number, restaurant = restaurant_requested, name_address='x', last_message='x')

    order = conversation.get_order()

    menu_requested = Menu.objects.get(restaurant=restaurant_requested)
    menu_link = 'http://www.mygoodcanteen.com/menu-mobile/' + str(menu_requested.id)

    if conversation.last_message == 'x':
        mes_content = "Hi, thank you for visiting " + str(restaurant_requested.name) + ". Please text us 'd' or 'p' to inform us whether it is for delivery or pickup."
        msg = resp.message(mes_content)
        conversation.last_message = 'ask d or p'
        conversation.save()
        return HttpResponse(str(resp))

    if conversation.last_message == 'ask d or p':
        if ('d' in content) or ('D' in content):
            mes_content = "You choose delivery! Please text us your address. The format should be 'Street address, City, State Zip code', for example, '833 Bridle Avenue, San Jose, CA 95111'."
            msg = resp.message(mes_content)
            conversation.last_message = 'received d'
            conversation.save()
            return HttpResponse(str(resp))
        if ('p' in content) or ('P' in content):
            mes_content = "You choose pickup! Please text us your name for pick up:"
            msg = resp.message(mes_content)
            conversation.delivery = False
            conversation.last_message = 'received p'
            conversation.save()
            return HttpResponse(str(resp))
        mes_content = "Hi, thank you for visiting " + str(restaurant_requested.name) + ". Please text us 'd' or 'p' to inform us whether it is for delivery or pickup."
        msg = resp.message(mes_content)
        return HttpResponse(str(resp))

    if conversation.last_message in ('received d','received p'):
        conversation.name_address = content
        conversation.last_message = 'received name'
        conversation.save()
        msg = resp.message("We have received your info! Here is a link to our menu:" + menu_link + ". Please order by texting 'Add' with the dish number like 'Add 1', or clicking the button in the menu. When you are finished, just text us 'check out'.")
        return HttpResponse(str(resp))

    add_pattern = re.compile('[Aa]dd')
    if add_pattern.match(content) != None:
        p = re.compile('\d+')
        new_dish_num = int(p.findall(content)[0])
        try:
            new_dish = Dish.objects.get(num=new_dish_num, menu=menu_requested)
            conversation.total_money = conversation.total_money + new_dish.price
            order.append(new_dish.name)
            conversation.set_order(order)
            conversation.save()     
            ordered_list = ''
            for each in order:
                ordered_list += each + ', '
            ordered_list = ordered_list.strip(', ')
            mes_content = "You have successfully added it!" + " You have ordered " + ordered_list + " from " + str(conversation.restaurant) + ". Total: $" + "%.2f" % conversation.total_money + ". To remove, just type 'remove " + str(new_dish_num) + "'" 
            msg = resp.message(mes_content)
            return HttpResponse(str(resp))
        except:
            mes_content = "Please text a valid dish number!" 
            msg = resp.message(mes_content)
            return HttpResponse(str(resp))
    
    remove_pattern = re.compile('[Rr]emove')
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
        link = "http://www.mygoodcanteen.com/payment/" + str(conversation.id)
        mes_content = "Awesome, your total is " + "%.2f" % conversation.total_money + ". Please pay via this link: " + link + ' You will receive a meesage informing successful payment.'
        msg = resp.message(mes_content)
        conversation.last_message = 'checkout'
        conversation.save()
        return HttpResponse(str(resp))
        
    msg = resp.message("Here is a link to our "+ menuType + " menu:" + menu_link + ". Please order by texting 'Add' with the dish number like 'Add 1', or clicking the button in the menu. When you are finished, just text us 'check out'.")
    return HttpResponse(str(resp))

@csrf_exempt
def charge(request, conversation_id):
    stripe.api_key = "sk_test_D31hRGRmIRtbtdd7p8ZQtEtU"
    conversation = Conversation.objects.get(id = conversation_id)

    data = json.loads(request.body)
    token = data["stripeToken"]  
    email = data["email"]
    amount = int(conversation.total_money * 100)

    customer = stripe.Customer.create(
      source=token,  
      email=email,
    )

    charge = stripe.Charge.create(
      amount=amount,
      currency='usd',
      customer=customer.id,
    )

    client = Client("ACff2f802fee15e3d862ea55067969b4ce", "516a408fbb0e0dbb3c3b48cb598b8061")

    conversation.last_message = 'x'
    conversation.total_money = 0.0
    conversation.order = '[]'
    conversation.save()

    message = client.messages.create(
                                  body="You order has been submitted successfully!",
                                  from_=conversation.restaurant_phoneNum,
                                  to=conversation.customer_phoneNum
                              )

