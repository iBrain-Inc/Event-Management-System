from django.shortcuts import get_object_or_404, render, redirect
from event.forms import EventForm, EventRegistrationForm
from event.models import Event, EventRegistration
from django.db.models import Count
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages


def home(request):
    events = Event.objects.all().order_by('start_time')
    return render(request, 'home.html', {'events': events})


@login_required(login_url='login')
@user_passes_test(lambda user: user.is_staff, login_url='home')
def admin(request):
    editing_event = None
    editing_registration = None
    event_form = None
    registration_form = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_event':
            event_id = request.POST.get('event_id')
            instance = get_object_or_404(Event, id=event_id) if event_id else None
            event_form = EventForm(request.POST, request.FILES, instance=instance)
            if event_form.is_valid():
                event = event_form.save()
                messages.success(request, f'"{event.title}" was saved.')
                return redirect('admin_dashboard')
            editing_event = instance
            messages.error(request, 'Please fix the event form errors below.')

        elif action == 'edit_event':
            editing_event = get_object_or_404(Event, id=request.POST.get('event_id'))

        elif action == 'delete_event':
            event = get_object_or_404(Event, id=request.POST.get('event_id'))
            title = event.title
            event.delete()
            messages.success(request, f'"{title}" was deleted.')
            return redirect('admin_dashboard')

        elif action == 'save_registration':
            registration_id = request.POST.get('registration_id')
            instance = get_object_or_404(EventRegistration, id=registration_id) if registration_id else None
            registration_form = EventRegistrationForm(request.POST, instance=instance)
            if registration_form.is_valid():
                registration = registration_form.save()
                messages.success(request, f'{registration.attendee} was saved.')
                return redirect('admin_dashboard')
            editing_registration = instance
            messages.error(request, 'Please fix the attendee form errors below.')

        elif action == 'edit_registration':
            editing_registration = get_object_or_404(EventRegistration, id=request.POST.get('registration_id'))

        elif action == 'delete_registration':
            registration = get_object_or_404(EventRegistration, id=request.POST.get('registration_id'))
            attendee = registration.attendee
            registration.delete()
            messages.success(request, f'{attendee} was removed from the attendee list.')
            return redirect('admin_dashboard')

    if event_form is None:
        event_form = EventForm(instance=editing_event)
    if registration_form is None:
        registration_form = EventRegistrationForm(instance=editing_registration)

    events = Event.objects.annotate(registration_count=Count('registrations')).order_by('-start_time')
    registrations = EventRegistration.objects.select_related('event').order_by('-registration_date')
    total_revenue = sum(reg.event.ticket_price for reg in registrations)
    upcoming_count = events.filter(status='upcoming').count()

    return render(request, 'admin.html', {
        'events': events,
        'registrations': registrations,
        'event_form': event_form,
        'registration_form': registration_form,
        'editing_event': editing_event,
        'editing_registration': editing_registration,
        'total_revenue': total_revenue,
        'upcoming_count': upcoming_count,
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')

    return render(request, 'login.html')


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'login.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'login.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'login.html')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                password=password
            )

            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {first_name}!')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'login.html')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')
