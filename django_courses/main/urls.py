from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('about/', views.about, name='about'),
    path('course/', views.course, name='course'),
]
