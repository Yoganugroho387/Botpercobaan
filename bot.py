from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import sqlite3
import os

TOKEN = "7469561476:AAGVAbKkc1T3qW-TREeJbDUUGmo5cAxVMWU"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Database Setup
conn = sqlite3.connect("bot_data.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        invited_by INTEGER,
        points INTEGER DEFAULT 0
    )
""")
conn.commit()

# Start Command
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    args = message.get_args()
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        invited_by = int(args) if args.isdigit() else None
        cursor.execute("INSERT INTO users (user_id, invited_by, points) VALUES (?, ?, 0)", (user_id, invited_by))
        conn.commit()
        
        if invited_by:
            cursor.execute("UPDATE users SET points = points + 10 WHERE user_id = ?", (invited_by,))
            conn.commit()
            await bot.send_message(invited_by, f"🎉 Anda mendapatkan 10 poin karena mengundang {message.from_user.full_name}!")
    
    menu_markup = InlineKeyboardMarkup()
    menu_markup.add(InlineKeyboardButton("🎟 Undang", callback_data="invite"))
    menu_markup.add(InlineKeyboardButton("💰 Tarik Saldo", callback_data="withdraw"))
    menu_markup.add(InlineKeyboardButton("📊 Saldo Saya", callback_data="balance"))
    menu_markup.add(InlineKeyboardButton("📢 Official Channel", url="https://t.me/yourchannel"))
    menu_markup.add(InlineKeyboardButton("👨‍💼 Admin Care", url="https://t.me/youradmin"))
    
    await message.answer("👋 Selamat datang! Undang teman dan kumpulkan poin!", reply_markup=menu_markup)

# Handle Menu
@dp.callback_query_handler(lambda call: call.data == "invite")
async def invite(call: types.CallbackQuery):
    user_id = call.from_user.id
    invite_link = f"httpd://t.me/Percobaanana_bot?start={user_id}"
    await call.message.answer(f"🔗 Bagikan tautan ini untuk mengundang teman dan dapatkan poin!\n{invite_link}")

@dp.callback_query_handler(lambda call: call.data == "balance")
async def balance(call: types.CallbackQuery):
    user_id = call.from_user.id
    cursor.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
    points = cursor.fetchone()[0]
    await call.message.answer(f"💰 Saldo Anda: {points} Poin")

@dp.callback_query_handler(lambda call: call.data == "withdraw")
async def withdraw(call: types.CallbackQuery):
    user_id = call.from_user.id
    cursor.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
    points = cursor.fetchone()[0]
    if points < 50:
        await call.message.answer("⚠️ Minimal penarikan 50 poin!")
    else:
        await bot.send_message(7660182646, f"🔔 Permintaan penarikan dari {call.from_user.full_name} ({user_id}), saldo: {points} Poin.")
        await call.message.answer("✅ Permintaan penarikan dikirim ke admin!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
    