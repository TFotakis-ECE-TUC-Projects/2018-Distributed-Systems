from django.db import models


class User(models.Model):
	Name = models.CharField(max_length=100)
	Surname = models.CharField(max_length=100)
	Username = models.CharField(max_length=100)
	Email = models.CharField(max_length=100)

	@property
	def FullName(self): return self.Name + ' ' + self.Surname

	def __str__(self): return self.FullName


class Friendship(models.Model):
	User = models.ForeignKey('User', on_delete=models.CASCADE, default=1, related_name='User')
	Friend = models.ForeignKey('User', on_delete=models.CASCADE, default=1, related_name='Friend')

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


class PhotoComment(models.Model):
	User = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
	Photo = models.ForeignKey(Photo, on_delete=models.CASCADE, default=1)
	UploadDateTime = models.DateTimeField(auto_now_add=True, null=True)
	Text = models.CharField(max_length=1024)

	def __str__(self): return str(self.Photo) + " - " + str(self.UploadDateTime)


class Like(models.Model):
	User = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
	Photo = models.ForeignKey(Photo, on_delete=models.CASCADE, default=1)
