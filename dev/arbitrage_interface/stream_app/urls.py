from django.conf.urls import url
from stream_app import views

urlpatterns = [
    url(r'^$', views.stream, name='stream'),
]
