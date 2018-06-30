import json
import pytz
import requests
from datetime import datetime
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.timezone import localtime

from App import views as AppViews
from App.models import Friendship, Photo, PhotoComment, Profile, Like, GalleryComment, Gallery
from WebService import settings
from WebService.cryptography import cr
from WebService.zoo import zk

LOGIN_URL = 'login?system=' + settings.ZOOKEEPER_NODE_ID + '&callback=' + settings.SERVER_HOSTNAME + ':' + settings.SERVER_PORT + '/'


def statusView(request):
	return JsonResponse(zk.getStatus())


def nodeStatusView(request, node):
	return JsonResponse(zk.getNodeData(node))


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def addComment(request, photoId):
	comment = PhotoComment.objects.create(User_id=request.user.id, Photo_id=photoId, Text=request.GET['comment'])
	context = {
		'id': comment.id,
		'userId': comment.User_id,
		'userFullName': comment.User.get_full_name(),
		'photoId': comment.Photo_id,
		'text': comment.Text
	}
	return JsonResponse(context)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def addGalleryComment(request, galleryId):
	GalleryComment.objects.create(User_id=request.user.id, Gallery_id=galleryId, Text=request.GET['comment'])
	referer = request.META.get('HTTP_REFERER')
	return HttpResponseRedirect(referer)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def deleteComment(request, commentId):
	PhotoComment.objects.get(id=commentId).delete()
	return HttpResponse(status=200)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def updateComment(request, commentId):
	PhotoComment.objects.filter(id=commentId).update(Text=request.GET['comment'])
	referer = request.META.get('HTTP_REFERER')
	return HttpResponseRedirect(referer)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def uploadPhoto(request):
	galleryId = request.POST['galleryId']
	description = request.POST['Description']
	location = request.POST['Location']
	photoFile = request.FILES['photoFile']

	requestUrl = zk.applicationService + 'uploadPhoto/'
	response = requests.post(requestUrl, files={'photoFile': photoFile})

	if response.ok:
		UUID = json.loads(response.text)['UUID']
		Photo.objects.create(Gallery_id=galleryId, UUID=UUID, Description=description, Location=location)
		return redirect('App:gallery', id=galleryId)
	return redirect('App:uploadPhoto')


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def uploadProfilePhoto(request):
	galleryId = None
	description = None
	location = None
	photoFile = request.FILES['photoFile']

	requestUrl = zk.applicationService + 'uploadPhoto/'
	response = requests.post(requestUrl, files={'photoFile': photoFile})

	if response.ok:
		UUID = json.loads(response.text)['UUID']
		photo = Photo.objects.create(Gallery_id=galleryId, UUID=UUID, Description=description, Location=location)
		user = User.objects.get(id=request.user.id)
		user.profile.ProfilePhoto = photo
		user.save()
		return redirect('App:myProfile')
	return redirect('App:uploadProfilePhoto')


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def makeFriendship(request, friendId):
	userId = request.user.id
	Friendship.objects.create(User_id=userId, Friend_id=friendId)
	return redirect('App:listOfUsers')


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def deleteFriendship(request, friendId):
	userId = request.user.id
	Friendship.objects.filter(User_id=userId, Friend_id=friendId).delete()
	return redirect('App:listOfUsers')


def loginExternal(request):
	try:
		userData = json.loads(request.GET.get('token'))
	except Exception:
		return redirect('App:login')
	sharedKey = ''
	for authService in zk.authenticationServiceList:
		if authService['name'] == userData['issuer']:
			sharedKey = authService['sharedKey']
			break
	decrypted = cr.defaultDecrypt(inputData=userData['crypted'].replace(' ', '+'), sharedKeyBase64=sharedKey)
	userid = json.loads(decrypted['data'])['userid']
	profile = Profile.objects.get(AuthService=userData['issuer'], AuthServiceUserId=userid)
	if profile is not None:
		login(request, profile.User)
		return redirect('App:home')
	else:
		return redirect('App:login')


