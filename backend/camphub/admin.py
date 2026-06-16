from django.contrib import admin
from .models import Room, Activity, Cohort, StudyYear, Scheduleentry, Contact, TVBooking, Reminder

admin.site.register(Room)
admin.site.register(Activity)
admin.site.register(Cohort)
admin.site.register(StudyYear)
admin.site.register(Scheduleentry)
admin.site.register(Contact)
admin.site.register(TVBooking)
admin.site.register(Reminder)
