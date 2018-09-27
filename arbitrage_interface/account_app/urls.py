from django.conf.urls import url
from django.contrib.auth import views as auth_views
from main_app import views as arb_views

urlpatterns = [
    url(r'^$', arb_views.index),
    url(r'^profile/$', arb_views.index, name='home'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
]
