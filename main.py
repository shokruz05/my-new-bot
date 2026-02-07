import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Состояния для опроса
class Order(StatesGroup):
    waiting_for_topic = State()
    waiting_for_pages = State()
    waiting_for_site_details = State()
    waiting_for_bot_details = State()
    waiting_for_bot_token = State()
    waiting_for_tech_problem = State()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8239382195  # Твой Telegram ID
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Словарь всех текстов на 3 языках
MESSAGES = {
    'uz': {
        'services': "Xizmatni tanlang:",
        'topic': "Mavzu nima haqida?",
        'pages': "Necha varaq (list) bo'lishi kerak?",
        'site_q': "Qanday mavzuda sayt yaratmoqchisiz?",
        'bot_q': "Bot qanday funksiyalarni bajarishi kerak?",
        'bot_inst': "Avval @BotFather orqali bot oching va menga TOKEN yuboring.",
        'problem': "Muammoingizni yozib qoldiring:",
        'done': "Sizning so'rovingiz adminga yuborildi. Tez orada aloqaga chiqamiz!",
        'contact_btn': "Admin bilan bog'lanish",
        'btn_pres': "Презентация 📽", 'btn_kurs': "Курсовая 📚", 'btn_sam': "Самостоятельная 📝",
        'btn_site': "Sayt yaratish 🌐", 'btn_bot': "Bot yaratish 🤖", 
        'btn_help': "PK/Tel yordam 🛠", 'btn_admin': "Admin bilan aloqa 👨‍💻"
    },
    'ru': {
        'services': "Выберите услугу:",
        'topic': "На какую тему?",
        'pages': "Сколько листов должно быть?",
        'site_q': "На какую тему вы хотите создать сайт?",
        'bot_q': "Какие функции должен выполнять бот?",
        'bot_inst': "Сначала создайте бота в @BotFather и отправьте мне TOKEN созданного бота.",
        'problem': "Опишите вашу проблему:",
        'done': "Ваш запрос отправлен администратору. Скоро мы свяжемся с вами!",
        'contact_btn': "Связаться с админом",
        'btn_pres': "Презентация 📽", 'btn_kurs': "Курсовая 📚", 'btn_sam': "Самостоятельная 📝",
        'btn_site': "Создать сайт 🌐", 'btn_bot': "Создать бота 🤖", 
        'btn_help': "Помощь с ПК/Тел 🛠", 'btn_admin': "Связь с админом 👨‍💻"
    },
    'en': {
        'services': "Choose a service:",
        'topic': "What is the topic?",
        'pages': "How many pages should it be?",
        'site_q': "What kind of website do you want to create?",
        'bot_q': "What functions should the bot perform?",
        'bot_inst': "First create a bot in @BotFather and send me the TOKEN.",
        'problem': "Describe your problem:",
        'done': "Your request has been sent to the admin. We will contact you soon!",
        'contact_btn': "Contact Admin",
        'btn_pres': "Presentation 📽", 'btn_kurs': "Coursework 📚", 'btn_sam': "Independent work 📝",
        'btn_site': "Create Website 🌐", 'btn_bot': "Create Bot 🤖", 
        'btn_help': "PC/Phone Help 🛠", 'btn_admin': "Contact Admin 👨‍💻"
    }
}

# Клавиатуры
def get_lang_kb():
    return types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="🇺🇿 O'zbekcha"), types.KeyboardButton(text="🇷🇺 Русский"), types.KeyboardButton(text="🇬🇧 English")]
    ], resize_keyboard=True)

def get_services_kb(lang):
    m = MESSAGES[lang]
    return types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text=m['btn_pres']), types.KeyboardButton(text=m['btn_kurs'])],
        [types.KeyboardButton(text=m['btn_sam']), types.KeyboardButton(text=m['btn_site'])],
        [types.KeyboardButton(text=m['btn_bot']), types.KeyboardButton(text=m['btn_help'])],
        [types.KeyboardButton(text=m['btn_admin'])]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("ZAR Digital Bot\n🇺🇿 Tilni tanlang / 🇷🇺 Выберите язык / 🇬🇧 Choose language:", reply_markup=get_lang_kb())

