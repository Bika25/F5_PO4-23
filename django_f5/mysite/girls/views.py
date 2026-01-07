from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
    update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Course, Lesson, Enrollment


# ---------------------------
# STATIC PAGES
# ---------------------------

def homepage(request):
    courses = Course.objects.filter(is_published=True)
    return render(request, 'girls/homepage.html', {'courses': courses})


def catalog(request):
    courses = Course.objects.filter(is_published=True)

    # ----------------------
    # GET parameters
    # ----------------------
    selected_levels = request.GET.getlist('level')
    selected_durations = request.GET.getlist('duration')
    selected_prices = request.GET.getlist('price')

    # ----------------------
    # Level filter
    # ----------------------
    if selected_levels:
        courses = courses.filter(level__in=selected_levels)

    # ----------------------
    # Duration filter (text field)
    # ----------------------
    if selected_durations:
        duration_query = Q()
        for d in selected_durations:
            try:
                start, end = map(int, d.split('-'))
                for week in range(start, end + 1):
                    duration_query |= Q(duration__icontains=str(week))
            except ValueError:
                pass
        courses = courses.filter(duration_query)

    # ----------------------
    # Price filter
    # ----------------------
    if selected_prices:
        price_query = Q()
        for p in selected_prices:
            try:
                min_p, max_p = map(int, p.split('-'))
                price_query |= Q(price__gte=min_p, price__lte=max_p)
            except ValueError:
                pass
        courses = courses.filter(price_query)

    return render(request, 'girls/catalog.html', {
        'courses': courses,
        'selected_levels': selected_levels,
        'selected_durations': selected_durations,
        'selected_prices': selected_prices,
    })


def aboutus(request):
    return render(request, 'girls/aboutus.html')


# ---------------------------
# COURSE PAGE + ENROLL
# ---------------------------

@login_required
def coursepage(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_published=True)

    enrollment = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).first()

    return render(request, 'girls/coursepage.html', {
        'course': course,
        'enrollment': enrollment
    })


@login_required
def enroll_course(request, course_id):
    """
    Handles enrollment.
    Redirects to 'next' URL if passed, else to profile.
    """
    course = get_object_or_404(Course, id=course_id, is_published=True)

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'status': 'active'}
    )

    if created:
        messages.success(request, f"You have successfully enrolled in {course.title}!")
    else:
        messages.info(request, f"You are already enrolled in {course.title}.")

    # Redirect to next page if provided
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('girls:profile')


# ---------------------------
# LESSONS
# ---------------------------

@login_required
def lesson_dynamic(request, course_id, lesson_order):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, course=course, order=lesson_order)

    # Protect lessons if user is not enrolled
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "You must enroll in the course first.")
        return redirect('girls:coursepage', course_id=course.id)

    return render(request, 'girls/lesson_dynamic.html', {
        'course': course,
        'lesson': lesson
    })


# ---------------------------
# AUTH
# ---------------------------

def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        terms_accepted = request.POST.get('terms') == 'on'

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
        elif not terms_accepted:
            messages.error(request, "You must accept the terms!")
        elif User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered!")
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=surname
            )
            auth_login(request, user)
            return redirect('girls:profile')

    return render(request, 'girls/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('girls:homepage')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect('girls:profile')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'girls/login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('girls:login')


# ---------------------------
# PROFILE
# ---------------------------

@login_required
def editprofile(request):
    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.username = user.email

        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if password:
            if password == confirm_password:
                user.set_password(password)
                update_session_auth_hash(request, user)
            else:
                messages.error(request, "Passwords do not match")
                return redirect('girls:editprofile')

        user.save()
        messages.success(request, "Profile updated")

    return render(request, 'girls/editprofile4.html', {'user': user})

@login_required
def profile(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    user_courses = []

    for enrollment in enrollments:
        course = enrollment.course
        # Get the next lesson (the first lesson that the user has not completed)
        next_lesson = course.lessons.first()  # simple version, adjust for completed logic

        user_courses.append({
            'course': course,
            'enrollment': enrollment,
            'next_lesson': next_lesson
        })

    return render(request, 'girls/profile3.html', {'user_courses': user_courses})

def contact(request):
    return render(request, 'girls/contact.html')


@login_required
def payment_view(request):
    return render(request, 'girls/payment.html')
