from django.contrib import admin

from .models import User, Friendship, Gallery, GalleryComment, Photo, PhotoComment, Like

admin.site.register([
	User,
	Friendship,
	Gallery,
	GalleryComment,
	Photo,
	PhotoComment,
	Like,
])