# Выбор языка
@dp.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English"]))
async def set_lang(message: types.Message, state: FSMContext):
    lang_map = {"🇺🇿 O'zbekcha": 'uz', "🇷🇺 Русский": 'ru', "🇬🇧 English": 'en'}
    lang = lang_map[message.text]
    await state.update_data(lang=lang)
    await message.answer(MESSAGES[lang]['services'], reply_markup=get_services_kb(lang))

# Логика: Презентации, Курсовые, Самостоятельные
@dp.message(lambda m: any(m.text in [MESSAGES[l][k] for k in ['btn_pres', 'btn_kurs', 'btn_sam']] for l in MESSAGES))
async def process_edu_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    await state.update_data(service=message.text)
    await message.answer(MESSAGES[lang]['topic'])
    await state.set_state(Order.waiting_for_topic)

@dp.message(Order.waiting_for_topic)
async def process_topic(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    await state.update_data(topic=message.text)
    await message.answer(MESSAGES[lang]['pages'])
    await state.set_state(Order.waiting_for_pages)

@dp.message(Order.waiting_for_pages)
async def finish_edu_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    admin_msg = f"🆕 ЗАКАЗ: {data['service']}\nТема: {data['topic']}\nЛистов: {message.text}\nОт: {user_info}"
    await bot.send_message(ADMIN_ID, admin_msg)
    await message.answer(MESSAGES[lang]['done'])
    await state.clear()

# Логика: Создать сайт
@dp.message(lambda m: any(m.text == MESSAGES[l]['btn_site'] for l in MESSAGES))
async def start_site(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    await message.answer(MESSAGES[lang]['site_q'])
    await state.set_state(Order.waiting_for_site_details)

@dp.message(Order.waiting_for_site_details)
async def finish_site(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    await bot.send_message(ADMIN_ID, f"🌐 ЗАКАЗ САЙТА\nТема: {message.text}\nОт: {user_info}")
    await message.answer(MESSAGES[lang]['done'])
    await state.clear()

# Логика: Создать бота
@dp.message(lambda m: any(m.text == MESSAGES[l]['btn_bot'] for l in MESSAGES))
async def start_bot_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    await message.answer(MESSAGES[lang]['bot_q'])
    await state.set_state(Order.waiting_for_bot_details)

@dp.message(Order.waiting_for_bot_details)
async def next_bot_step(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    await state.update_data(bot_desc=message.text)
    await message.answer(MESSAGES[lang]['bot_inst'])
    await state.set_state(Order.waiting_for_bot_token)

@dp.message(Order.waiting_for_bot_token)
async def finish_bot_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    await bot.send_message(ADMIN_ID, f"🤖 ЗАКАЗ БОТА\nОписание: {data['bot_desc']}\nTOKEN: {message.text}\nОт: {user_info}")
    await message.answer(MESSAGES[lang]['done'])
    await state.clear()

# Логика: Помощь ПК/Тел
@dp.message(lambda m: any(m.text == MESSAGES[l]['btn_help'] for l in MESSAGES))
async def start_help(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    await message.answer(MESSAGES[lang]['problem'])
    await state.set_state(Order.waiting_for_tech_problem)

@dp.message(Order.waiting_for_tech_problem)
async def finish_help(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    await bot.send_message(ADMIN_ID, f"🛠 ТЕХ ПОМОЩЬ\nПроблема: {message.text}\nОт: {user_info}")
    await message.answer(MESSAGES[lang]['done'])
    await state.clear()

# Логика: Связь с админом
@dp.message(lambda m: any(m.text == MESSAGES[l]['btn_admin'] for l in MESSAGES))
async def contact_admin(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=MESSAGES[lang]['contact_btn'], url="https://t.me/kvonyeon")]
    ])
    await message.answer("👇", reply_markup=kb)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
