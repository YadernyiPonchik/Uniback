from rest_framework import serializers
from .models import Scheduleentry


class ScheduleEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheduleentry
        fields = '__all__'
