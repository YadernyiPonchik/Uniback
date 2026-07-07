from rest_framework import viewsets, permissions
from .serializers import EventSerializer, ContactSerializer, ScheduleSerializer
from .models import Event, Contact, ClassEvent

from rest_framework import viewsets, permissions

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset= Contact.objects.all()
    serializer_class = ContactSerializer

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            # Allow everyone to see
            permission_classes = [permissions.AllowAny]
        else:
            # Only admins can change
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]


class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        queryset = ClassEvent.objects.select_related(
            'event_id', 'subject_id', 'instructor_id',
            'cohort_id', 'cohort_id__study_year_id'
        )
        day = self.request.query_params.get('day')
        course = self.request.query_params.get('course')
        if day:
            queryset = queryset.filter(event_id__day=day.upper())
        if course:
            queryset = queryset.filter(cohort_id=course)
        return queryset
