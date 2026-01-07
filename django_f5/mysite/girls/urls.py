from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import payment_view

app_name = 'girls'  # important if you’re using namespaced URLs


urlpatterns = [
    # Static / main pages
    path('', views.homepage, name='homepage'),
    path('catalog/', views.catalog, name='catalog'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('course/<int:course_id>/', views.coursepage, name='coursepage'),
    path('payment/', payment_view, name='payment'),
    path('course/<int:course_id>/join/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/lesson/<int:lesson_order>/', views.lesson_dynamic, name='lesson_dynamic'),
    path('contact/', views.contact, name='contact'),


    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile / account
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.editprofile, name='editprofile'),
]

# Serve static/media in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
