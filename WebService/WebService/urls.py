from django.contrib import admin
from django.urls import path, include

from WebService.zoo import zk

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include(('App.urls', 'App'), namespace='App')),
	path('api/', include(('RestAPI.urls', 'RestAPI'), namespace='RestAPI')),
]
zk.initialize()
