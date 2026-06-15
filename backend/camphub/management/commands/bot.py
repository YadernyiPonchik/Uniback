import asyncio
from aiogram import Bot, Dispatcher, types
import os
from aiogram.filters import CommandStart, Command as TgCommand, StateFilter
from django.core.management.base import BaseCommand
from aiogram.fsm.storage.redis import RedisStorage

from redis.asyncio import Redis
from dotenv import load_dotenv

from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from aiogram.fsm.state import StatesGroup, State
from accounts.models import UserAccount
import logging 
load_dotenv()

YOUR_ADMIN_ID = 6853397362


class Registration(StatesGroup):
    waiting_for_gender = State()

class Command(BaseCommand):
    help = "Starts the Telegram bot"

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        # This starts the async loop
        asyncio.run(self.main())

    async def main(self):
        
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_connection = Redis.from_url(REDIS_URL)
        storage = RedisStorage(redis=redis_connection)

        
        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        bot = Bot(token=TOKEN)
        dp = Dispatcher(storage=storage)

        
        @dp.message(CommandStart())
        async def cmd_start(message: types.Message, state: FSMContext):

            user_exists = await sync_to_async(UserAccount.objects.filter(telegram_id=message.from_user.id).exists)()
            if not user_exists:
                await state.set_state(Registration.waiting_for_gender)
                kb = [
                [types.KeyboardButton(text="Male"),
                types.KeyboardButton(text="Female")]
            ]
                keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
                await message.answer("Welcome! To provide better schedules, please select your gender:", reply_markup=keyboard)
            else:
                await message.answer("Welcome back to UniSpace!")


            # await message.answer(f"Hello! Your ID is: {message.from_user.id}")



            await message.answer(f"Hello, {message.from_user.first_name}! Welcome to UniSpace.")

        @dp.message(StateFilter(Registration.waiting_for_gender))
        async def process_gender(message: types.Message, state: FSMContext):
                if message.text in ["Male", "Female"]:
                # SAVE THE STUDENT TO POSTGRESQL
                    await sync_to_async(UserAccount.objects.create)(
                    email=f"tg_{message.from_user.id}@unispace.com",
                    name=message.from_user.full_name or "Student",
                    telegram_id=message.from_user.id,
                    gender=message.text.upper()
                )

                    await state.clear() # Unlocks the bot for the user
                    await message.answer(f"Registration complete! You are now set as {message.text}.",
                                    reply_markup=types.ReplyKeyboardRemove())
                else:
                    await message.answer("Please use the buttons provided.")

# showing the stats
        @dp.message(TgCommand("stats"))
        async def cmd_stats(message: types.Message):
                if message.from_user.id != YOUR_ADMIN_ID:
                    await message.answer("❌ Access denied.")
                    return
                total = await  sync_to_async(UserAccount.objects.count)()
                males= await sync_to_async(UserAccount.objects.filter(gender= 'MALE').count)()
                females= await sync_to_async(UserAccount.objects.filter(gender= 'FEMALE').count)()

                response = (
                    "📊 **UniSpace Analytics**\n\n"
                    f"Total Users: {total}\n"
                    f"Male Students: {males}\n"
                    f"Female Students: {females}\n"
                )

                await message.answer(response, parse_mode= "Markdown")
        
        @dp.message(TgCommand("help"))  
        async def cmd_help(message: types.Message):
            await message.answer("I can help you check the Gym or Lesson schedule.")

        self.stdout.write(self.style.SUCCESS("Bot is polling..."))
        await dp.start_polling(bot)
