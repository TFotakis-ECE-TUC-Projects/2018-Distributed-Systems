from django.db import models


class Photo(models.Model):
	UUID = models.CharField(max_length=1024)
	StorageService = models.CharField(max_length=100)

	def __str__(self): return self.UUID + ' - ' + self.StorageService
