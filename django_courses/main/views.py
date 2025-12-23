from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def home(request):
    return render(request, 'homepage.html')

def catalog(request):
    return render(request, 'catalog.html')

def about(request):
    return render(request, 'aboutus.html')

def course(request):
    return render(request, 'coursepage.html')
