from django.db import models
from django.conf import settings

# Create your models here.
#  new section


class Room(models.Model):
    room_number = models.CharField(
        max_length=15, unique=True)

    def __str__(self):
        return self.room_number


class StudyYear(models.Model):
    CHOICES = [
        ('FESH', 'Fresh'),
        ('SOPH', 'Soph'),
        ('JUN', 'Jun'),
        ('SEN', 'Sen'),
    ]
    year_name = models.CharField(max_length=50, choices=CHOICES, default='SOF')


class Subject(models.Model):
    CHOICES = [
        ('MATH', 'Math'),
        ('ENGLISH', 'English'),
        ('PHYSICS', 'Physics'),
        ('KYRGIZ', 'Kyrgiz'),
    ]
    name = models.CharField(max_length=50)


class Cohort(models.Model):

    study_year_id = models.ForeignKey(
        StudyYear, on_delete=models.CASCADE, null=True, blank=True, db_column='study_year_id')
    cohort_name = models.CharField(max_length=50)
    # delete


class Event(models.Model):
    CHOICES = [
        ('GYM', 'Gym'),
        ('CLASS', 'Class'),
        ('BUBBLE', 'Bubble'),
        ('MEAL_TIME', 'Meal_Time'),
    ]
    DAYS = [
        ('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'),
        ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')
    ]
    day = models.CharField(max_length=3, choices=DAYS, default='MON')
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(

        max_length=50, choices=CHOICES, default='GYM')


class GymEvent(models.Model):
    CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),

    ]
    gender = models.CharField(
        max_length=50, choices=CHOICES, default='MALE')
    event_id = models.ForeignKey(
        Event, on_delete=models.CASCADE, null=True, blank=True, db_column='event_id')


class Instructor(models.Model):
    STATUS_TYPE = [
        ('ON_CAMPUS', 'on_campus'),
        ('OFF_CAMPUS', 'off_campus'),
    ]

    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    status = models.CharField(
        max_length=20, choices=STATUS_TYPE, default='ON_CAMPUS')


class ClassEvent(models.Model):

    subject_id = models.ForeignKey(
        Subject, on_delete=models.CASCADE, null=True, blank=True, db_column='subject_id')
    instructor_id = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, null=True, blank=True, db_column='instructor_id')
    cohort_id = models.ForeignKey(
        Cohort, on_delete=models.CASCADE, null=True, blank=True, db_column='cohort_id')
    event_id = models.ForeignKey(
        Event, on_delete=models.CASCADE, null=True, blank=True, db_column='event_id')

    room_id = models.ForeignKey(
        Room, on_delete=models.CASCADE, null=True, blank=True, db_column='room_id')


class MealTime(models.Model):
    meal_name = models.CharField(max_length=50)
    event_id = models.ForeignKey(
        Event, on_delete=models.CASCADE, null=True, blank=True, db_column='event_id')


# end of new section


class Contact(models.Model):
    CATEGORY_CHOICES = [
        ('MEDICAL', 'Medical'),
        ('FOOD', 'Food/Shop'),
        ('SECURITY', 'Security'),
        ('ADMIN', 'Administration'),
        ('TAXI', 'Taxi/Transport')

    ]

    LOCATION_CHOICES = [
        ('ON_CAMPUS', 'On Campus'),
        ('OFF_CAMPUS', 'Off Campus'),
    ]

    full_name = models.CharField(
        max_length=50)
    role = models.CharField(
        max_length=50)
    phone_number = models.CharField(max_length=20)
    sector = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="FOOD")

    location = models.CharField(
        max_length=20, choices=LOCATION_CHOICES, null=True, blank=True)


class TVBooking(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, db_column='user_id')
    lounge_name = models.CharField(max_length=50)
    booker_name = models.CharField(max_length=100)
    booking_date = models.CharField(max_length=10)
    booking_time = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.booker_name} - {self.lounge_name} ({self.booking_date} {self.booking_time})"


class Reminder(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, db_column='user_id')
    # "lesson", "gym", "bubble", "tv"
    reminder_type = models.CharField(max_length=20)
    subject_name = models.CharField(max_length=100)
    day = models.CharField(max_length=15)
    event_time_str = models.CharField(max_length=10)
    reminder_offset = models.IntegerField()

    def __str__(self):
        return f"{self.user} - {self.reminder_type} - {self.subject_name}"
