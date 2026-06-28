from django.shortcuts import render
from .serializers import EventSerializer
from .models import Event
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
