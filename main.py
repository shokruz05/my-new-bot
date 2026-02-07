import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- ДАННЫЕ ИЗ ТВОЕГО СООБЩЕНИЯ ---
TOKEN = "8185440589:AAH-QOBqKunLzLQvYmhGt8osUOKXeR4gd8E"
ADMIN_ID = 8239382195  # Твой ID, куда будут падать заказы

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Тексты на трех языках
TEXTS = {
    'ru': {
        'welcome': "Привет! Я твой личный помощник. Выберите язык интерфейса:",
        'services': "Наши услуги:",
        'sent': "✅ Запрос отправлен! Администратор @kvonyeon свяжется с вами скоро.",
        'btn_admin': "👤 Связаться с админом",
        'menu': ["Презентации", "Курсовые", "Самостоятельные", "Создать сайт", "Создать бота", "Помощь с ПК/Тел"]
    },
    'uz': {
        'welcome': "Salom! Men sizning shaxsiy yordamchingizman. Tilni tanlang:",
        'services': "Bizning xizmatlar:",
        'sent': "✅ So'rov yuborildi! Administrator @kvonyeon tez orada siz bilan bog'lanadi.",
        'btn_admin': "👤 Admin bilan bog'lanish",
        'menu': ["Prezentatsiyalar", "Kurs ishlari", "Mustaqil ishlar", "Sayt yaratish", "Bot yaratish", "Kompyuter/Tel yordami"]
    },
    'en': {
        'welcome': "Hello! I am your personal assistant. Choose a language:",
        'services': "Our services:",
        'sent': "✅ Request sent! Administrator @kvonyeon will contact you shortly.",
        'btn_admin': "👤 Contact Admin",
        'menu': ["Presentations", "Term papers", "Homework", "Create website", "Create bot", "PC/Phone help"]
    }
}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"))
    builder.row(types.InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"))
    builder.row(types.InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"))
    await message.answer(TEXTS['ru']['welcome'], reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    builder = InlineKeyboardBuilder()
    
    for service in TEXTS[lang]['menu']:
        builder.row(types.InlineKeyboardButton(text=service, callback_data=f"order_{lang}_{service[:15]}"))
    
    builder.row(types.InlineKeyboardButton(text=TEXTS[lang]['btn_admin'], callback_data=f"contact_admin_{lang}"))
    await callback.message.edit_text(TEXTS[lang]['services'], reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("order_"))
async def process_order(callback: types.CallbackQuery):
    _, lang, service = callback.data.split("_")
    await callback.answer(TEXTS[lang]['sent'], show_alert=True)
    
    user = callback.from_user
    admin_msg = (f"🚀 **НОВЫЙ ЗАКАЗ!**\n\n"
                 f"👤 Клиент: {user.full_name}\n"
                 f"🔗 Юзер: @{user.username if user.username else 'нет'}\n"
                 f"🆔 ID: `{user.id}`\n"
                 f"🛠 Услуга: **{service}**")
    
    await bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("contact_admin_"))
async def contact_admin(callback: types.CallbackQuery):
    lang = callback.data.split("_")[2]
    await callback.answer(f"Write to: @kvonyeon", show_alert=True)

async def main():
    print("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
