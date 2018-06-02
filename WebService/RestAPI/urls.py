from django.urls import path

from . import views

urlpatterns = [
	path('status/', views.statusView, name='status'),
	path('status/<str:node>/', views.nodeStatusView, name='nodeStatus'),
	path('addComment/<int:photoId>', views.addComment, name='addComment'),
	path('deleteComment/<int:commentId>/', views.deleteComment, name='deleteComment'),
	path('uploadPhoto/', views.uploadPhoto, name='uploadPhoto'),
	path('makeFriendship/<int:userId>/<int:friendId>/', views.makeFriendship, name='makeFriendship'),
	path('deleteFriendship/<int:userId>/<int:friendId>/', views.deleteFriendship, name='deleteFriendship'),
	path('login', views.loginExternal, name='login'),
]
