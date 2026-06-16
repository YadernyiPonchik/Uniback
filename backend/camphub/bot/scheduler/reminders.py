from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from ..crud import get_all_reminders
from datetime import datetime, timedelta

async def check_reminders(bot: Bot):
    now = datetime.now()
    current_day = now.strftime("%A")
    current_date = now.strftime("%d.%m")
    
    reminders = await get_all_reminders()
    
    for r in reminders:
        # Lesson/Gym/Bubble reminders check the weekday name
        if r.reminder_type in ["lesson", "gym", "bubble"]:
            if r.day != current_day:
                continue
        # TV lounge reminders check the date (e.g. "16.06")
        elif r.reminder_type == "tv":
            if r.day != current_date:
                continue
            
        try:
            event_time = datetime.strptime(r.event_time_str, "%H:%M").time()
            event_datetime = datetime.combine(now.date(), event_time)
            trigger_time = event_datetime - timedelta(minutes=r.reminder_offset)
            
            # Check if it is the exact minute
            if trigger_time.hour == now.hour and trigger_time.minute == now.minute:
                if r.reminder_type == "lesson":
                    msg = f"📚 {r.subject_name} starts in {r.reminder_offset} minutes."
                elif r.reminder_type == "gym":
                    msg = f"🏋️ Gym session starts in {r.reminder_offset} minutes."
                elif r.reminder_type == "bubble":
                    msg = f"🏀 {r.subject_name} starts in {r.reminder_offset} minutes."
                else:
                    msg = f"📺 Your Lounge {r.subject_name} booking starts in {r.reminder_offset} minutes."
                    
                await bot.send_message(r.telegram_user_id, msg)
        except Exception as e:
            print(f"Error processing reminder {r.id}: {e}")

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_reminders, 'cron', minute='*', args=[bot])
    scheduler.start()
    return scheduler
