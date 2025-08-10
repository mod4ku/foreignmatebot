import logging
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from db import save_user, get_next_profile, set_like, is_match, ban_user, user_exists, DB_NAME, get_profiles_list
from config import IMGUR_BASE_URL, DEFAULT_PROFILE_IMAGE, ADMIN_IDS
import sqlite3


router = Router()
logger = logging.getLogger("StudyBot")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("INFO:StudyBot:%(message)s")
handler.setFormatter(formatter)
logger.handlers = [handler]

class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()
    search_gender = State()
    photo = State()
    from_country = State()
    to_country = State()
    exams = State()
    ielts_or_toefl = State()
    ielts_score = State()
    toefl_score = State()
    sat_taken = State()
    sat_score = State()
    description = State()

@router.message(Command("start"))
async def start_cmd(message: Message, state: FSMContext):
    logger.info(f"Обновление: /start от пользователя {message.from_user.id}")
    if user_exists(message.from_user.id):
        await message.answer("👋 С возвращением! Сейчас покажу анкеты...")
        await next_profile(message)
        return
    image_url = IMGUR_BASE_URL + DEFAULT_PROFILE_IMAGE
    await message.answer_photo(photo=image_url, caption=f"👋 Привет, {message.from_user.first_name}!")
    await message.answer("Добро пожаловать в StudyBot — сервис для поиска друзей, поступающих за границу!\nДавай создадим твою анкету. Как тебя зовут?")
    await state.set_state(Form.name)

@router.message(StateFilter(Form.name))
async def name_step(message: Message, state: FSMContext):
    logger.info(f"Обновление: имя от {message.from_user.id}: {message.text}")
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    await message.answer("Сколько тебе лет?")

@router.message(StateFilter(Form.age))
async def age_step(message: Message, state: FSMContext):
    logger.info(f"Обновление: возраст от {message.from_user.id}: {message.text}")
    await state.update_data(age=message.text)
    await state.set_state(Form.gender)
    await message.answer("Укажи свой пол (м/ж):")

@router.message(StateFilter(Form.gender))
async def gender_step(message: Message, state: FSMContext):
    logger.info(f"Обновление: пол от {message.from_user.id}: {message.text}")
    await state.update_data(gender=message.text)
    await state.set_state(Form.search_gender)
    await message.answer("Кого ты хочешь найти? (м/ж/оба):")

@router.message(StateFilter(Form.search_gender))
async def search_gender_step(message: Message, state: FSMContext):
    logger.info(f"Обновление: кого ищет {message.from_user.id}: {message.text}")
    await state.update_data(search_gender=message.text)
    await state.set_state(Form.photo)
    await message.answer("Пришли своё фото.")

@router.message(StateFilter(Form.photo))
async def photo_step(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, пришли фото.")
        return
    logger.info(f"Обновление: фото от {message.from_user.id}")
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(Form.from_country)
    await message.answer("Из какой ты страны?")

@router.message(StateFilter(Form.from_country))
async def from_country_step(message: Message, state: FSMContext):
    logger.info(f"Обновление: страна {message.from_user.id}: {message.text}")
    await state.update_data(from_country=message.text)
    await state.set_state(Form.to_country)
    await message.answer("В какую страну хочешь поступать?")

@router.message(StateFilter(Form.to_country))
async def to_country_step(message: Message, state: FSMContext):
    logger.info(f"Обновление: поступление в {message.text} от {message.from_user.id}")
    await state.update_data(to_country=message.text)
    await exams_step(message, state)

@router.message(StateFilter(Form.exams))
async def exams_step(message: Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="IELTS", callback_data="exam:ielts")],
        [types.InlineKeyboardButton(text="TOEFL", callback_data="exam:toefl")],
        [types.InlineKeyboardButton(text="Ещё не сдавал", callback_data="exam:none")]
    ])
    await message.answer("Какой языковой экзамен ты сдавал?", reply_markup=markup)

@router.callback_query(lambda c: c.data.startswith("exam:"))
async def exam_choice_callback(call: types.CallbackQuery, state: FSMContext):
    exam = call.data.split(":")[1]
    if exam == "ielts":
        await state.update_data(language_exam="IELTS", exams="IELTS")
        await call.message.edit_text("Введи свой балл за IELTS (от 4.0 до 9.0, шаг 0.5):")
        await state.set_state(Form.ielts_score)
    elif exam == "toefl":
        await state.update_data(language_exam="TOEFL", exams="TOEFL")
        await call.message.edit_text("Введи свой балл за TOEFL (от 30 до 120):")
        await state.set_state(Form.toefl_score)
    else:
        await state.update_data(language_exam="None", exams="None")
        await ask_sat_callback(call, state)
        await state.set_state(Form.sat_taken)


@router.message(StateFilter(Form.ielts_score))
async def ielts_score_step(message: Message, state: FSMContext):
    try:
        score = float(message.text.replace(",", "."))
        if score < 4.0 or score > 9.0 or round(score * 2) != score * 2:
            raise ValueError
        await state.update_data(ielts_score=score)
        await ask_sat_message(message, state)
    except ValueError:
        await message.answer("Некорректный балл. Введи значение от 4.0 до 9.0 с шагом 0.5.")

