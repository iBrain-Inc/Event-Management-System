from django.shortcuts import get_object_or_404, render, redirect
from .models import Event, EventRegistration
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def create_event(request):
    if request.method == 'POST':
        try:
            title = request.POST['title']
            organizer_name = request.POST['organizer']
            category = request.POST['category']
            date = request.POST['date']
            time = request.POST['start_time']
            venue = request.POST['venue']
            capacity = request.POST['capacity']
            ticket_price = request.POST['ticket_price'] or '0'
            description = request.POST['description']
            image = request.FILES.get('image')

            start_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

            organizer_user, created = User.objects.get_or_create(
                username=organizer_name.replace(' ', '_').lower(),
                defaults={'first_name': organizer_name}
            )

            category_map = {
                'technology': 'technology',
                'workshop': 'workshop',
                'community': 'community',
                'career': 'career',
                'competition': 'competition',
                'meetups': 'meetups',
                'other': 'other',
                'conference': 'conference',
                'webinar': 'webinar',
                'fundraiser': 'fundraiser'
            }
            category_value = category_map.get(category.lower(), 'other')
            if capacity <= 0:
                messages.error(request, 'Capacity cannot be zero or negative.')
                return render(request, 'event/create_event.html')
            Event.objects.create(
                title=title,
                organizer=str(organizer_user),
                category=category_value,
                start_time=start_datetime,
                end_time=start_datetime,
                venue=venue,
                capacity=capacity,
                ticket_price=ticket_price,
                description=description,
                status='upcoming',
                image=image
            )
            messages.success(request, 'Event created successfully!')
            return redirect('create-event')
        except Exception as e:
            messages.error(request, f'Error creating event: {str(e)}')
            return render(request, 'event/create_event.html')
    return render(request, 'event/create_event.html')

def display_events(request):
    events = Event.objects.all()
    return render(request, 'home.html', {'events': events})

def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        try:
            attendee = request.POST.get('attendee', '').strip()
            email = request.POST.get('email', '').strip().lower()
            phone = request.POST.get('phone', '').strip()
            ticket_type = request.POST.get('ticket_type', 'general').strip()
            notes = request.POST.get('notes', '').strip()

            if not attendee or not email:
                messages.error(request, 'Please provide your name and email address.')
                return render(request, 'event/register_event.html', {'event': event})

            registered_count = EventRegistration.objects.filter(event=event).count()
            if registered_count >= event.capacity:
                messages.error(request, 'This event is at full capacity.')
                return render(request, 'event/register_event.html', {'event': event})

            if EventRegistration.objects.filter(event=event, email=email).exists():
                messages.warning(request, 'This email is already registered for this event.')
                return render(request, 'event/register_event.html', {'event': event})

            EventRegistration.objects.create(
                attendee=attendee,
                event=event,
                email=email,
                phone=phone,
                ticket_type=ticket_type,
                notes=notes
            )

            messages.success(request, f'Successfully registered for {event.title}!')
            return redirect('register_event', event_id=event.id)

        except Exception as e:
            messages.error(request, f'Error registering for event: {str(e)}')
            return render(request, 'event/register_event.html', {'event': event})

    return render(request, 'event/register_event.html', {'event': event})
