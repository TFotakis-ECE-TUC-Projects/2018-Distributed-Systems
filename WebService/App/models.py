import json
import requests
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from WebService.zoo import zk


class Profile(models.Model):
	User = models.OneToOneField(User, on_delete=models.CASCADE)
	AuthService = models.CharField(max_length=100, blank=True, default='')
	AuthServiceUserId = models.PositiveIntegerField(blank=True, default=1)
	PhotoUUID = models.CharField(max_length=1024, blank=True, default='')

	@property
	def FullName(self): return self.User.first_name + ' ' + self.User.last_name

	def __str__(self): return self.FullName

	@property
	def photoUrl(self):
		try:
			requestUrl = zk.applicationService + 'getStorageService/' + self.PhotoUUID + '/'
			response = requests.get(requestUrl)
			content = json.loads(response.content)
			return content['storageService'] + 'getImage/' + self.PhotoUUID + '/'
		except Exception:
			return ""


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(User=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()


class Friendship(models.Model):
	User = models.ForeignKey('auth.User', default=1, on_delete=models.CASCADE, related_name='User')
	Friend = models.ForeignKey('auth.User', default=1, on_delete=models.CASCADE, related_name='Friend')

	def __str__(self): return str(self.User) + " -> " + str(self.Friend)


class Gallery(models.Model):
	Owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
	Name = models.CharField(max_length=100)

	def __str__(self): return str(self.Name) + " - " + str(self.Owner)


class GalleryComment(models.Model):
	User = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
	Gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, default=1)
	UploadDateTime = models.DateTimeField(default=None, null=True)
	Text = models.CharField(max_length=1024)

	def __str__(self): return str(self.Gallery) + " - " + str(self.UploadDateTime)


class Photo(models.Model):
	Gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, default=1)
	UploadDateTime = models.DateTimeField(auto_now_add=True, null=True)
	UUID = models.CharField(max_length=1024)
	Location = models.CharField(default='', blank=True, null=True, max_length=100)
	Description = models.CharField(default='', blank=True, null=True, max_length=1024)

	def __str__(self): return str(self.Gallery) + " - " + self.UUID

	@property
	def url(self):
		try:
			requestUrl = zk.applicationService + 'getStorageService/' + self.UUID + '/'
			response = requests.get(requestUrl)
			content = json.loads(response.content)
			return content['storageService'] + 'getImage/' + self.UUID + '/'
		except Exception:
			return ""


class PhotoComment(models.Model):
	User = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
	Photo = models.ForeignKey(Photo, on_delete=models.CASCADE, default=1)
	UploadDateTime = models.DateTimeField(auto_now_add=True, null=True)
	Text = models.CharField(max_length=1024)

	def __str__(self): return str(self.Photo) + " - " + str(self.UploadDateTime)


class Like(models.Model):
	User = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
	Photo = models.ForeignKey(Photo, on_delete=models.CASCADE, default=1)
