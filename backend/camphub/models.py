from django.db import models

# Create your models here.


class StudyYear(models.Model):
    year_name = models.CharField(max_length=50)


class Cohort(models.Model):
    study_year = models.ForeignKey(StudyYear, on_delete=models.CASCADE)
    cohort_name = models.CharField(max_length=50)


class Activity(models.Model):
    CLASS_CHOICES = [
        ('MATH', 'Math'),
        ('ENGLISH', 'English'),
        ('CALCULUS', 'Calculus'),
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('FACULTY', 'Faculty'),
        ('CLEANING', 'Cleaning'),
        ('CLEANING & DISINFECTION', 'Cleaning & Disinfection'),
        ('ALTAI-NARYN FOOTBALL SCHOOL', 'Altai-Naryn Football School'),
        ('JUDO GRAPPLING', 'Judo Grappling'),
        ('MCHS', 'MCHS'),
        ('PHYSICAL EDUCATION', 'Physical Education'),
        ('VOLLEYBALL', 'Volleyball'),
    ]


    name = models.CharField(
        max_length=50, choices=CLASS_CHOICES, default='MATH')


class Instructor(models.Model):
    STATUS_TYPE = [
        ('ON_CAMPUS', 'on_campus'),
        ('OFF_CAMPUS', 'off_campus'),
    ]

    firstname = models.CharField(max_length=15)
    lastname = models.CharField(max_length=15)
    status = models.CharField(
        max_length=20, choices=STATUS_TYPE, default='ON_CAMPUS')


class Room(models.Model):
    room_number = models.CharField(max_length=15)


class Scheduleentry(models.Model):
    CLASS_TYPE = [
        ('LESSON', 'Lesson'),
        ('EXAM', 'Exam'),
    ]

    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]

    cohort = models.ForeignKey(
        Cohort, on_delete=models.CASCADE, null=True, blank=True)
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE,  null=True, blank=True)
    entry_date = models.DateField(null=True, blank=True)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK,
                        default='MON')
    start_time = models.TimeField()
    end_time = models.TimeField()
    entry_type = models.CharField(
        max_length=20, choices=CLASS_TYPE, null=True, blank=True)
    instructors = models.ManyToManyField(Instructor, blank=True)
    rooms = models.ManyToManyField(Room, blank=True)


# class EntryInstructors(models.Model):
#     entry = models.ForeignKey(Scheduleentry, on_delete=models.CASCADE)
#     instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)


class Reminder(models.Model):
    user = models.ForeignKey('accounts.UserAccount', on_delete=models.CASCADE)
    entry = models.ForeignKey('Scheduleentry', on_delete=models.CASCADE)
    minutes_before = models.IntegerField(default=15)


class Contact(models.Model):
    CATEGORY_CHOICES = [
        ('MEDICAL', 'Medical'),
        ('FOOD', 'Food/Shop'),
        ('SECURITY', 'Security'),
        ('ADMIN', 'Administration'),

    ]

    LOCATION_CHOICES = [
        ('ON_CAMPUS', 'On Campus'),
        ('OFF_CAMPUS', 'Off Campus'),
    ]

    full_name = models.CharField(
        max_length=50)
    role = models.CharField(
        max_length=50)
    phone_number= models.IntegerField()
    sector = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)

# class Canteen(models.Model):
#     MEAL_CHOICES= [

#     ]

from django.conf import settings

class TVBooking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lounge_name = models.CharField(max_length=50)
    booker_name = models.CharField(max_length=100)
    booking_date = models.CharField(max_length=10)
    booking_time = models.CharField(max_length=5)
    
    def __str__(self):
        return f"{self.booker_name} - {self.lounge_name} ({self.booking_date} {self.booking_time})"

class Reminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reminder_type = models.CharField(max_length=20)  # "lesson", "gym", "bubble", "tv"
    subject_name = models.CharField(max_length=100)
    day = models.CharField(max_length=15)
    event_time_str = models.CharField(max_length=10)
    reminder_offset = models.IntegerField()
    
    def __str__(self):
        return f"{self.user} - {self.reminder_type} - {self.subject_name}"