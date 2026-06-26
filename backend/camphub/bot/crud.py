from asgiref.sync import sync_to_async
from django.conf import settings
from accounts.models import UserAccount
from camphub.models import Cohort, Activity, Scheduleentry, Contact, TVBooking, Reminder, StudyYear
from datetime import datetime, time, timedelta

day_mapping = {
    "Monday": "MON", "Tuesday": "TUE", "Wednesday": "WED", "Thursday": "THU",
    "Friday": "FRI", "Saturday": "SAT", "Sunday": "SUN",
    "MON": "MON", "TUE": "TUE", "WED": "WED", "THU": "THU", "FRI": "FRI", "SAT": "SAT", "SUN": "SUN"
}

# Compatibility wrappers to mimic SQLAlchemy model objects
class LessonWrapper:
    def __init__(self, entry):
        self.id = entry.id
        self.academic_level = entry.cohort.cohort_name if entry.cohort else ""
        self.day_of_week = next((k for k, v in day_mapping.items() if v == entry.day), entry.day)
        self.time_str = entry.start_time.strftime("%H:%M") if entry.start_time else "09:00"
        self.subject_name = entry.activity.name.title() if entry.activity else ""

class GymSlotWrapper:
    def __init__(self, entry):
        self.id = entry.id
        self.day_of_week = next((k for k, v in day_mapping.items() if v == entry.day), entry.day)
        self.start_time_str = entry.start_time.strftime("%H:%M") if entry.start_time else ""
        self.end_time_str = entry.end_time.strftime("%H:%M") if entry.end_time else ""
        self.session_type = entry.activity.name.title() if entry.activity else ""

class BubbleWrapper:
    def __init__(self, entry):
        self.id = entry.id
        self.day_of_week = next((k for k, v in day_mapping.items() if v == entry.day), entry.day)
        self.sport_name = entry.activity.name.title() if entry.activity else ""
        self.time_str = f"{entry.start_time.strftime('%H:%M')} – {entry.end_time.strftime('%H:%M')}"

class ContactWrapper:
    def __init__(self, entry):
        self.id = entry.id
        self.category = "On Campus" if entry.location == "ON_CAMPUS" else "Off Campus"
        self.name = entry.full_name
        self.phone = str(entry.phone_number)
        self.details = entry.role

class TVBookingWrapper:
    def __init__(self, entry):
        self.id = entry.id
        self.user_id = entry.user.telegram_id
        self.lounge_name = entry.lounge_name
        self.booker_name = entry.booker_name
        self.booking_date = entry.booking_date
        self.booking_time = entry.booking_time

class ReminderWrapper:
    def __init__(self, entry):
        self.id = entry.id
        self.telegram_user_id = entry.user.telegram_id
        self.reminder_type = entry.reminder_type
        self.subject_name = entry.subject_name
        self.day = entry.day
        self.event_time_str = entry.event_time_str
        self.reminder_offset = entry.reminder_offset

def parse_time_str(t_str):
    t_str = t_str.strip()
    dt = datetime.strptime(t_str, "%H:%M")
    return time(dt.hour, dt.minute)

# --- User CRUD ---
@sync_to_async
def get_user(telegram_id: int):
    try:
        u = UserAccount.objects.select_related('cohort').get(telegram_id=telegram_id)
        u.academic_level = u.cohort.cohort_name if u.cohort else None
        return u
    except UserAccount.DoesNotExist:
        return None

@sync_to_async
def create_user(telegram_id: int, name: str = None, gender: str = None, cohort_name: str = None):
    email = f"tg_{telegram_id}@unispace.com"
    cohort = None
    if cohort_name:
        cohort = Cohort.objects.filter(cohort_name=cohort_name).first()
    
    u = UserAccount.objects.create(
        email=email,
        name=name or "Student",
        telegram_id=telegram_id,
        gender=gender.upper() if gender else None,
        cohort=cohort
    )
    u.academic_level = cohort_name
    return u