@router.message(StateFilter(Form.toefl_score))
async def toefl_score_step(message: Message, state: FSMContext):
    try:
        score = int(message.text)
        if score < 30 or score > 120:
            raise ValueError
        await state.update_data(toefl_score=score)
        await ask_sat_message(message, state)
    except ValueError:
        await message.answer("Некорректный балл. Введи число от 30 до 120.")

async def ask_sat_message(message: Message, state: FSMContext):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Да", callback_data="sat:yes")],
        [types.InlineKeyboardButton(text="Нет", callback_data="sat:no")]
    ])
    await message.answer("Сдавал ли ты SAT?", reply_markup=markup)
    await state.set_state(Form.sat_taken)

async def ask_sat_callback(call: types.CallbackQuery, state: FSMContext):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Да", callback_data="sat:yes")],
        [types.InlineKeyboardButton(text="Нет", callback_data="sat:no")]
    ])
    await call.message.edit_text("Сдавал ли ты SAT?", reply_markup=markup)
    await state.set_state(Form.sat_taken)

@router.callback_query(lambda c: c.data.startswith("sat:"))
async def sat_choice_callback(call: types.CallbackQuery, state: FSMContext):
    if call.data == "sat:yes":
        await call.message.edit_text("Введи свой балл за SAT (от 400 до 1600):")
        await state.set_state(Form.sat_score)
    else:
        await state.update_data(sat_score=None)
        await call.message.edit_text("Теперь расскажи немного о себе:")
        await state.set_state(Form.description)

@router.message(StateFilter(Form.sat_score))
async def sat_score_step(message: Message, state: FSMContext):
    try:
        score = int(message.text)
        if score < 400 or score > 1600:
            raise ValueError
        await state.update_data(sat_score=score)
        await ask_description(message, state)
    except ValueError:
        await message.answer("Некорректный балл. Введи число от 400 до 1600.")

async def ask_description(message: Message, state: FSMContext):
    await message.answer("Теперь расскажи немного о себе:")
    await state.set_state(Form.description)

@router.message(StateFilter(Form.description))
async def description_step(message: Message, state: FSMContext):
    logger.info(f"Обновление: описание от {message.from_user.id}")
    await state.update_data(description=message.text)
    data = await state.get_data()
    save_user(data, message.from_user.id)
    await message.answer("✅ Анкета создана! Чтобы начать просмотр других пользователей, напиши /next")
    await state.clear()

@router.message(Command("next"))
async def next_profile(message: Message):
    from_id = message.from_user.id
    profiles = get_profiles_list(from_id)

    if not profiles:
        await message.answer("Анкет больше нет.")
        return

    for profile in profiles:
        (
            user_id, name, age, gender, search_gender, photo,
            from_c, to_c, exams, desc, lang_exam,
            ielts_score, toefl_score, sat_score, is_active
        ) = profile

        if int(user_id) == int(from_id):
            continue
        if int(is_active) != 1:
            continue

        # Кнопки
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[  
            types.InlineKeyboardButton(text="❤", callback_data=f"like:{user_id}"),
            types.InlineKeyboardButton(text="👎", callback_data=f"dislike:{user_id}")
        ]])

        exam_details = exams
        if exams == "IELTS" and ielts_score:
            exam_details += f" ({ielts_score})\nSAT: ({sat_score})"
        elif exams == "TOEFL" and toefl_score:
            exam_details += f" ({toefl_score})\nSAT: ({sat_score})"

        await message.answer_photo(
            photo=photo,
            caption=(
                f"Имя: {name}\n"
                f"Возраст: {age}\n"
                f"Пол: {gender}\n"
                f"Из: {from_c}\n"
                f"В: {to_c}\n"
                f"Экзамены: {exam_details}\n"
                f"Описание: {desc}"
            ),
            reply_markup=keyboard
        )

        set_like(from_id, user_id, 'skipped')

        return

    await message.answer("Анкет больше нет.")

@router.callback_query(lambda c: c.data.startswith("like:"))
async def like_callback(call: types.CallbackQuery):
    from_id = call.from_user.id
    to_id = int(call.data.split(":")[1])
    set_like(from_id, to_id, 'like')
    logger.info(f"Лайк: {from_id} -> {to_id}")
    if is_match(from_id, to_id):
        try:
            user = await call.bot.get_chat(to_id)
            username = f"@{user.username}" if user.username else f"ID: {to_id}"
        except:
            username = f"ID: {to_id}"
        await call.message.answer(f"💫 У вас совпадение! Вот ник: {username}")
    await call.message.delete()
    await next_profile(call.message)
    
@router.callback_query(lambda c: c.data.startswith("dislike:"))
async def dislike_callback(call: types.CallbackQuery):
    from_id = call.from_user.id
    to_id = int(call.data.split(":")[1])
    set_like(from_id, to_id, 'dislike')
    logger.info(f"Дизлайк: {from_id} -> {to_id}")
    await call.message.delete()
    await next_profile(call.message)

@router.message(Command("ban"))
async def admin_ban(message: Message):
    if message.from_user.id in ADMIN_IDS:
        parts = message.text.split()
        if len(parts) == 2:
            ban_user(int(parts[1]))
            logger.info(f"Бан: админ {message.from_user.id} забанил {parts[1]}")
            await message.answer("Пользователь забанен")
