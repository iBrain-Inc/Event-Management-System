from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('create-event/', views.create_event, name='create-event'),
    path('register/<int:event_id>/', views.register_event, name='register_event'),
]
