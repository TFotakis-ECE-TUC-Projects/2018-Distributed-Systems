from django.urls import path

from . import views

urlpatterns = [
	path('status/', views.statusView, name='status'),
	path('status/<str:node>/', views.nodeStatusView, name='nodeStatus'),
	path('addComment/<int:photoId>', views.addComment, name='addComment'),
	path('deleteComment/<int:commentId>/', views.deleteComment, name='deleteComment'),
	path('uploadPhoto/', views.uploadPhoto, name='uploadPhoto'),
]
