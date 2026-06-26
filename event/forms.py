from django import forms

from .models import Event, EventRegistration


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs.setdefault("class", "form-control")
        super().__init__(attrs=attrs, format="%Y-%m-%dT%H:%M")


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "organizer",
            "description",
            "start_time",
            "end_time",
            "capacity",
            "ticket_price",
            "category",
            "venue",
            "status",
            "image",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "organizer": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "start_time": DateTimeLocalInput(),
            "end_time": DateTimeLocalInput(),
            "capacity": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ticket_price": forms.NumberInput(attrs={"class": "form-control", "min": 0, "step": "0.01"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "venue": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ("start_time", "end_time"):
            self.fields[field].input_formats = ["%Y-%m-%dT%H:%M"]


class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ["attendee", "event", "email", "phone", "ticket_type", "notes"]
        widgets = {
            "attendee": forms.TextInput(attrs={"class": "form-control"}),
            "event": forms.Select(attrs={"class": "form-select"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "ticket_type": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
