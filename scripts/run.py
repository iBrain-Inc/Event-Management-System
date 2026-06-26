""" from event.models import Event
event = Event.objects.create(
            title=title,
            organizer=organizer,
            category=category,
            start_time=f"{date} {time}",
            venue=venue,
            capacity=capacity,
            ticket_price=ticket_price,
            description=description,
            image=image  # Save the uploaded image
        )
print(event) """