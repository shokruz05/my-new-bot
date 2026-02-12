import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class Order(StatesGroup):
    lang = State()
    waiting_for_topic = State()
    waiting_for_pages = State()
    confirming = State()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8239382195 # Твой ID
CARD_NUMBER = "9860 1966 0027 8234" # Твоя карта
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Цены и тексты
PRICES = {'btn_pres': 15000, 'btn_kurs': 20000, 'btn_sam': 15000} #

MESSAGES = {
    'uz': {
        'services': "Xizmatni tanlang:",
        'topic': "Mavzu nima haqida?",
        'pages': "Necha varaq bo'lishi kerak?",
        'check': "Ma'lumotlar to'g'rimi?\nXizmat: {service}\nMavzu: {topic}\nVaraqlar: {pages}",
        'confirm_btn': "Hammasi to'g'ri ✅",
        'pay': "To'lov miqdori: {price} so'm.\nBuyurtma to'lovdan so'ng boshlanadi.\nKarta: {card}\nSkrinshotni adminga yuboring: @kvonyeon\nIsbotlar: @zar_isbot",
        'btn_pres': "Prezentatsiya", 'btn_kurs': "Kursovoy", 'btn_sam': "Mustaqil ish"
    },
    'ru': {
        'services': "Выберите услугу:",
        'topic': "На какую тему?",
        'pages': "Сколько листов должно быть?",
        'check': "Все верно?\nУслуга: {service}\nТема: {topic}\nЛистов: {pages}",
        'confirm_btn': "Все правильно ✅",
        'pay': "Сумма к оплате: {price} сум.\nЗаказ будет начат после оплаты.\nКарта: {card}\nОтправьте скриншот админу: @kvonyeon\nДоказательства: @zar_isbot",
        'btn_pres': "Презентация", 'btn_kurs': "Курсовая", 'btn_sam': "Самостоятельная"
    }
}

# Клавиатуры
def get_lang_kb():
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="🇺🇿 O'zbekcha"), types.KeyboardButton(text="🇷🇺 Русский")]], resize_keyboard=True)

def get_confirm_kb(lang):
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text=MESSAGES[lang]['confirm_btn'])]], resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=get_lang_kb())

@dp.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский"]))
async def set_lang(message: types.Message, state: FSMContext):
    lang = 'uz' if "O'zbekcha" in message.text else 'ru'
    await state.update_data(lang=lang)
    kb = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text=MESSAGES[lang]['btn_pres']), types.KeyboardButton(text=MESSAGES[lang]['btn_kurs'])],
        [types.KeyboardButton(text=MESSAGES[lang]['btn_sam'])]
    ], resize_keyboard=True)
    await message.answer(MESSAGES[lang]['services'], reply_markup=kb)

@dp.message(lambda m: any(m.text == MESSAGES[l][k] for l in MESSAGES for k in ['btn_pres', 'btn_kurs', 'btn_sam']))
async def start_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    # Определяем ключ услуги для цены
    service_key = next(k for k in ['btn_pres', 'btn_kurs', 'btn_sam'] if MESSAGES[lang][k] == message.text)
    await state.update_data(service=message.text, price=PRICES[service_key])
    await message.answer(MESSAGES[lang]['topic'])
    await state.set_state(Order.waiting_for_topic)

@dp.message(Order.waiting_for_topic)
async def get_topic(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    await state.update_data(topic=message.text)
    await message.answer(MESSAGES[lang]['pages'])
    await state.set_state(Order.waiting_for_pages)

@dp.message(Order.waiting_for_pages)
async def show_check(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    await state.update_data(pages=message.text)
    text = MESSAGES[lang]['check'].format(service=data['service'], topic=data['topic'], pages=message.text)
    await message.answer(text, reply_markup=get_confirm_kb(lang))
    await state.set_state(Order.confirming)

@dp.message(Order.confirming, lambda m: any(m.text == MESSAGES[l]['confirm_btn'] for l in MESSAGES))
async def send_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    # Отправка данных админу
    admin_text = f"✅ ПОДТВЕРЖДЕННЫЙ ЗАКАЗ:\n{data['service']}\nТема: {data['topic']}\nЛистов: {data['pages']}\nОт: @{message.from_user.username}"
    await bot.send_message(ADMIN_ID, admin_text)
    # Сообщение об оплате пользователю
    pay_text = MESSAGES[lang]['pay'].format(price=data['price'], card=CARD_NUMBER)
    await message.answer(pay_text, reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