@sync_to_async
def update_user_level(telegram_id: int, level: str):
    try:
        cohort = Cohort.objects.filter(cohort_name=level).first()
        u = UserAccount.objects.get(telegram_id=telegram_id)
        u.cohort = cohort
        u.save()
        u.academic_level = level
        return u
    except UserAccount.DoesNotExist:
        return None

@sync_to_async
def update_user_gender(telegram_id: int, gender: str):
    try:
        u = UserAccount.objects.get(telegram_id=telegram_id)
        u.gender = gender.upper()
        u.save()
        return u
    except UserAccount.DoesNotExist:
        return None

# --- Lessons CRUD ---
@sync_to_async
def get_lessons_for_day(level: str, day: str):
    day_code = day_mapping.get(day, day)
    entries = Scheduleentry.objects.filter(
        cohort__cohort_name=level,
        day=day_code,
        entry_type="LESSON"
    ).select_related('cohort', 'activity').order_by('start_time')
    return [LessonWrapper(e) for e in entries]

@sync_to_async
def get_weekly_lessons(level: str):
    entries = Scheduleentry.objects.filter(
        cohort__cohort_name=level,
        entry_type="LESSON"
    ).select_related('cohort', 'activity').order_by('day', 'start_time')
    return [LessonWrapper(e) for e in entries]

@sync_to_async
def add_lesson(level: str, day: str, time_str: str, subject_name: str):
    study_year, _ = StudyYear.objects.get_or_create(year_name="2025-2026")
    cohort, _ = Cohort.objects.get_or_create(study_year=study_year, cohort_name=level)
    activity, _ = Activity.objects.get_or_create(name=subject_name.upper()[:50])
    
    day_code = day_mapping.get(day, "MON")
    start_time = parse_time_str(time_str)
    start_dt = datetime.combine(datetime.today(), start_time)
    end_time = (start_dt + timedelta(hours=1, minutes=30)).time()
    
    entry, _ = Scheduleentry.objects.get_or_create(
        cohort=cohort,
        activity=activity,
        day=day_code,
        start_time=start_time,
        end_time=end_time,
        entry_type="LESSON"
    )
    return LessonWrapper(entry)

@sync_to_async
def remove_lesson(lesson_id: int):
    Scheduleentry.objects.filter(id=lesson_id).delete()

# --- Gym Slots CRUD ---
@sync_to_async
def get_gym_slots_for_day(day: str):
    day_code = day_mapping.get(day, day)
    entries = Scheduleentry.objects.filter(
        cohort__isnull=True,
        day=day_code,
        activity__name__in=['MALE', 'FEMALE', 'FACULTY', 'CLEANING', 'FACULTY / OPS']
    ).select_related('activity').order_by('start_time')
    return [GymSlotWrapper(e) for e in entries]

@sync_to_async
def get_all_gym_slots():
    entries = Scheduleentry.objects.filter(
        cohort__isnull=True,
        activity__name__in=['MALE', 'FEMALE', 'FACULTY', 'CLEANING', 'FACULTY / OPS']
    ).select_related('activity').order_by('day', 'start_time')
    return [GymSlotWrapper(e) for e in entries]

# --- Bubble Sports CRUD ---
@sync_to_async
def get_bubble_sports_for_day(day: str):
    day_code = day_mapping.get(day, day)
    entries = Scheduleentry.objects.filter(
        cohort__isnull=True,
        day=day_code
    ).exclude(
        activity__name__in=['MALE', 'FEMALE', 'FACULTY', 'CLEANING', 'FACULTY / OPS']
    ).select_related('activity').order_by('start_time')
    return [BubbleWrapper(e) for e in entries]

@sync_to_async
def get_all_bubble_sports():
    entries = Scheduleentry.objects.filter(
        cohort__isnull=True
    ).exclude(
        activity__name__in=['MALE', 'FEMALE', 'FACULTY', 'CLEANING', 'FACULTY / OPS']
    ).select_related('activity').order_by('day', 'start_time')
    return [BubbleWrapper(e) for e in entries]

# --- Contacts CRUD ---
@sync_to_async
def get_contacts_by_category(category: str):
    loc = "ON_CAMPUS" if category == "On Campus" else "OFF_CAMPUS"
    entries = Contact.objects.filter(location=loc)
    return [ContactWrapper(e) for e in entries]

