
from django.conf.urls import url, include
from canteen import views

urlpatterns = [
    url(r'^$', views.search, name='home_view'),
    url(r'^restaurant/(?P<res_id>\d+)/$',views.restaurant, name='restaurant'),
    url(r'^menu/(?P<menu_ID>\d+)/$', views.menu, name='menu_view'),
    url(r'^menu-mobile/(?P<menu_ID>\d+)/$', views.menu_mobile),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^account/$', views.account),
    url(r'^account/edit_menu/(?P<menu_id>\d+)/$', views.edit_menu, name='edit_menu_view'),
    url(r'^delete/(?P<dish_id>\d+)/$', views.delete_dish, name='delete_dish_view'),
    url(r'^sms/$', views.sms),
    url('^', include('django.contrib.auth.urls')),
]