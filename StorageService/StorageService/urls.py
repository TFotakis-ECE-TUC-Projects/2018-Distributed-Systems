from django.contrib import admin
from django.urls import path, include

from .zoo import zk

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include(('App.urls', 'App'), namespace='App'))
]
zk.initialize()
