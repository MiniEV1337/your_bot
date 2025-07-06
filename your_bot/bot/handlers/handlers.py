from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ..keyboards import (
    get_main_menu,
    get_settings_menu,
    get_subscription_menu,
    get_category_selector
)
from bot.user_manager import (
    set_subscription,
    get_subscription,
    toggle_night_news,
    save_favorites
)
from database import Session, User
import os

router = Router()
ADMIN_ID = os.getenv("ADMIN_ID")

user_temp_selection: dict[int, list[str]] = {}

class CategorySelect(StatesGroup):
    selecting = State()

class Broadcast(StatesGroup):
    waiting_for_photo = State()
    waiting_for_caption = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    is_admin = str(message.from_user.id) == str(ADMIN_ID)
    await message.answer(
        "Привет! 👋 Выбери интересующую категорию или перейди в настройки:",
        reply_markup=get_main_menu() if not is_admin else get_settings_menu(is_admin=True)
    )

@router.callback_query(F.data.in_([
    "politics", "technology", "sports", "economy", "culture", "world",
    "science", "gaming", "cinema", "medicine"
]))
async def handle_category(callback: CallbackQuery):
    category = callback.data
    await callback.message.answer(f"🔎 Ищу свежие новости по теме: *{category}*")
    await callback.answer()

@router.callback_query(F.data == "open_settings")
async def open_settings(callback: CallbackQuery):
    is_admin = str(callback.from_user.id) == str(ADMIN_ID)
    await callback.message.edit_text("⚙️ Настройки:", reply_markup=get_settings_menu(is_admin))
    await callback.answer()

@router.callback_query(F.data == "subscription")
async def open_subscription_menu(callback: CallbackQuery):
    await callback.message.edit_text("💎 Выберите уровень подписки:", reply_markup=get_subscription_menu())
    await callback.answer()

@router.callback_query(F.data.in_(["subscribe_1", "subscribe_2"]))
async def handle_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    level = 1 if callback.data == "subscribe_1" else 2
    set_subscription(user_id, level)
    await callback.message.answer(f"✅ Подписка уровня {level} активирована!")
    await callback.answer()

@router.callback_query(F.data == "toggle_night")
async def toggle_night_news_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    new_state = toggle_night_news(user_id)
    message = "🌙 Ночной режим включён. Вы будете получать новости ночью." if new_state \
        else "🌙 Ночной режим выключен. Новости приходят только днём."
    await callback.message.answer(message)
    await callback.answer()

@router.callback_query(F.data == "my_stats")
async def show_user_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    level = get_subscription(user_id)
    await callback.message.answer(f"📊 Ваша подписка: уровень {level}\n(Остальная статистика будет позже.)")
    await callback.answer()

@router.callback_query(F.data.in_(["back_to_main", "back_to_settings"]))
async def go_back(callback: CallbackQuery):
    is_admin = str(callback.from_user.id) == str(ADMIN_ID)
    if callback.data == "back_to_main":
        await callback.message.edit_text("🔙 Возврат в главное меню.", reply_markup=get_main_menu())
    elif callback.data == "back_to_settings":
        await callback.message.edit_text("⚙️ Настройки:", reply_markup=get_settings_menu(is_admin))
    await callback.answer()

@router.callback_query(F.data == "select_favorites")
async def begin_category_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    level = get_subscription(user_id)
    limit = 3 if level == 1 else 6
    selected = []
    user_temp_selection[user_id] = selected
    await state.set_state(CategorySelect.selecting)
    await callback.message.edit_text(
        f"Выберите до {limit} любимых тем:",
        reply_markup=get_category_selector(selected, limit)
    )
    await callback.answer()

@router.callback_query(CategorySelect.selecting, F.data.startswith("toggle_cat:"))
async def toggle_category(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    code = callback.data.split(":")[1]
    selected = user_temp_selection.get(user_id, [])
    level = get_subscription(user_id)
    limit = 3 if level == 1 else 6

    if code in selected:
        selected.remove(code)
    elif len(selected) < limit:
        selected.append(code)

    user_temp_selection[user_id] = selected
    await callback.message.edit_reply_markup(reply_markup=get_category_selector(selected, limit))
    await callback.answer()

@router.callback_query(CategorySelect.selecting, F.data == "save_categories")
async def save_selected_categories(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    selected = user_temp_selection.get(user_id, [])
    save_favorites(user_id, selected)
    await state.clear()
    await callback.message.edit_text("✅ Темы сохранены!", reply_markup=get_settings_menu())
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    if str(callback.from_user.id) != str(ADMIN_ID):
        await callback.message.answer("⛔ Только для администратора.")
        return
    await state.set_state(Broadcast.waiting_for_photo)
    await callback.message.answer("📷 Отправь изображение для рассылки (jpg/png)")
    await callback.answer()

@router.message(Broadcast.waiting_for_photo, F.photo)
async def receive_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(Broadcast.waiting_for_caption)
    await message.answer("✍️ Теперь отправь подпись для фото (она будет под изображением)")

@router.message(Broadcast.waiting_for_caption)
async def receive_caption_and_send(message: Message, state: FSMContext):
    bot = message.bot
    data = await state.get_data()
    photo_id = data.get("photo")
    caption = message.text
    count = 0

    session = Session()
    for user in session.query(User).all():
        try:
            await bot.send_photo(user.telegram_id, photo_id, caption=caption)
            count += 1
        except Exception:
            continue
    session.close()
    await message.answer(f"✅ Рассылка завершена. Отправлено {count} пользователям.")
    await state.clear()
