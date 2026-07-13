from rest_framework import serializers
from .models import Event, Contact, ClassEvent

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    day         = serializers.CharField(source='event_id.day')
    start_time  = serializers.TimeField(source='event_id.start_time')
    end_time    = serializers.TimeField(source='event_id.end_time')
    subject     = serializers.CharField(source='subject_id.name')
    instructor  = serializers.SerializerMethodField()
    cohort      = serializers.CharField(source='cohort_id.cohort_name')
    course_year = serializers.CharField(source='cohort_id.study_year_id.year_name')
    class Meta:
        model = ClassEvent
        fields = ['id', 'day', 'start_time', 'end_time', 'subject', 'instructor', 'cohort', 'course_year']
    def get_instructor(self, obj):
        if obj.instructor_id:
            return f"{obj.instructor_id.first_name} {obj.instructor_id.last_name}"
        return None