from django.shortcuts import render

# Create your views here.
def start(request):
	return render(request, "start.html")

def help(request):
	return render(request, "help.html")