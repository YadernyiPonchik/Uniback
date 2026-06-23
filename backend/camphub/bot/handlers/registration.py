from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ..keyboards.inline import get_academic_level_kb
from ..keyboards.reply import get_main_menu
from ..crud import get_user, create_user, update_user_level

router = Router()

class RegistrationState(StatesGroup):
    waiting_for_gender = State()
    waiting_for_level = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await get_user(message.from_user.id)
    if user:
        await message.answer(
            f"Welcome back, {message.from_user.first_name or 'Student'}! 🌟\n"
            f"Here is your MAIN MENU. Use the buttons below to navigate.",
            reply_markup=get_main_menu()
        )
    else:
        # Start combined registration flow
        await state.set_state(RegistrationState.waiting_for_gender)
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Male"), KeyboardButton(text="Female")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(
            "🌟 <b>Welcome to the UCA Campus Assistant!</b> 🎓\n\n"
            "I'm here to help you navigate campus life seamlessly.\n"
            "To personalize your experience, please select your gender first: 👇",
            reply_markup=kb,
            parse_mode="HTML"
        )

@router.message(RegistrationState.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    gender_text = message.text.strip()
    if gender_text not in ["Male", "Female"]:
        await message.answer("Please use the buttons provided to select your gender (Male/Female).")
        return
        
    await state.update_data(gender=gender_text)
    await state.set_state(RegistrationState.waiting_for_level)
    
    # Hide the reply keyboard
    await message.answer(
        "Gender recorded! ✅",
        reply_markup=ReplyKeyboardRemove()
    )
    # Ask for Academic Level
    await message.answer(
        "Now, please select your current academic level below: 👇",
        reply_markup=get_academic_level_kb()
    )

@router.callback_query(F.data.startswith("level_"))
async def process_level_selection(callback: CallbackQuery, state: FSMContext):
    level = callback.data.split("_")[1]
    current_state = await state.get_state()
    
    if current_state == RegistrationState.waiting_for_level.state:
        # New user registration completion
        data = await state.get_data()
        gender = data.get("gender", "Male")
        
        await create_user(
            telegram_id=callback.from_user.id,
            name=callback.from_user.full_name or "Student",
            gender=gender,
            cohort_name=level
        )
        await state.clear()
        
        await callback.message.edit_text(
            f"✅ Registration complete!\n"
            f"👤 Gender: {gender}\n"
            f"🎓 Academic level: {level}"
        )
    else:
        # Existing user updating their level
        await update_user_level(callback.from_user.id, level)
        await callback.message.edit_text(f"🎓 Academic level updated to: {level}")
        
    await callback.message.answer(
        "Here is your MAIN MENU. Use the buttons below to navigate.",
        reply_markup=get_main_menu()
    )
    await callback.answer()