# --- TV Bookings CRUD ---
@sync_to_async
def get_tv_bookings(user_id: int):
    entries = TVBooking.objects.filter(user__telegram_id=user_id).select_related('user')
    return [TVBookingWrapper(e) for e in entries]

@sync_to_async
def get_tv_booking_by_id(booking_id: int):
    try:
        b = TVBooking.objects.select_related('user').get(id=booking_id)
        return TVBookingWrapper(b)
    except TVBooking.DoesNotExist:
        return None

@sync_to_async
def add_tv_booking(user_id: int, lounge_name: str, booker_name: str, booking_date: str, booking_time: str):
    u = UserAccount.objects.get(telegram_id=user_id)
    b = TVBooking.objects.create(
        user=u,
        lounge_name=lounge_name,
        booker_name=booker_name,
        booking_date=booking_date,
        booking_time=booking_time
    )
    return TVBookingWrapper(b)

@sync_to_async
def update_tv_booking(booking_id: int, lounge_name: str, booker_name: str, booking_date: str, booking_time: str):
    try:
        b = TVBooking.objects.get(id=booking_id)
        b.lounge_name = lounge_name
        b.booker_name = booker_name
        b.booking_date = booking_date
        b.booking_time = booking_time
        b.save()
        return TVBookingWrapper(b)
    except TVBooking.DoesNotExist:
        return None

@sync_to_async
def delete_tv_booking(booking_id: int):
    TVBooking.objects.filter(id=booking_id).delete()

# --- Reminders CRUD ---
@sync_to_async
def get_user_reminders(user_id: int):
    entries = Reminder.objects.filter(user__telegram_id=user_id).select_related('user')
    return [ReminderWrapper(e) for e in entries]

@sync_to_async
def get_all_reminders():
    entries = Reminder.objects.all().select_related('user')
    return [ReminderWrapper(e) for e in entries]

@sync_to_async
def add_reminder(user_id: int, r_type: str, subject: str, day: str, time_str: str, offset: int):
    u = UserAccount.objects.get(telegram_id=user_id)
    # Delete duplicate if it exists to mimic get_or_create/override behavior
    Reminder.objects.filter(
        user=u,
        reminder_type=r_type,
        subject_name=subject,
        day=day,
        event_time_str=time_str
    ).delete()
    
    r = Reminder.objects.create(
        user=u,
        reminder_type=r_type,
        subject_name=subject,
        day=day,
        event_time_str=time_str,
        reminder_offset=offset
    )
    return ReminderWrapper(r)

@sync_to_async
def delete_reminder(user_id: int, r_type: str, subject: str, day: str, time_str: str):
    u = UserAccount.objects.get(telegram_id=user_id)
    Reminder.objects.filter(
        user=u,
        reminder_type=r_type,
        subject_name=subject,
        day=day,
        event_time_str=time_str
    ).delete()

@sync_to_async
def add_gym_slot(day: str, start_str: str, end_str: str, session_type: str = "MALE"):
    activity, _ = Activity.objects.get_or_create(name=session_type.upper()[:50])
    day_code = day_mapping.get(day, "MON")
    start_time = parse_time_str(start_str)
    end_time = parse_time_str(end_str)
    
    entry = Scheduleentry.objects.create(
        activity=activity,
        day=day_code,
        start_time=start_time,
        end_time=end_time,
        entry_type="LESSON"
    )
    return entry

@sync_to_async
def add_bubble_sport(day: str, sport: str, time_range_str: str):
    import re
    activity, _ = Activity.objects.get_or_create(name=sport.upper()[:50])
    day_code = day_mapping.get(day, "MON")
    
    parts = re.split(r'[–-]', time_range_str)
    start_time = parse_time_str(parts[0].strip())
    end_time = parse_time_str(parts[1].strip()) if len(parts) > 1 else start_time
    
    entry = Scheduleentry.objects.create(
        activity=activity,
        day=day_code,
        start_time=start_time,
        end_time=end_time,
        entry_type="LESSON"
    )
    return entry
