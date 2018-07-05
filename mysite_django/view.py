from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect
import datetime
from mysite_django.forms import ContactForm
from django.core.mail import send_mail, get_connection
# test server side user email 
# change server side user name

def hello(request): 
    return HttpResponse("Hello world") 

def my_home_view(request):
	return HttpResponse("My home page")

def current_datetime(request):
    now = datetime.datetime.now()
    return render(request, 'current_datetime.html', {'current_date': now})

def hours_ahead(request, offset):
    try:
        offset = int(offset)
    except ValueError:
        raise Http404()
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    html = "<html><body>In %s hour(s), it will be  %s.</body></html>" % (offset, dt)
    return HttpResponse(html)

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_date
            con = get_connection('django.core.mail.backends.console.EmailBackend')
            send_mail(
                cd['subject'], 
                cd['message'], 
                cd.get('email', 'rola.uiuc@gmail.com'), 
                ['siteowner@example.com'], 
                connection = con
                )
            return HttpResponseRedirct('/contact/thanks/')
    else:
        form = ContactForm()

    return render(request, 'contact_form.html', {'form': form})

