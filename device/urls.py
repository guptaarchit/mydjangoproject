from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from . import views
app_name = 'device'

urlpatterns = [
    url(r'^$',views.index,name='index'),
    url(r'^device_details/$', views.device_details, name='device_details'),
    url(r'^device_charts/$', views.device_charts, name='device_charts'),
]
