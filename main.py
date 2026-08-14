import asyncio
import os
import sqlite3
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv

load_dotenv(".env", override=True)
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("Xatolik: BOT_TOKEN topilmadi!")
    exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, cat_id INTEGER, title TEXT, author TEXT, price TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, book_title TEXT)")
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO categories (id, name) VALUES (1, '📚 Badiiy adabiyot'), (2, '💻 IT & Dasturlash')")
        cursor.execute("INSERT INTO books (cat_id, title, author, price) VALUES (1, 'Alkimyogar', 'Paulo Koelyo', '35 000'), (1, 'Shaytanat', 'Tohir Malik', '50 000'), (2, 'Python Dasturlash', 'Gvido van Rossum', '70 000')")
        conn.commit()
    conn.close()

init_db()

async def handle(request):
    return web.Response(text="Bot muvaffaqiyatli ishlayapti!")

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛍 Katalog", callback_data="catalog")]])
    await message.answer("Assalomu alaykum! Xush kelibsiz. 👇", reply_markup=kb)

@dp.callback_query(F.data == "catalog")
async def show_categories(call: CallbackQuery):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    cats = cursor.fetchall()
    conn.close()
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"cat_{id}")] for id, name in cats]
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="main")])
    await call.message.edit_text("Kategoriyani tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("cat_"))
async def show_books(call: CallbackQuery):
    cat_id = call.data.split("_")[1]
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM books WHERE cat_id = ?", (cat_id,))
    books = cursor.fetchall()
    conn.close()
    buttons = [[InlineKeyboardButton(text=title, callback_data=f"book_{id}")] for id, title in books]
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="catalog")])
    await call.message.edit_text("Kitobni tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("book_"))
async def book_detail(call: CallbackQuery):
    book_id = call.data.split("_")[1]
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, author, price FROM books WHERE id = ?", (book_id,))
    b = cursor.fetchone()
    conn.close()
    text = f"📖 **{b[0]}**\n✍️ Muallif: {b[1]}\n💰 Narxi: {b[2]} so'm"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Buyurtma berish", callback_data=f"order_{book_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="catalog")]
    ])
    await call.message.edit_text(text, reply_markup=kb)

@dp.callback_query(F.data.startswith("order_"))
async def order_book(call: CallbackQuery):
    book_id = call.data.split("_")[1]
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM books WHERE id = ?", (book_id,))
    title = cursor.fetchone()[0]
    cursor.execute("INSERT INTO orders (user_id, book_title) VALUES (?, ?)", (call.from_user.id, title))
    conn.commit()
    conn.close()
    await call.answer("Buyurtmangiz qabul qilindi!", show_alert=True)

@dp.callback_query(F.data == "main")
async def back_to_start(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛍 Katalog", callback_data="catalog")]])
    await call.message.edit_text("Assalomu alaykum! Xush kelibsiz. 👇", reply_markup=kb)

async def main():
    port = int(os.environ.get("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    asyncio.create_task(site.start())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
