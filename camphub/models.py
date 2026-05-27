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
        ('CLEANING', 'Cleaning')
    ]

    name = models.CharField(
        max_length=20, choices=CLASS_CHOICES, default='Math')


class Instructor(models.Model):
    STATUS_TYPE = [
        ('ON_CAMPUS', 'on_campus'),
        ('OFF_CAMPUS', 'off_campus'),
    ]

    firstname = models.CharField(max_length=15)
    lastname = models.CharField(max_length=15)
    status = models.CharField(
        max_length=20, choices=STATUS_TYPE, default='on_campus')


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
    ]

    cohort = models.ForeignKey(
        Cohort, on_delete=models.CASCADE, null=True, blank=True)
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE,  null=True, blank=True)
    entry_date = models.DateField(null=True, blank=True)
    day= models.CharField(max_length=10, choices=DAYS_OF_WEEK, null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    entry_type = models.CharField(
        max_length=20, choices=CLASS_TYPE, default='Lesson')
    instructors = models.ManyToManyField(Instructor, blank=True)
    rooms = models.ManyToManyField(Room, blank=True)


# class EntryInstructors(models.Model):
#     entry = models.ForeignKey(Scheduleentry, on_delete=models.CASCADE)
#     instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)


class Entryrooms(models.Model):
    entry = models.ForeignKey(Scheduleentry, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
