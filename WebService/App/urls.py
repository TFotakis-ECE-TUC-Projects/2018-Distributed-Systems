from django.urls import path

from . import views

urlpatterns = [
	path('', views.homeView, name='home'),
	path('dynamicHome', views.dynamicHomeView, name='dynamicHome'),
	path('profile/<int:id>/', views.profileView, name='profile'),
	path('myProfile/', views.myProfileView, name='myProfile'),
	path('gallery/<int:id>/', views.galleryView, name='gallery'),
	path('uploadPhoto/', views.uploadPhotoView, name='uploadPhoto'),
	path('uploadProfilePhoto/', views.uploadProfilePhotoView, name='uploadProfilePhoto'),
	path('listOfUsers/', views.listOfUsers, name='listOfUsers'),
	path('login/', views.loginView, name='login'),
	path('register/', views.registerView, name='register'),
	path('logout/', views.logoutView, name='logout'),
	path('createGallery/', views.createGallery, name='createGallery'),
]
