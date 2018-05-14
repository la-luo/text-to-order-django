
from django.conf.urls import url, include
from canteen import views

urlpatterns = [
    url(r'^$', views.search, name='home_view'),
    url(r'^restaurant/(?P<res_id>\d+)/$',views.restaurant, name='restaurant'),
    url(r'^menu/(?P<menu_ID>\d+)/$', views.menu, name='menu_view'),
    url(r'^menu-mobile/(?P<menu_ID>\d+)/$', views.menu_mobile),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^account/$', views.account, name='account'),
    url(r'^edit-res/(?P<res_id>\d+)/$', views.edit_res, name='edit_res'),
    url(r'^account/edit_menu/(?P<menu_id>\d+)/$', views.edit_menu, name='edit_menu_view'),
    url(r'^add-dishtype/(?P<menu_id>\d+)/$', views.add_dishtype, name='add_dishtype'),
    url(r'^delete-dishtype/(?P<menu_id>\d+)/(?P<dishtype>\w+)/$', views.delete_dishtype, name='delete_dishtype'),
    url(r'^edit-dish/(?P<dish_id>\d+)/$', views.edit_dish, name='edit_dish'),
    url(r'^delete/(?P<dish_id>\d+)/$', views.delete_dish, name='delete_dish_view'),
    url(r'^payment/(?P<conversation_id>\d+)/$', views.payment),
    url(r'^check/$', views.check),
    url(r'^sms/$', views.sms),
    url(r'^charge/$', views.charge),
    url('^', include('django.contrib.auth.urls')),
]