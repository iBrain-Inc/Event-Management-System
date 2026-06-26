from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Event, EventRegistration


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff",
            password="password123",
            is_staff=True,
        )
        self.member = User.objects.create_user(
            username="member",
            password="password123",
            is_staff=False,
        )
        self.url = reverse("admin_dashboard")

    def event_payload(self, **overrides):
        data = {
            "action": "save_event",
            "title": "Launch Meetup",
            "organizer": "Eventry Team",
            "description": "A practical meetup for builders.",
            "start_time": "2026-07-01T09:00",
            "end_time": "2026-07-01T11:00",
            "capacity": "100",
            "ticket_price": "250.00",
            "category": "meetups",
            "venue": "Main Hall",
            "status": "upcoming",
        }
        data.update(overrides)
        return data

    def create_event(self, **overrides):
        now = timezone.now()
        data = {
            "title": "Launch Meetup",
            "organizer": "Eventry Team",
            "description": "A practical meetup for builders.",
            "start_time": now,
            "end_time": now + timezone.timedelta(hours=2),
            "capacity": 100,
            "ticket_price": "250.00",
            "category": "meetups",
            "venue": "Main Hall",
            "status": "upcoming",
        }
        data.update(overrides)
        return Event.objects.create(**data)

    def test_only_staff_can_access_dashboard(self):
        self.client.login(username="member", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

        self.client.logout()
        self.client.login(username="staff", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_staff_can_crud_events_from_dashboard(self):
        self.client.login(username="staff", password="password123")

        response = self.client.post(self.url, self.event_payload())
        self.assertRedirects(response, self.url)
        event = Event.objects.get(title="Launch Meetup")

        response = self.client.post(self.url, self.event_payload(event_id=event.id, title="Updated Meetup"))
        self.assertRedirects(response, self.url)
        event.refresh_from_db()
        self.assertEqual(event.title, "Updated Meetup")

        response = self.client.post(self.url, {"action": "delete_event", "event_id": event.id})
        self.assertRedirects(response, self.url)
        self.assertFalse(Event.objects.filter(id=event.id).exists())

    def test_staff_can_crud_attendees_and_dashboard_displays_all(self):
        event = self.create_event()
        self.client.login(username="staff", password="password123")

        response = self.client.post(self.url, {
            "action": "save_registration",
            "attendee": "Amina Wekesa",
            "event": event.id,
            "email": "amina@example.com",
            "phone": "0712345678",
            "ticket_type": "general",
            "notes": "Front row",
        })
        self.assertRedirects(response, self.url)
        registration = EventRegistration.objects.get(email="amina@example.com")

        response = self.client.get(self.url)
        self.assertContains(response, "Amina Wekesa")
        self.assertContains(response, "Launch Meetup")

        response = self.client.post(self.url, {
            "action": "save_registration",
            "registration_id": registration.id,
            "attendee": "Amina Nekesa",
            "event": event.id,
            "email": "amina@example.com",
            "phone": "0712345678",
            "ticket_type": "vip",
            "notes": "Front row",
        })
        self.assertRedirects(response, self.url)
        registration.refresh_from_db()
        self.assertEqual(registration.attendee, "Amina Nekesa")
        self.assertEqual(registration.ticket_type, "vip")

        response = self.client.post(self.url, {"action": "delete_registration", "registration_id": registration.id})
        self.assertRedirects(response, self.url)
        self.assertFalse(EventRegistration.objects.filter(id=registration.id).exists())
