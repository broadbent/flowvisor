from django.conf.urls import patterns, url

from gui import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<_slice>[A-Za-z0-9\-]+)/$', views.slice, name='slice'),
    url(r'^(?P<_slice>[A-Za-z0-9\-]+)/dpid/(?P<_id>[0-9]+)/$', views.dpid, name='dpid'),
    url(r'^dpid/(?P<_id>[0-9]+)/$', views.dpid, name='dpid'),
)