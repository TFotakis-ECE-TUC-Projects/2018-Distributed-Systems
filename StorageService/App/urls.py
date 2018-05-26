from django.urls import path

from . import views

urlpatterns = [
	path('status/', views.statusView, name='status'),
	path('status/<str:node>/', views.nodeStatusView, name='nodeStatus'),
	path('getImage/<str:filename>/', views.getImage, name='getImage'),
]
