from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from ..keyboards.inline import get_contacts_submenu_kb
from ..crud import get_contacts_by_category

router = Router()

@router.message(F.text == "📞 Contacts")
async def contacts_menu(message: Message):
    await message.answer("📞 Contacts Menu:", reply_markup=get_contacts_submenu_kb())

@router.callback_query(F.data.startswith("contacts_"))
async def show_contacts(callback: CallbackQuery):
    cat_id = callback.data.split("_", 1)[1]
    category = "On Campus" if cat_id == "on_campus" else "Off Campus"

    contacts = await get_contacts_by_category(category)

    if not contacts:
        await callback.message.edit_text(f"No {category} contacts available.")
        return

    text = f"📞 {category} Contacts:\n\n"
    for c in contacts:
        text += f"*{c.name}*\n"
        text += f"Phone: {c.phone}\n"
        if c.details:
            text += f"Details: {c.details}\n"
        text += "\n"

    await callback.message.edit_text(text, parse_mode="Markdown")
