import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- SOZLAMALAR ---
TOKEN = "8185440589:AAH-QOBqKunLzLQvYmhGt8osUOKXeR4gd8E"
ADMIN_ID = 8239382195
ADMIN_USERNAME = "@kvonyeon"
CARD_NUMBER = "9860 1966 0027 8234"
CHANNEL_LINK = "@zar_isbot"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class Order(StatesGroup):
    lang = State()
    section = State()
    waiting_for_topic = State()
    waiting_for_pages = State()
    waiting_for_desc = State()
    waiting_for_payment = State()

# --- MATNLAR ---
MESSAGES = {
    'uz': {
        'start': "Assalomu alaykum! Tilni tanlang / Выберите язык / Select language:",
        'menu': "Bo'limni tanlang:",
        'topic': "Mavzu nima haqida?",
        'pages': "Necha varaq bo'lishi kerak?",
        'it_ask': "Qanday maqsadda yaratmoqchisiz?",
        'it_resp': "Yaqin orada admin sizga shaxsiy xabarda javob beradi!",
        'tech_ask': "Qanday muammoingiz bor?",
        'tech_resp': "Admin tez orada javob beradi!",
        'pay_info': "💰 Xizmat narxi: {price} so'm\n\n💳 Karta raqami: `{card}`\n\n❗️ To'lovni amalga oshirib, skrinshotni shu yerga yuboring.\n\n📚 Namunalar: {channel}\n👨‍💻 Admin: {admin}",
        'done': "Skrinshot qabul qilindi! ✅ Admin tasdiqlashi bilan loyihangiz boshlanadi.",
        'btns': ["📊 Prezentatsiya", "📚 Kurs ishi / Mustaqil ish", "🤖 Bot yaratish", "🌐 Sayt yaratish", "🛠 PK/Tel yordam", "👨‍💻 Admin bilan aloqa"]
    },
    'ru': {
        'start': "Здравствуйте! Выберите язык / Select language:",
        'menu': "Выберите раздел:",
        'topic': "На какую тему работа?",
        'pages': "Сколько листов нужно?",
        'it_ask': "Для каких целей вы хотите создать?",
        'it_resp': "В ближайшее время админ ответит вам в личные сообщения!",
        'tech_ask': "Какая у вас проблема?",
        'tech_resp': "Админ ответит вам скоро!",
        'pay_info': "💰 Стоимость: {price} сум\n\n💳 Номер карты: `{card}`\n\n❗️ Пополните баланс и отправьте скриншот сюда.\n\n📚 Канал доверия: {channel}\n👨‍💻 Админ: {admin}",
        'done': "Скриншот принят! ✅ Как только админ подтвердит его, мы начнем ваш проект.",
        'btns': ["📊 Презентация", "📚 Курсовая / Самостоятельная", "🤖 Создать бота", "🌐 Создать сайт", "🛠 Помощь ПК/Тел", "👨‍💻 Связь с админом"]
    },
    'en': {
        'start': "Welcome! Please select language:",
        'menu': "Select a section:",
        'topic': "What is the topic?",
        'pages': "How many pages?",
        'it_ask': "For what purposes do you want to create it?",
        'it_resp': "Admin will contact you shortly in private messages!",
        'tech_ask': "What is your problem?",
        'tech_resp': "Admin will answer you soon!",
        'pay_info': "💰 Price: {price} UZS\n\n💳 Card number: `{card}`\n\n❗️ Please pay and send the screenshot here.\n\n📚 Proofs: {channel}\n👨‍💻 Admin: {admin}",
        'done': "Screenshot received! ✅ Once the admin confirms it, we will start your project.",
        'btns': ["📊 Presentation", "📚 Coursework / Independent work", "🤖 Create a Bot", "🌐 Create a Website", "🛠 PC/Phone Help", "👨‍💻 Contact Admin"]
    }
}

# --- KLAVIATURALAR ---
def get_lang_kb():
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="🇺🇿 O'zbekcha"), types.KeyboardButton(text="🇷🇺 Русский"), types.KeyboardButton(text="🇬🇧 English")]], resize_keyboard=True)

def get_menu_kb(lang):
    b = MESSAGES[lang]['btns']
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text=b[0]), types.KeyboardButton(text=b[1])],[types.KeyboardButton(text=b[2]), types.KeyboardButton(text=b[3])],[types.KeyboardButton(text=b[4]), types.KeyboardButton(text=b[5])]], resize_keyboard=True)

# --- LOGIKA ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer(MESSAGES['uz']['start'], reply_markup=get_lang_kb())

@dp.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English"]))
async def set_lang(m: types.Message, state: FSMContext):
    l = 'uz' if "O'z" in m.text else 'ru' if "Рус" in m.text else 'en'
    await state.update_data(lang=l)
    await m.answer(MESSAGES[l]['menu'], reply_markup=get_menu_kb(l))

@dp.message(lambda m: any(m.text in MESSAGES[l]['btns'] for l in MESSAGES))
async def handle_menu(m: types.Message, state: FSMContext):
    data = await state.get_data()
    l = data.get('lang', 'ru')
    btn = m.text
    
    if btn in [MESSAGES[l]['btns'][0], MESSAGES[l]['btns'][1]]: # Pres yoki Kurs/Mustaqil
        p = 15000 if btn == MESSAGES[l]['btns'][0] else 20000
        await state.update_data(section=btn, price=p)
        await m.answer(MESSAGES[l]['topic'])
        await state.set_state(Order.waiting_for_topic)
    
    elif btn in [MESSAGES[l]['btns'][2], MESSAGES[l]['btns'][3], MESSAGES[l]['btns'][4]]: # Bot, Sayt, PK
        await state.update_data(section=btn)
        q = MESSAGES[l]['it_ask'] if btn != MESSAGES[l]['btns'][4] else MESSAGES[l]['tech_ask']
        await m.answer(q)
        await state.set_state(Order.waiting_for_desc)
    else: # Admin
        await m.answer(f"👨‍💻 Admin: {ADMIN_USERNAME}")

@dp.message(Order.waiting_for_topic)
async def get_topic(m: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(topic=m.text)
    await m.answer(MESSAGES[data['lang']]['pages'])
    await state.set_state(Order.waiting_for_pages)

@dp.message(Order.waiting_for_pages)
async def get_pages(m: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(pages=m.text)
    txt = MESSAGES[data['lang']]['pay_info'].format(price=data['price'], card=CARD_NUMBER, channel=CHANNEL_LINK, admin=ADMIN_USERNAME)
    await m.answer(txt, parse_mode="Markdown")
    await state.set_state(Order.waiting_for_payment)

@dp.message(Order.waiting_for_desc)
async def get_desc(m: types.Message, state: FSMContext):
    data = await state.get_data()
    l = data['lang']
    await bot.send_message(ADMIN_ID, f"📩 SO'ROV: {data['section']}\nKimdan: @{m.from_user.username}\nMa'lumot: {m.text}")
    await m.answer(MESSAGES[l]['it_resp'] if "🤖" in data['section'] or "🌐" in data['section'] else MESSAGES[l]['tech_resp'])
    await state.clear()

@dp.message(Order.waiting_for_payment, F.photo)
async def get_pay(m: types.Message, state: FSMContext):
    data = await state.get_data()
    user = f"@{m.from_user.username}" if m.from_user.username else f"ID: {m.from_user.id}"
    caption = f"🔥 YANGI TO'LOV!\n\nTur: {data['section']}\nMavzu: {data['topic']}\nVaraq: {data['pages']}\nMijoz: {user}"
    await bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=caption)
    await m.answer(MESSAGES[data['lang']]['done'])
    await state.clear()

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
