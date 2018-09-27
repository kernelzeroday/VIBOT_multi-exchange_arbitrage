from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^start/$', views.start, name="start"),
    url(r'^stop/$', views.stop, name="stop"),
    url(r'^pause/$', views.pause, name="pause"),
    url(r'^update_config/$', views.update_config, name="update_config"),
    # url(r'^$', views.accounts, name="accounts"),
    # url(r'^(?P<ex_acc_id>[0-9]+)/delete/$', views.delete, name="delete"),
    # url(r'^add/$', views.add, name="add"),
]
