from django.shortcuts import render


def homeView(request):
	context = {}
	return render(request=request, template_name="App/home.html", context=context)
