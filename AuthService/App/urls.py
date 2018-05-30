from django.urls import path

from . import views

urlpatterns = [
	path('login', views.loginView, name='login'),
	path('register', views.registerView, name='register'),
	path('authService/', views.authService, name='authSevice'),
	path('webService/', views.webService, name='webService'),
]
