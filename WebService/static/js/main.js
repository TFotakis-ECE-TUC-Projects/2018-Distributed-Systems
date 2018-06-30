let lastDateTime = "now";


photoList = new Vue({
	el: "#photoList",
	data: {
		photoList: []
	},
	methods: {
		likePhoto: function (photoId) {
			$.ajax(
				{
					url: "/api/likePhoto/" + photoId + '/',
					success: function () {
						let heartIcon = document.getElementById("heart" + photoId);
						let likeCounter = document.getElementById('likesCounter' + photoId);
						if (heartIcon.className === "far fa-heart") {
							heartIcon.setAttribute('class', 'fas fa-heart text-danger');
							likeCounter.textContent = (parseInt(likeCounter.textContent) + 1).toString();
						} else {
							heartIcon.setAttribute('class', 'far fa-heart');
							likeCounter.textContent = (parseInt(likeCounter.textContent) - 1).toString();
						}
					}
				}
			)
		},
		deleteComment: function (commentId) {
			$.ajax(
				{
					url: "/api/deleteComment/" + commentId + '/',
					success: function () {
						document.getElementById("comment" + commentId).remove();
					}
				}
			)
		},
		addComment: function (photoId) {
			let photoTextInput = document.getElementById("photoTextInput" + photoId);
			let text = photoTextInput.value;
			$.ajax(
				{
					url: "/api/addComment/" + photoId + '?comment=' + text,
					success: function (data) {
						let photo = photoList.photoList.find(photo => photo.id == data.photoId);
						let comment = {
							id: data.id,
							userId: data.userId,
							userFullName: data.userFullName,
							text: data.text,
							canDelete: true
						};
						photo.comments.push(comment);
						document.getElementById("form" + data.photoId).reset();
					}
				}
			)
		}
	}
});


function checkScrolling() {
	return $(window).scrollTop() >= ($(document).height() - window.innerHeight - 10);
}


let hasPhoto = true;
let requestUrl = function () {
	if (window.location.pathname === '/') {
		return "/api/homeFeed?latestDateTime=" + lastDateTime;
	} else {
		let galleryId = window.location.pathname.split('/')[2];
		return "/api/galleryFeed?galleryId=" + galleryId + "&latestDateTime=" + lastDateTime;
	}
};

function addPhoto() {
	$.ajax(
		{
			url: requestUrl(),
			success: function (data) {
				if (!data) {
					hasPhoto = false;
					return;
				}
				lastDateTime = data.uploadDateTime;
				photoList.photoList.push(data);
				hasPhoto = true;
				if (checkScrolling()) {
					addPhoto()
				}
			},
			error: function () {
				hasPhoto = false;
			}
		}
	);
}


$(document).ready(function () {
	addPhoto();
	let hasPhoto = true;
	$(window).scroll(function () {
		if (checkScrolling() && hasPhoto) {
			hasPhoto = addPhoto();
		}
	});
});
