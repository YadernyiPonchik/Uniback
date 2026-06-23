import os
import sqlite3
import re
from datetime import datetime, time, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from camphub.models import StudyYear, Cohort, Activity, Scheduleentry, Contact


class Command(BaseCommand):
    help = "Seeds the Django database with lessons, gym, and sports data from the bot's SQLite database"

    def handle(self, *args, **options):
        # Allow configuring the SQLite source via environment variable or Django settings.
        db_path = os.environ.get("SEED_SQLITE_PATH") or getattr(
            settings, "SEED_SQLITE_PATH", "/home/student/Desktop/Project/campus_assistant.db")
        self.stdout.write(f"Connecting to SQLite database at {db_path}...")

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
        except Exception as e:
            self.stderr.write(f"Failed to connect to SQLite: {e}")
            return

        # 1. Create a default Study Year
        study_year, _ = StudyYear.objects.get_or_create(year_name="2025-2026")

        day_mapping = {
            "Monday": "MON",
            "Tuesday": "TUE",
            "Wednesday": "WED",
            "Thursday": "THU",
            "Friday": "FRI",
            "Saturday": "SAT",
            "Sunday": "SUN"
        }

        def parse_time(t_str):
            t_str = t_str.strip()
            # Handle formats like "09:00" or "9:00"
            for fmt in ("%H:%M", "%I:%M %p", "%I:%M%p", "%H:%M:%S"):
                try:
                    dt = datetime.strptime(t_str, fmt)
                    return time(dt.hour, dt.minute)
                except ValueError:
                    continue
            return time(9, 0)  # Fallback

        # --- A. Migrate Lessons ---
        self.stdout.write("Migrating Lessons...")
        cursor.execute(
            "SELECT academic_level, day_of_week, time_str, subject_name FROM lessons;")
        lessons = cursor.fetchall()

        lesson_count = 0
        for level, day_name, time_str, subject in lessons:
            cohort, _ = Cohort.objects.get_or_create(
                study_year=study_year,
                cohort_name=level
            )

            # Map activity
            activity_name = subject.upper()
            activity, _ = Activity.objects.get_or_create(
                name=activity_name[:50])  # limit to max_length

            day_code = day_mapping.get(day_name, "MON")
            start_time = parse_time(time_str)

            # Estimate end time (1.5 hours later)
            start_dt = datetime.combine(datetime.today(), start_time)
            end_time = (start_dt + timedelta(hours=1, minutes=30)).time()

            # Create schedule entry
            Scheduleentry.objects.get_or_create(
                cohort=cohort,
                activity=activity,
                day=day_code,
                start_time=start_time,
                end_time=end_time,
                entry_type="LESSON"
            )
            lesson_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully migrated {lesson_count} lessons."))

        # --- B. Migrate Gym Slots ---
        self.stdout.write("Migrating Gym Slots...")
        cursor.execute(
            "SELECT day_of_week, start_time_str, end_time_str, session_type FROM gym_slots;")
        gym_slots = cursor.fetchall()

        gym_count = 0
        for day_name, start_str, end_str, session in gym_slots:
            activity_name = session.upper()
            activity, _ = Activity.objects.get_or_create(
                name=activity_name[:50])

            day_code = day_mapping.get(day_name, "MON")
            start_time = parse_time(start_str)
            end_time = parse_time(end_str)

            Scheduleentry.objects.get_or_create(
                activity=activity,
                day=day_code,
                start_time=start_time,
                end_time=end_time,
                entry_type="LESSON"  # Treating gym slots as lessons for general schedule queries
            )
            gym_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully migrated {gym_count} gym slots."))

        # --- C. Migrate Bubble Sports ---
        self.stdout.write("Migrating Bubble Sports...")
        cursor.execute(
            "SELECT day_of_week, sport_name, time_str FROM bubble_sports;")
        bubble_slots = cursor.fetchall()

        bubble_count = 0
        for day_name, sport, duration_str in bubble_slots:
            activity_name = sport.upper()
            activity, _ = Activity.objects.get_or_create(
                name=activity_name[:50])

            day_code = day_mapping.get(day_name, "MON")

            # Parse duration_str like "10:00 – 12:00" or "18:00 – 21:00"
            parts = re.split(r'[–-]', duration_str)
            start_str = parts[0].strip()
            end_str = parts[1].strip() if len(parts) > 1 else start_str

            start_time = parse_time(start_str)
            end_time = parse_time(end_str)

            Scheduleentry.objects.get_or_create(
                activity=activity,
                day=day_code,
                start_time=start_time,
                end_time=end_time,
                entry_type="LESSON"
            )
            bubble_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully migrated {bubble_count} bubble sports slots."))

        # --- D. Migrate Contacts ---
        self.stdout.write("Migrating Contacts...")
        cursor.execute("SELECT category, name, phone, details FROM contacts;")
        contacts = cursor.fetchall()

        contact_count = 0
        for category, name, phone, details in contacts:
            # category is "On Campus" or "Off Campus" -> Map to location "ON_CAMPUS" or "OFF_CAMPUS"
            location_val = "ON_CAMPUS"
            if category.lower() == "off campus":
                location_val = "OFF_CAMPUS"

            # clean phone to int
            phone_digits = ''.join(c for c in phone if c.isdigit())
            phone_num = int(phone_digits) if phone_digits else 0

            Contact.objects.get_or_create(
                full_name=name,
                role=details or "Staff",
                phone_number=phone_num,
                sector="ADMIN",  # Default sector
                location=location_val
            )
            contact_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully migrated {contact_count} contacts."))

        conn.close()
        self.stdout.write(self.style.SUCCESS("All migrations complete!"))
