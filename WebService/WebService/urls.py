from django.contrib import admin
from django.urls import path, include

# Used to initialize ZooKeeper Connections
# noinspection PyUnresolvedReferences
from WebService.zoo import zk

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include(('App.urls', 'App'), namespace='App')),
	path('api/', include(('RestAPI.urls', 'RestAPI'), namespace='RestAPI')),
]
