from django.contrib import admin

from .models import Profile, Friendship, Gallery, GalleryComment, Photo, PhotoComment, Like

admin.site.register([
	Profile,
	Friendship,
	Gallery,
	GalleryComment,
	Photo,
	PhotoComment,
	Like,
])
