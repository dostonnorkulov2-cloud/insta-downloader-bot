import yt_dlp
import os
import asyncio
from shazamio import Shazam
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

TOKEN = "8547979723:AAEVdtmWdXFPpslU63Zex8UYnJ2F5AJfuQg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 👋\n\n"
        "✅ Instagram/YouTube havolasini yuboring - yuklab beraman!\n"
        "✅ Ovozli xabar yuboring - qo'shiq nomini topaman! 🎵"
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "instagram.com" not in url and "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Faqat Instagram yoki YouTube havolasini yuboring!")
        return

    await update.message.reply_text("⏳ Yuklanmoqda, kuting...")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for f in os.listdir():
            if f.startswith("video."):
                await update.message.reply_video(
                    open(f, 'rb'),
                    caption="✅ Eng yuqori sifat! 🎬"
                )
                os.remove(f)
                return

        await update.message.reply_text("❌ Yuklab bo'lmadi.")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

async def shazam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Qo'shiq aniqlanmoqda, kuting...")

    voice = update.message.voice or update.message.audio
    file = await context.bot.get_file(voice.file_id)
    await file.download_to_drive("audio.ogg")

    try:
        shazam = Shazam()
        result = await shazam.recognize("audio.ogg")

        if "track" in result:
            track = result["track"]
            title = track.get("title", "Noma'lum")
            artist = track.get("subtitle", "Noma'lum")
            await update.message.reply_text(
                f"🎵 {title}\n"
                f"👤 {artist}",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("❌ Qo'shiq topilmadi.")

        os.remove("audio.ogg")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, shazam))
app.run_polling()

