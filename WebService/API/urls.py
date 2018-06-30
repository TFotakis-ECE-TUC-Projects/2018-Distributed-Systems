from django.urls import path

from . import views

urlpatterns = [
	path('status/', views.statusView, name='status'),
	path('status/<str:node>/', views.nodeStatusView, name='nodeStatus'),
	path('addComment/<int:photoId>', views.addComment, name='addComment'),
	path('addGalleryComment/<int:galleryId>', views.addGalleryComment, name='addGalleryComment'),
	path('deleteComment/<int:commentId>/', views.deleteComment, name='deleteComment'),
	path('uploadPhoto/', views.uploadPhoto, name='uploadPhoto'),
	path('uploadProfilePhoto/', views.uploadProfilePhoto, name='uploadProfilePhoto'),
	path('makeFriendship/<int:friendId>/', views.makeFriendship, name='makeFriendship'),
	path('deleteFriendship/<int:friendId>/', views.deleteFriendship, name='deleteFriendship'),
	path('login', views.loginExternal, name='login'),
	path('register', views.registerExternal, name='register'),
	path('likePhoto/<int:photoId>/', views.likePhoto, name='likePhoto'),
	path('deletePhoto', views.deletePhoto, name='deletePhoto'),
	path('deleteGallery/<int:galleryId>/', views.deleteGallery, name='deleteGallery'),
	path('profile', views.profile, name='profile'),
	path('gallery', views.gallery, name='gallery'),
	path('homeFeed', views.homeFeed, name='homeFeed'),
	path('galleryFeed', views.galleryFeed, name='galleryFeed'),
]
