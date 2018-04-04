from django.urls import path

from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('messageView/', views.messageView, name='messageView'),
	path('setMessage/<str:givenMessage>', views.setMessage, name='setMessage'),
]