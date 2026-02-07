import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Состояния
class Order(StatesGroup):
    lang = State()
    waiting_for_topic = State()
    waiting_for_pages = State()
    waiting_for_site_details = State()
    waiting_for_bot_token = State()
    waiting_for_tech_problem = State()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8239382195 # Твой ID
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Словарь текстов
MESSAGES = {
    'uz': {
        'start': "Tilni tanlang:",
        'services': "Xizmatni tanlang:",
        'topic': "Mavzu nima haqida?",
        'pages': "Necha varaq bo'lishi kerak?",
        'done': "Sizning so'rovingiz adminga yuborildi.",
        'bot_inst': "@BotFather orqali bot oching va menga TOKEN yuboring.",
        'problem': "Muammoingiz nimada?",
        'contact': "Admin bilan bog'lanish",
        'btn_pres': "Prezentatsiya", 'btn_kurs': "Kursovoy", 'btn_site': "Sayt yaratish",
        'btn_bot': "Bot yaratish", 'btn_help': "PK/Tel yordam", 'btn_admin': "Admin bilan aloqa"
    },
    'ru': {
        'start': "Выберите язык:",
        'services': "Выберите услугу:",
        'topic': "На какую тему?",
        'pages': "Сколько листов должно быть?",
        'done': "Ваш запрос отправлен администратору.",
        'bot_inst': "Создайте бота в @BotFather и отправьте мне TOKEN.",
        'problem': "Какая у вас проблема?",
        'contact': "Связаться с админом",
        'btn_pres': "Презентация", 'btn_kurs': "Курсовая", 'btn_site': "Создать сайт",
        'btn_bot': "Создать бота", 'btn_help': "Помощь с ПК/Тел", 'btn_admin': "Связь с админом"
    },
    'en': {
        'start': "Choose language:",
        'services': "Choose a service:",
        'topic': "What is the topic?",
        'pages': "How many pages?",
        'done': "Your request has been sent to the admin.",
        'bot_inst': "Create a bot in @BotFather and send me the TOKEN.",
        'problem': "What is your problem?",
        'contact': "Contact Admin",
        'btn_pres': "Presentation", 'btn_kurs': "Coursework", 'btn_site': "Create Website",
        'btn_bot': "Create Bot", 'btn_help': "PC/Phone Help", 'btn_admin': "Contact Admin"
    }
}

def get_lang_kb():
    return types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="🇺🇿 O'zbekcha"), types.KeyboardButton(text="🇷🇺 Русский"), types.KeyboardButton(text="🇬🇧 English")]
    ], resize_keyboard=True)

def get_services_kb(lang):
    m = MESSAGES[lang]
    return types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text=m['btn_pres']), types.KeyboardButton(text=m['btn_kurs'])],
        [types.KeyboardButton(text=m['btn_site']), types.KeyboardButton(text=m['btn_bot'])],
        [types.KeyboardButton(text=m['btn_help']), types.KeyboardButton(text=m['btn_admin'])]
    ], resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🇺🇿 Tilni tanlang / 🇷🇺 Выберите язык / 🇬🇧 Choose language:", reply_markup=get_lang_kb())

@dp.message(F.text.contains("O'zbekcha"))
async def set_uz(m: types.Message, state: FSMContext):
    await state.update_data(lang='uz')
    await m.answer(MESSAGES['uz']['services'], reply_markup=get_services_kb('uz'))

@dp.message(F.text.contains("Русский"))
async def set_ru(m: types.Message, state: FSMContext):
    await state.update_data(lang='ru')
    await m.answer(MESSAGES['ru']['services'], reply_markup=get_services_kb('ru'))

@dp.message(F.text.contains("English"))
async def set_en(m: types.Message, state: FSMContext):
    await state.update_data(lang='en')
    await m.answer(MESSAGES['en']['services'], reply_markup=get_services_kb('en'))

# Пример логики для Презентации (автоматически на нужном языке)
@dp.message(lambda m: any(m.text == MESSAGES[l]['btn_pres'] for l in MESSAGES))
async def start_pres(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    await state.update_data(service="Презентация")
    await message.answer(MESSAGES[lang]['topic'])
    await state.set_state(Order.waiting_for_topic)

# Логика для связи с админом
@dp.message(lambda m: any(m.text == MESSAGES[l]['btn_admin'] for l in MESSAGES))
async def contact_admin(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    url_button = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=MESSAGES[lang]['contact'], url="https://t.me/kvonyeon")]
    ])
    await message.answer("👇", reply_markup=url_button)

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
