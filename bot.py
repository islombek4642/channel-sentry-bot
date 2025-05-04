import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatMemberUpdated, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
from dateutil import tz
from aiogram.utils.markdown import hbold
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import sys
import socket
import pymysql

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
load_dotenv()
API_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MYSQL_URL = os.getenv('MYSQL_URL')

# SQLAlchemy sozlash
pymysql.install_as_MySQLdb()
engine = create_engine(MYSQL_URL, echo=False)
Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    join_date = Column(String(32))
    source = Column(Text)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Bot va Dispatcher
def get_bot():
    return Bot(token=API_TOKEN)
bot = get_bot()
dp = Dispatcher()

# Oddiy reply keyboard (lokal test uchun)
stats_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Statistika")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Yangi a'zo qo'shilganini aniqlash
@dp.chat_member()
async def handle_chat_member(update: ChatMemberUpdated):
    logger.info(f"Chat ID: {update.chat.id}")
    global CHANNEL_ID
    if CHANNEL_ID is None:
        CHANNEL_ID = int(update.chat.id)
        logger.info(f"CHANNEL_ID set to: {CHANNEL_ID}")
    if int(update.chat.id) != CHANNEL_ID:
        logger.warning(f"Wrong chat ID: {update.chat.id}, expected: {CHANNEL_ID}")
        return
    user = update.new_chat_member.user
    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status
    join_time = datetime.now(tz.gettz('Asia/Tashkent')).strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"User {user.id} ({user.username or user.first_name}) status changed from {old_status} to {new_status}")
    try:
        user_profile = await bot.get_chat(user.id)
        bio = user_profile.bio or "Bio mavjud emas"
    except Exception as e:
        logger.error(f"Error getting user bio: {e}")
        bio = "Bio ma'lumotini olish imkonsiz"
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
    message = (
        f"🎉 {hbold('Yangi a\'zo qo\'shildi!')}\n"
        f"👤 {hbold('Ism')}: {user.first_name} {user.last_name or ''}\n"
        f"🆔 {hbold('ID')}: {user.id}\n"
        f"🔗 {hbold('Username')}: @{user.username or 'Yo\'q'}\n"
        f"📝 {hbold('Bio')}: {bio}\n"
        f"⏰ {hbold('Qo\'shilgan vaqt')}: {join_time}\n"
        f"🌐 {hbold('Manba')}: {source}"
    )
    if old_status in ['left', 'kicked'] and new_status == 'member':
        try:
            session = Session()
            member = Member(user_id=user.id, join_date=join_time, source=source)
            session.add(member)
            session.commit()
            logger.info(f"User {user.id} added to database")
            today = join_time[:10]
            daily_count = session.query(Member).filter(Member.join_date.like(f"{today}%")).count()
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            weekly_count = session.query(Member).filter(Member.join_date >= week_ago).count()
            stats_message = (
                f"\n📊 {hbold('Statistika')}:\n"
                f"  - Bugun: {daily_count} a'zo\n"
                f"  - Haftada: {weekly_count} a'zo"
            )
            full_message = message + stats_message
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID, 
                text=full_message, 
                parse_mode='HTML',
                reply_markup=stats_keyboard
            )
            logger.info(f"Notification sent to admin about new member {user.id}")
            session.close()
        except Exception as e:
            logger.error(f"Error processing new member: {e}")
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

# Statistika funksiyalari
def get_today_stats():
    try:
        session = Session()
        today = datetime.now().strftime('%Y-%m-%d')
        count = session.query(Member).filter(Member.join_date.like(f"{today}%")).count()
        session.close()
        return count
    except Exception as e:
        logger.error(f"Error getting today's stats: {e}")
        return 0

def get_weekly_stats():
    try:
        session = Session()
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        count = session.query(Member).filter(Member.join_date >= week_ago).count()
        session.close()
        return count
    except Exception as e:
        logger.error(f"Error getting weekly stats: {e}")
        return 0

# Statistika tugmasi bosilganda havola yuborish
@dp.message(lambda message: message.text == "📊 Statistika")
async def send_stats_link(message: types.Message):
    await message.answer(
        "📊 Statistika uchun web-app havolasi:\n"
        "https://web-production-8de5.up.railway.app\n\n"
        "Agar tugma orqali ochilmasa, havolani brauzerda oching."
    )

# Botni ishga tushirish
def main():
    import asyncio
    asyncio.run(_main())

async def _main():
    try:
        logger.info("Bot starting...")
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

if __name__ == '__main__':
    main()