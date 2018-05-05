from django.urls import path

from . import views

urlpatterns = [
	path('', views.homeView, name='home'),
	# path('status/', views.statusView, name='status'),
]
