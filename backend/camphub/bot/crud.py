from asgiref.sync import sync_to_async
from django.conf import settings
from accounts.models import UserAccount
from camphub.models import (
    Cohort, Subject, ClassEvent, GymEvent, Event,
    Instructor, Contact, TVBooking, Reminder, StudyYear
)
from datetime import datetime, time, timedelta

day_mapping = {
    "Monday": "MON", "Tuesday": "TUE", "Wednesday": "WED", "Thursday": "THU",
    "Friday": "FRI", "Saturday": "SAT", "Sunday": "SUN",
    "MON": "MON", "TUE": "TUE", "WED": "WED", "THU": "THU", "FRI": "FRI", "SAT": "SAT", "SUN": "SUN"
}

day_reverse = {
    "MON": "Monday", "TUE": "Tuesday", "WED": "Wednesday", "THU": "Thursday",
    "FRI": "Friday", "SAT": "Saturday", "SUN": "Sunday"
}

# Compatibility wrappers to mimic SQLAlchemy model objects


class LessonWrapper:
    def __init__(self, entry):
        self.id = entry.id
        self.academic_level = entry.cohort.cohort_name if entry.cohort else ""
        self.day_of_week = day_reverse.get(entry.day, entry.day)
        self.time_str = entry.start_time.strftime(
            "%H:%M") if entry.start_time else "09:00"
        self.subject_name = entry.subject.name.title() if entry.subject else ""


class GymSlotWrapper:
    def __init__(self, entry):
        self.id = entry.id
        self.day_of_week = day_reverse.get(entry.day, entry.day)
        self.start_time_str = entry.start_time.strftime(
            "%H:%M") if entry.start_time else ""
        self.end_time_str = entry.end_time.strftime(
            "%H:%M") if entry.end_time else ""
        self.session_type = entry.gender.title() if entry.gender else ""


class BubbleWrapper:
    def __init__(self, entry):
        self.id = entry.id
        self.day_of_week = day_reverse.get(entry.day, entry.day)
        self.sport_name = entry.status.replace(
            "_", " ").title() if entry.status else ""
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
        u = UserAccount.objects.select_related(
            'cohort').get(telegram_id=telegram_id)
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

# --- Lessons CRUD (now uses ClassEvent) ---


@sync_to_async
def get_lessons_for_day(level: str, day: str):
    day_code = day_mapping.get(day, day)
    entries = ClassEvent.objects.filter(
        cohort__cohort_name=level,
        day=day_code,
    ).select_related('cohort', 'subject').order_by('start_time')
    return [LessonWrapper(e) for e in entries]


@sync_to_async
def get_weekly_lessons(level: str):
    entries = ClassEvent.objects.filter(
        cohort__cohort_name=level,
    ).select_related('cohort', 'subject').order_by('day', 'start_time')
    return [LessonWrapper(e) for e in entries]


@sync_to_async
def add_lesson(level: str, day: str, time_str: str, subject_name: str):
    study_year, _ = StudyYear.objects.get_or_create(year_name="2025-2026")
    cohort, _ = Cohort.objects.get_or_create(
        study_year=study_year, cohort_name=level)
    subject, _ = Subject.objects.get_or_create(name=subject_name.title()[:50])
    instructor, _ = Instructor.objects.get_or_create(
        first_name="TBD", last_name="TBD",
        defaults={"status": "ON_CAMPUS"}
    )

    day_code = day_mapping.get(day, "MON")
    start_time = parse_time_str(time_str)
    start_dt = datetime.combine(datetime.today(), start_time)
    end_time = (start_dt + timedelta(hours=1, minutes=30)).time()

    entry, _ = ClassEvent.objects.get_or_create(
        cohort=cohort,
        subject=subject,
        instructor=instructor,
        day=day_code,
        start_time=start_time,
        end_time=end_time,
        defaults={"status": "CLASS"}
    )
    return LessonWrapper(entry)


@sync_to_async
def remove_lesson(lesson_id: int):
    ClassEvent.objects.filter(id=lesson_id).delete()

# --- Gym Slots CRUD (now uses GymEvent) ---


@sync_to_async
def get_gym_slots_for_day(day: str):
    day_code = day_mapping.get(day, day)
    entries = GymEvent.objects.filter(
        day=day_code,
    ).order_by('start_time')
    return [GymSlotWrapper(e) for e in entries]


@sync_to_async
def get_all_gym_slots():
    entries = GymEvent.objects.all().order_by('day', 'start_time')
    return [GymSlotWrapper(e) for e in entries]


@sync_to_async
def add_gym_slot(day: str, start_str: str, end_str: str, session_type: str = "MALE"):
    day_code = day_mapping.get(day, "MON")
    start_time = parse_time_str(start_str)
    end_time = parse_time_str(end_str)

    entry = GymEvent.objects.create(
        day=day_code,
        start_time=start_time,
        end_time=end_time,
        status="GYM",
        gender=session_type.upper()
    )
    return entry

# --- Bubble Sports CRUD (now uses Event with status=BUBBLE) ---


@sync_to_async
def get_bubble_sports_for_day(day: str):
    day_code = day_mapping.get(day, day)
    entries = Event.objects.filter(
        day=day_code,
        status="BUBBLE",
    ).order_by('start_time')
    # Exclude GymEvent subclass entries
    entries = [e for e in entries if not hasattr(e, 'gymevent')]
    return [BubbleWrapper(e) for e in entries]


@sync_to_async
def get_all_bubble_sports():
    entries = Event.objects.filter(
        status="BUBBLE",
    ).order_by('day', 'start_time')
    entries = [e for e in entries if not hasattr(e, 'gymevent')]
    return [BubbleWrapper(e) for e in entries]


@sync_to_async
def add_bubble_sport(day: str, sport: str, time_range_str: str):
    import re
    day_code = day_mapping.get(day, "MON")

    parts = re.split(r'[–-]', time_range_str)
    start_time = parse_time_str(parts[0].strip())
    end_time = parse_time_str(parts[1].strip()) if len(
        parts) > 1 else start_time

    entry = Event.objects.create(
        day=day_code,
        start_time=start_time,
        end_time=end_time,
        status="BUBBLE"
    )
    return entry

# --- Contacts CRUD ---


@sync_to_async
def get_contacts_by_category(category: str):
    loc = "ON_CAMPUS" if category == "On Campus" else "OFF_CAMPUS"
    entries = Contact.objects.filter(location=loc)
    return [ContactWrapper(e) for e in entries]

# --- TV Bookings CRUD ---


@sync_to_async
def get_tv_bookings(user_id: int):
    entries = TVBooking.objects.filter(
        user__telegram_id=user_id).select_related('user_id')
    return [TVBookingWrapper(e) for e in entries]


@sync_to_async
def get_tv_booking_by_id(booking_id: int):
    try:
        b = TVBooking.objects.select_related('user_id').get(id=booking_id)
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
    entries = Reminder.objects.filter(
        user__telegram_id=user_id).select_related('user_id')
    return [ReminderWrapper(e) for e in entries]


@sync_to_async
def get_all_reminders():
    entries = Reminder.objects.all().select_related('user_id')
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
