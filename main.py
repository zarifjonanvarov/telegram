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
if not TOKEN: exit("Xatolik: .env faylida BOT_TOKEN topilmadi!")

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
    await call
