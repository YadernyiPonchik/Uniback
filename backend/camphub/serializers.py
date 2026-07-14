from rest_framework import serializers

from .bot.crud import day_mapping
from .models import Event, Contact, ClassEvent, GymEvent, MealTime, BubbleEvent

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

class EventWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['day', 'start_time', 'end_time']

class BubbleEventSerializer(serializers.ModelSerializer):
    event = EventSerializer(source='event_id', read_only=True)

    event_data = EventWriteSerializer(write_only=True)

    class Meta:
        model = BubbleEvent
        fields = ['id', 'name', 'event', 'event_data']

    def create(self, validated_data):
        event_data = validated_data.pop('event_data')

        day=event_data['day']
        start_time=event_data['start_time']
        end_time=event_data['end_time']

        overlapping = Event.objects.filter(
            day=day,
            status='BUBBLE',
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if overlapping.exists():
            raise serializers.ValidationError(
                {"error":"This time slot overlaps with an existing bubble event."}
            )

        event = Event.objects.create(
            day=day,
            start_time=start_time,
            end_time=end_time,
            status='BUBBLE'
        )
        if BubbleEvent.objects.filter(event_id=event).exists():
            raise serializers.ValidationError(
                {"error": "This slot is already booked."}
            )

        return BubbleEvent.objects.create(
            event_id=event,
            **validated_data
        )

class MealTimeSerializer(serializers.ModelSerializer):
    event = EventSerializer(source='event_id', read_only=True)

    event_data = EventWriteSerializer(write_only=True)

    class Meta:
        model = MealTime
        fields = ['id', 'meal_name', 'event', 'event_data']

    def create(self, validated_data):
        event_data = validated_data.pop('event_data')

        day=event_data['day']
        start_time=event_data['start_time']
        end_time=event_data['end_time']

        overlapping = Event.objects.filter(
           day=day,
            status='MEAL_TIME',
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if overlapping.exists():
            raise serializers.ValidationError(
                {"error":"This time slot overlaps with an existing meal time event."}
            )

        event = Event.objects.create(
            day=day,
            start_time=start_time,
            end_time=end_time,
            status='MEAL_TIME'
        )

        if MealTime.objects.filter(event_id=event).exists():
            raise serializers.ValidationError(
                {"error": "This slot is already booked."}
            )

        return MealTime.objects.create(
            event_id=event,
            **validated_data
        )

class GymEventSerializer(serializers.ModelSerializer):
    event = EventSerializer(source='event_id', read_only=True)

    event_data = EventWriteSerializer(write_only=True)

    class Meta:
        model = GymEvent
        fields = ['id', 'gender', 'event', 'event_data']

    def create(self, validated_data):
        event_data = validated_data.pop('event_data')


        day=event_data['day']
        start_time=event_data['start_time']
        end_time=event_data['end_time']

        overlapping = Event.objects.filter(
            day=day,
            status='GYM',
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if overlapping.exists():
            raise serializers.ValidationError(
                {"error":"This time slot overlaps with an existing gym event."}
            )

        event = Event.objects.create(
            day=day,
            start_time=start_time,
            end_time=end_time,
            status='GYM'
        )

        if GymEvent.objects.filter(event_id=event).exists():
            raise serializers.ValidationError(
                {"error": "This slot is already booked."}
            )

        return GymEvent.objects.create(
            event_id=event,
            **validated_data
        )