import json
import requests
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from WebService.cryptography import cr
from WebService.zoo import zk


class Gallery(models.Model):
	Owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
	Name = models.CharField(max_length=100)

	def __str__(self): return str(self.Name) + " - " + str(self.Owner)


class Photo(models.Model):
	Gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, default=1, null=True, blank=True)
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
			content = json.loads(response.text)
			try:
				username = self.Gallery.Owner.username
			except Exception:
				username = ""
			sharedKeyBase64 = ''
			for storageService in zk.storageServicesList:
				if storageService['url'] == content['storageService']:
					sharedKeyBase64 = storageService['sharedKey']
					break
			hmac = cr.defaultEncrypt(inputData=self.UUID + username, sharedKeyBase64=sharedKeyBase64)['data']
			url = content['storageService'] + 'getImage?uuid=' + self.UUID + '&username=' + username + '&hmac=' + hmac
			return url
		except Exception:
			return ""


class Profile(models.Model):
	User = models.OneToOneField(User, on_delete=models.CASCADE)
	AuthService = models.CharField(max_length=100, blank=True, default='')
	AuthServiceUserId = models.PositiveIntegerField(blank=True, default=1)
	ProfilePhoto = models.ForeignKey(Photo, on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)

	@property
	def FullName(self): return self.User.first_name + ' ' + self.User.last_name

	def __str__(self): return self.FullName

	@property
	def photoUrl(self):
		try:
			requestUrl = zk.applicationService + 'getStorageService/' + self.PhotoUUID + '/'
			response = requests.get(requestUrl)
			content = json.loads(response.text)
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


class GalleryComment(models.Model):
	User = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
	Gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, default=1)
	UploadDateTime = models.DateTimeField(default=None, null=True)
	Text = models.CharField(max_length=1024)

	def __str__(self): return str(self.Gallery) + " - " + str(self.UploadDateTime)


class PhotoComment(models.Model):
	User = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
	Photo = models.ForeignKey(Photo, on_delete=models.CASCADE, default=1)
	UploadDateTime = models.DateTimeField(auto_now_add=True, null=True)
	Text = models.CharField(max_length=1024)

	def __str__(self): return str(self.Photo) + " - " + str(self.UploadDateTime)


class Like(models.Model):
	User = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
	Photo = models.ForeignKey(Photo, on_delete=models.CASCADE, default=1)
