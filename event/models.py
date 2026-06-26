from django.db import models
from django.utils import timezone


class Event(models.Model):
    title = models.CharField(max_length=255)
    organizer = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.IntegerField(default=0)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    category = models.CharField(max_length=100, choices=[
        ('workshop', 'Workshop'),
        ('conference', 'Conference'),
        ('meeting', 'Meeting'),
        ('webinar', 'Webinar'),
        ('technology', 'Technology'),
        ('community', 'Community'),
        ('career', 'Career'),
        ('competition', 'Competition'),
        ('meetups', 'Meetups'),
        ('fundraiser', 'Fundraiser'),
        ('other', 'Other')
    ])
    venue = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[
            ('upcoming', 'Upcoming'),
            ('ongoing', 'Ongoing'),
            ('completed', 'Completed')
        ]
    )
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)

    def calculate_status(self):
        today = timezone.localdate()
        start_date = timezone.localtime(self.start_time).date()
        end_date = timezone.localtime(self.end_time).date()

        if start_date > today:
            return 'upcoming'
        if end_date < today:
            return 'completed'
        return 'ongoing'

    def save(self, *args, **kwargs):
        self.status = self.calculate_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    attendee = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    email = models.EmailField()
    ticket_type = models.CharField(max_length=100, choices=[
        ('general', 'General Admission'),
        ('vip', 'VIP'),
        ('student', 'Student'),
        ('early_bird', 'Early Bird'),
        ('group', 'Group'),
        ('other', 'Other')
    ], default='general')

    class Meta:
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.attendee} attending {self.event.title}"
