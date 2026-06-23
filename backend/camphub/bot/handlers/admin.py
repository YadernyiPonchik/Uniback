from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..crud import get_user, add_lesson, add_gym_slot, add_bubble_sport

router = Router()

class AdminState(StatesGroup):
    waiting_for_lesson_data = State()
    waiting_for_gym_data = State()
    waiting_for_bubble_data = State()

async def is_admin(user_id: int) -> bool:
    user = await get_user(user_id)
    return user and (user.is_staff or user.is_superuser or user_id == 6853397362)

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not await is_admin(message.from_user.id):
        await message.answer("You do not have permission to access the admin panel.")
        return
        
    builder = InlineKeyboardBuilder()
    builder.button(text="Add Lesson", callback_data="admin_add_lesson")
    builder.button(text="Add Gym Slot", callback_data="admin_add_gym")
    builder.button(text="Add Bubble Sport", callback_data="admin_add_bubble")
    builder.adjust(1)
    
    await message.answer("Admin Panel:", reply_markup=builder.as_markup())

@router.callback_query(F.data == "admin_add_lesson")
async def admin_add_lesson(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("Enter lesson data in format:\nLevel, Day, Time, Subject\nExample: Freshman, Monday, 09:00, Math")
    await state.set_state(AdminState.waiting_for_lesson_data)

@router.message(AdminState.waiting_for_lesson_data)
async def save_lesson(message: Message, state: FSMContext):
    try:
        level, day, time_str, subject = [x.strip() for x in message.text.split(",")]
        await add_lesson(level, day, time_str, subject)
        await message.answer("Lesson added successfully.")
    except Exception as e:
        await message.answer("Invalid format. Please try again from the /admin menu.")
    await state.clear()

@router.callback_query(F.data == "admin_add_gym")
async def admin_add_gym(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("Enter gym data in format:\nDay, Start Time, End Time, Session Type\nExample: Monday, 07:00, 08:30, Male")
    await state.set_state(AdminState.waiting_for_gym_data)

@router.message(AdminState.waiting_for_gym_data)
async def save_gym(message: Message, state: FSMContext):
    try:
        day, start, end, session_type = [x.strip() for x in message.text.split(",")]
        await add_gym_slot(day, start, end, session_type)
        await message.answer("Gym slot added successfully.")
    except Exception as e:
        # Fallback to default Male if session type not provided
        try:
            day, start, end = [x.strip() for x in message.text.split(",")]
            await add_gym_slot(day, start, end, "Male")
            await message.answer("Gym slot added successfully.")
        except Exception:
            await message.answer("Invalid format. Please try again from the /admin menu.")
    await state.clear()

@router.callback_query(F.data == "admin_add_bubble")
async def admin_add_bubble(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("Enter bubble sport data in format:\nDay, Sport, Time Range\nExample: Monday, Basketball, 18:00 - 20:00")
    await state.set_state(AdminState.waiting_for_bubble_data)

@router.message(AdminState.waiting_for_bubble_data)
async def save_bubble(message: Message, state: FSMContext):
    try:
        day, sport, time_str = [x.strip() for x in message.text.split(",")]
        await add_bubble_sport(day, sport, time_str)
        await message.answer("Bubble sport added successfully.")
    except Exception as e:
        await message.answer("Invalid format. Please try again from the /admin menu.")
    await state.clear()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != 6853397362:
        await message.answer("❌ Access denied.")
        return
    from accounts.models import UserAccount
    from asgiref.sync import sync_to_async
    total = await sync_to_async(UserAccount.objects.count)()
    males = await sync_to_async(lambda: UserAccount.objects.filter(gender='MALE').count())()
    females = await sync_to_async(lambda: UserAccount.objects.filter(gender='FEMALE').count())()

    response = (
        "📊 **UniSpace Analytics**\n\n"
        f"Total Users: {total}\n"
        f"Male Students: {males}\n"
        f"Female Students: {females}\n"
    )

    await message.answer(response, parse_mode="Markdown")
