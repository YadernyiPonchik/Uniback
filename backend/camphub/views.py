from django.shortcuts import render

# Create your views here.
from .serializers import ScheduleEntrySerializer
from .models import Scheduleentry
from rest_framework import viewsets

from rest_framework.permissions import IsAuthenticated

class ScheduleEntryViewSet(viewsets.ModelViewSet):
    queryset= Scheduleentry.objects.all()
    serializer_class=  ScheduleEntrySerializer
