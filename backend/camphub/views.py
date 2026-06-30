from django.shortcuts import render
from .serializers import EventSerializer, ContactSerializer
from .models import Event, Contact
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [AllowAny]

