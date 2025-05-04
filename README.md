# Kanal Statistikasi Web App + Telegram Bot

## Ishga tushirish

1. Kerakli kutubxonalarni o‘rnating:
   ```bash
   pip install -r requirements.txt
   ```

2. Streamlit web-appni ishga tushiring:
   ```bash
   streamlit run stats_web.py
   ```
   (Agar serverda ishlatsangiz, `http://<server-ip>:8501` havolasini bot kodida mos ravishda o‘zgartiring)

3. Telegram botni ishga tushiring:
   ```bash
   python bot.py
   ```

4. Telegramda "📊 Statistika" tugmasini bosing — web-app ochiladi va statistikani ko‘rasiz.

## Eslatma
- Web-app va bot bir xil papkada bo‘lishi kerak.
- Web-app havolasini (localhost yoki server IP) mos ravishda o‘zgartiring.
- WebApp tugmasi faqat Telegram mobil va desktop ilovasining so‘nggi versiyalarida ishlaydi. 