def registerExternal(request):
	try:
		userData = json.loads(request.GET.get('token'))
	except Exception:
		return redirect('App:register')
	sharedKey = ''
	for authService in zk.authenticationServiceList:
		if authService['name'] == userData['issuer']:
			sharedKey = authService['sharedKey']
			break
	decrypted = cr.defaultDecrypt(inputData=userData['crypted'], sharedKeyBase64=sharedKey)
	data = json.loads(decrypted['data'])
	usermeta = json.loads(data['usermeta'])
	user = User.objects.create_user(
		username=usermeta['nick'] + "-" + userData['issuer'],
		first_name=usermeta['name'].split()[0],
		last_name=usermeta['name'].split()[1],
		email=usermeta['email'],
	)
	if user is not None:
		user.profile.AuthService = userData['issuer']
		user.profile.AuthServiceUserId = data['userid']
		user.save()
		login(request, user)
		return redirect('App:home')
	else:
		return redirect('App:register')


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def likePhoto(request, photoId):
	photo = Photo.objects.get(id=photoId)
	user = User.objects.get(id=request.user.id)
	if Like.objects.filter(User=user, Photo=photo):
		Like.objects.get(User=user, Photo=photo).delete()
	else:
		Like.objects.create(User=user, Photo=photo)
	# referer = request.META.get('HTTP_REFERER')
	# return HttpResponseRedirect(referer)
	return HttpResponse(status=200)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def deletePhoto(request):
	photoId = request.GET.get('id')
	Photo.objects.get(id=photoId).delete()
	referer = request.META.get('HTTP_REFERER')
	return HttpResponseRedirect(referer)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def deleteGallery(request, galleryId):
	Gallery.objects.get(id=galleryId).delete()
	referer = request.META.get('HTTP_REFERER')
	return HttpResponseRedirect(referer)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def profile(request):
	return AppViews.profileView(request, request.GET.get('id'))


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def gallery(request):
	return AppViews.galleryView(request, request.GET.get('id'))


def photoResponse(request, photo):
	if photo is None:
		return HttpResponse(status=200)
	isLiked = Like.objects.filter(User=request.user, Photo=photo)
	photoData = {
		'id': photo.id,
		'uuid': photo.UUID,
		'profilePhotoUrl': photo.Gallery.Owner.profile.ProfilePhoto.url,
		'ownerId': photo.Gallery.Owner_id,
		'ownerFullName': photo.Gallery.Owner.get_full_name(),
		'location': photo.Location,
		'galleryId': photo.Gallery_id,
		'url': photo.url,
		'isLiked': 1 if isLiked else 0,
		'likesCounter': photo.like_set.count(),
		'description': photo.Description,
		'uploadDateTime': localtime(photo.UploadDateTime).strftime('%Y-%m-%d %H:%M:%S'),
		'comments': [
			{
				'id': comment.id,
				'userId': comment.User_id,
				'userFullName': comment.User.get_full_name(),
				'text': comment.Text,
				'canDelete': comment.User_id == request.user.id
			}
			for comment in photo.photocomment_set.all()
		],
	}
	return JsonResponse(photoData)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def homeFeed(request):
	latestDateTime = request.GET.get('latestDateTime')
	if latestDateTime == 'now':
		latestDateTime = timezone.now()
	else:
		local = pytz.timezone("Europe/Athens")
		naive = datetime.strptime(latestDateTime, "%Y-%m-%d %H:%M:%S")
		local_dt = local.localize(naive, is_dst=None)
		latestDateTime = local_dt.astimezone(pytz.utc)
	friends = Friendship.objects.filter(Friend_id=request.user.id).all().values_list('User', flat=True)
	photo = Photo.objects.filter(Gallery__Owner__in=friends, UploadDateTime__lt=latestDateTime).order_by('-UploadDateTime').first()
	return photoResponse(request, photo)


@login_required(login_url=LOGIN_URL, redirect_field_name='callback')
def galleryFeed(request):
	latestDateTime = request.GET.get('latestDateTime')
	galleryId = request.GET.get('galleryId')
	if latestDateTime == 'now':
		latestDateTime = timezone.now()
	else:
		local = pytz.timezone("Europe/Athens")
		naive = datetime.strptime(latestDateTime, "%Y-%m-%d %H:%M:%S")
		local_dt = local.localize(naive, is_dst=None)
		latestDateTime = local_dt.astimezone(pytz.utc)
	photo = Photo.objects.filter(Gallery_id=galleryId, UploadDateTime__lt=latestDateTime).order_by('-UploadDateTime').first()
	return photoResponse(request, photo)
