from django.conf.urls import patterns, url

from gui import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<slice_name>[A-Za-z0-9\-]+)/$', views.slice, name='slice'),
)