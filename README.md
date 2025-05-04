# Kanal Statistikasi Web App + Telegram Bot (Railway + MySQL)

## Xususiyatlar
- Telegram kanal/guruh uchun statistik bot
- Statistika WebApp (Streamlit) orqali grafikda ko‘rinadi
- Railway'da MySQL orqali umumiy ma'lumotlar bazasi
- WebApp tugmasi (Telegramda to'g'ridan-to'g'ri ochiladi)

---

## Ishga tushirish (Railway uchun)

### 1. GitHub repozitoriy tayyorlash
- Barcha kod va fayllarni (bot.py, stats_web.py, requirements.txt, Procfile, .gitignore va boshqalar) bitta papkaga joylang.
- `.env` va `stats.db` fayllari **.gitignore** ga kiritilgan bo'lishi kerak.

### 2. GitHub'ga push qilish
```bash
cd "D:/Channel Sentry Bot"   # Loyihangiz papkasiga kiring

git add .
git commit -m "Yangi o'zgarishlar: MySQL, WebApp tugmasi, va boshqalar"
git push
```

### 3. Railway'da deploy qilish
1. Railway'da yangi project oching va GitHub repozitoriydan import qiling.
2. **MySQL plugin** qo'shing (Add Plugin → MySQL) va yangi database yarating (agar kerak bo'lsa).
3. **MYSQL_URL** ni worker va web service'larning Variables bo'limiga qo'shing.
4. **BOT_TOKEN**, **ADMIN_CHAT_ID**, **CHANNEL_ID** kabi environment variable'larni ham qo'shing.
5. Railway avtomatik tarzda web (Streamlit) va worker (bot) service'larni ishga tushiradi.

### 4. WebApp tugmasi va foydalanish
- Telegramda /start yozing — bot salomlashadi va pastda **Statistika** WebApp tugmasi chiqadi.
- Tugmani bosing — statistikani Railway'dagi web-app'da ko'rasiz.
- Yangi a'zo qo'shsangiz, statistika real vaqtda yangilanadi.

---

## Muhim eslatmalar
- **MYSQL_URL** environment variable to'g'ri va to'liq bo'lishi shart (masalan, `mysql://root:parol@mysql.railway.internal:3306/railway`).
- Kodda `user_id` ustuni **BigInteger** bo'lishi shart.
- WebApp tugmasi faqat HTTPS va yangi Telegram ilovalarida ishlaydi.
- Barcha environment variable'larni Railway'da har bir service uchun alohida kiriting.

---

## Muammolar va tez-tez so'raladigan savollar
- **/start** komandasi ishlamayaptimi? — Kodda handler borligiga ishonch hosil qiling.
- **Statistika tugmasi ko'rinmayaptimi?** — Kodda WebApp tugmasi ishlatilganiga ishonch hosil qiling.
- **MySQL xatoliklari** — Jadvalni to'g'ri yarating, `user_id` ustunini BIGINT qiling, MYSQL_URL to'g'ri kiriting.

---

Agar savol yoki muammo bo'lsa, README'ni o'qing yoki yordam uchun muallifga murojaat qiling! 