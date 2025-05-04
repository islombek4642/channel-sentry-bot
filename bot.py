import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from datetime import datetime, timedelta
from dateutil import tz
import sqlite3
from aiogram.utils.markdown import hbold
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import pandas as pd
import io
import subprocess
import sys
import socket

# Logging sozlash
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"bot_{datetime.now().strftime('%Y-%m-%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot sozlamalari
load_dotenv()  # .env faylidan o'zgaruvchilarni yuklash
API_TOKEN = os.getenv('BOT_TOKEN')  # BotFather token
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))  # Admin chat ID
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # Kanal ID ni integer ga o'tkazamiz

# Bot va Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()  # Bot argumentini olib tashladik

# Ma'lumotlar bazasini sozlash
conn = sqlite3.connect('stats.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    join_date TEXT,
                    source TEXT
                )''')
conn.commit()

# Oddiy reply keyboard (lokal test uchun)
stats_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Statistika")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Streamlit web-appni avtomatik ishga tushirish
def start_streamlit():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8501))
    sock.close()
    if result == 0:
        return  # Streamlit allaqachon ishlayapti
    streamlit_cmd = [sys.executable, "-m", "streamlit", "run", "stats_web.py"]
    subprocess.Popen(streamlit_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

start_streamlit()

# Statistika grafiklarini yaratish
async def generate_stats_chart(period='day'):
    plt.figure(figsize=(10, 6))
    
    if period == 'day':
        # Bugungi statistika
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT strftime('%H', join_date) as hour, COUNT(*) as count 
            FROM members 
            WHERE join_date LIKE ? 
            GROUP BY hour 
            ORDER BY hour
        """, (f"{today}%",))
        data = cursor.fetchall()
        hours = [row[0] for row in data]
        counts = [row[1] for row in data]
        plt.bar(hours, counts)
        plt.title('Bugungi a\'zolar statistikasi')
        plt.xlabel('Soat')
        plt.ylabel('A\'zolar soni')
        
    elif period == 'week':
        # Haftalik statistika
        cursor.execute("""
            SELECT date(join_date) as date, COUNT(*) as count 
            FROM members 
            WHERE join_date >= date('now', '-7 days')
            GROUP BY date 
            ORDER BY date
        """)
        data = cursor.fetchall()
        dates = [row[0] for row in data]
        counts = [row[1] for row in data]
        plt.plot(dates, counts, marker='o')
        plt.title('Haftalik a\'zolar statistikasi')
        plt.xlabel('Sana')
        plt.ylabel('A\'zolar soni')
        plt.xticks(rotation=45)
        
    elif period == 'month':
        # Oylik statistika
        cursor.execute("""
            SELECT date(join_date) as date, COUNT(*) as count 
            FROM members 
            WHERE join_date >= date('now', '-30 days')
            GROUP BY date 
            ORDER BY date
        """)
        data = cursor.fetchall()
        dates = [row[0] for row in data]
        counts = [row[1] for row in data]
        plt.plot(dates, counts, marker='o')
        plt.title('Oylik a\'zolar statistikasi')
        plt.xlabel('Sana')
        plt.ylabel('A\'zolar soni')
        plt.xticks(rotation=45)
        
    elif period == 'sources':
        # Manbalar bo'yicha statistika
        cursor.execute("""
            SELECT source, COUNT(*) as count 
            FROM members 
            GROUP BY source 
            ORDER BY count DESC
        """)
        data = cursor.fetchall()
        sources = [row[0] for row in data]
        counts = [row[1] for row in data]
        plt.pie(counts, labels=sources, autopct='%1.1f%%')
        plt.title('A\'zolar manbalari bo\'yicha statistika')

    plt.tight_layout()
    
    # Grafikni rasmga aylantirish
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

# Yangi a'zo qo'shilganini aniqlash
@dp.chat_member()
async def handle_chat_member(update: ChatMemberUpdated):
    # Kanal ID'sini aniqlash uchun debug qatori
    logger.info(f"Chat ID: {update.chat.id}")
    
    # Agar CHANNEL_ID hali aniqlanmagan bo'lsa, uni avtomatik o'rnatamiz
    global CHANNEL_ID
    if CHANNEL_ID is None:
        CHANNEL_ID = int(update.chat.id)
        logger.info(f"CHANNEL_ID set to: {CHANNEL_ID}")

    # Agar update boshqa chatdan bo'lsa, e'tibor bermaymiz
    if int(update.chat.id) != CHANNEL_ID:
        logger.warning(f"Wrong chat ID: {update.chat.id}, expected: {CHANNEL_ID}")
        return

    user = update.new_chat_member.user
    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status
    join_time = datetime.now(tz.gettz('Asia/Tashkent')).strftime('%Y-%m-%d %H:%M:%S')

    logger.info(f"User {user.id} ({user.username or user.first_name}) status changed from {old_status} to {new_status}")

    # Foydalanuvchi bio ma'lumotini olish
    try:
        user_profile = await bot.get_chat(user.id)
        bio = user_profile.bio or "Bio mavjud emas"
    except Exception as e:
        logger.error(f"Error getting user bio: {e}")
        bio = "Bio ma'lumotini olish imkonsiz"

    # Manba aniqlash (havola yoki boshqa)
    source = "Noma'lum manba"
    try:
        if update.invite_link:
            source = f"Havola: {update.invite_link.name or 'Noma\'lum havola'}"
        elif update.chat.username:
            source = f"Qidiruv orqali: @{update.chat.username}"
        else:
            source = "Qidiruv orqali"
    except Exception as e:
        logger.error(f"Error detecting source: {e}")
    
    logger.info(f"User joined from source: {source}")

    # Xabar shablonini tayyorlash
    message = (
        f"🎉 {hbold('Yangi a\'zo qo\'shildi!')}\n"
        f"👤 {hbold('Ism')}: {user.first_name} {user.last_name or ''}\n"
        f"🆔 {hbold('ID')}: {user.id}\n"
        f"🔗 {hbold('Username')}: @{user.username or 'Yo\'q'}\n"
        f"📝 {hbold('Bio')}: {bio}\n"
        f"⏰ {hbold('Qo\'shilgan vaqt')}: {join_time}\n"
        f"🌐 {hbold('Manba')}: {source}"
    )

    # Yangi a'zo qo'shilgan bo'lsa
    if old_status in ['left', 'kicked'] and new_status == 'member':
        try:
            # Bazaga yozish
            cursor.execute("INSERT INTO members (user_id, join_date, source) VALUES (?, ?, ?)",
                        (user.id, join_time, source))
            conn.commit()
            logger.info(f"User {user.id} added to database")

            # Statistika hisoblash
            today = join_time[:10]  # YYYY-MM-DD
            cursor.execute("SELECT COUNT(*) FROM members WHERE join_date LIKE ?", (f"{today}%",))
            daily_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM members WHERE join_date >= date('now', '-7 days')")
            weekly_count = cursor.fetchone()[0]

            # Statistikani xabarga qo'shish
            stats_message = (
                f"\n📊 {hbold('Statistika')}:\n"
                f"  - Bugun: {daily_count} a'zo\n"
                f"  - Haftada: {weekly_count} a'zo"
            )
            full_message = message + stats_message

            # Adminlarga xabar yuborish
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID, 
                text=full_message, 
                parse_mode='HTML',
                reply_markup=stats_keyboard
            )
            logger.info(f"Notification sent to admin about new member {user.id}")
        except Exception as e:
            logger.error(f"Error processing new member: {e}")

    # A'zo chiqib ketgan bo'lsa
    if old_status == 'member' and new_status in ['left', 'kicked']:
        try:
            leave_message = (
                f"🚪 {hbold('A\'zo chiqib ketdi!')}\n"
                f"👤 {hbold('Ism')}: {user.first_name} {user.last_name or ''}\n"
                f"🆔 {hbold('ID')}: {user.id}\n"
                f"🔗 {hbold('Username')}: @{user.username or 'Yo\'q'}\n"
                f"⏰ {hbold('Chiqib ketgan vaqt')}: {join_time}"
            )
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=leave_message, parse_mode='HTML')
            logger.info(f"Notification sent to admin about member leaving {user.id}")
        except Exception as e:
            logger.error(f"Error sending leave notification: {e}")

# Botni ishga tushirish
async def main():
    try:
        logger.info("Bot starting...")
        # Bot ishga tushgani haqida xabar
        startup_message = (
            f"🤖 {hbold('Channel Sentry Bot')} ishga tushdi!\n\n"
            f"📊 {hbold('Statistika')}:\n"
            f"  - Bugun: {get_today_stats()} a'zo\n"
            f"  - Haftada: {get_weekly_stats()} a'zo\n\n"
            f"✅ Bot faol va a'zolarni kuzatmoqda..."
        )
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=startup_message,
            parse_mode='HTML',
            reply_markup=stats_keyboard
        )
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        logger.info("Bot stopped")

# Statistika funksiyalari
def get_today_stats():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM members WHERE join_date LIKE ?", (f"{today}%",))
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Error getting today's stats: {e}")
        return 0

def get_weekly_stats():
    try:
        cursor.execute("SELECT COUNT(*) FROM members WHERE join_date >= date('now', '-7 days')")
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Error getting weekly stats: {e}")
        return 0

# Statistika tugmasi bosilganda havola yuborish
@dp.message(lambda message: message.text == "📊 Statistika")
async def send_stats_link(message: types.Message):
    await message.answer(
        "📊 Statistika uchun web-app havolasi:\nhttp://localhost:8501\n\n"
        "Agar tugma orqali ochilmasa, havolani brauzerda oching."
    )

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())