from django.urls import path

from . import views

urlpatterns = [
	path('', views.homeView, name='home'),
	path('profile/<int:id>/', views.profileView, name='profile'),
	path('gallery/<int:id>/', views.galleryView, name='gallery'),
	path('uploadPhoto/<int:ownerId>/', views.uploadPhotoView, name='uploadPhoto'),
	path('listOfUsers/', views.listOfUsers, name='listOfUsers'),
	# path('status/', views.statusView, name='status'),
]
