from django.conf.urls import url
from django.contrib import admin
from discogsApp import views

urlpatterns = [
	url(r'^$', views.index, name='home'),
	url(r'^find_artist/$', views.find_artist, name='find_artist'),
    url(r'^find_alias/$', views.find_alias, name='find_alias'),
    url(r'^confirm_alias/$', views.confirm_alias, name='confirm_alias'),
    url(r'^admin/', admin.site.urls),
]
