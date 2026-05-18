import http.server
import socketserver
import threading
import telebot
from telebot import types
import yt_dlp
import os
import subprocess

# --- 0. YT-DLP MAJBURIY YANGILASH ---
try:
    print("yt-dlp yangilanmoqda...")
    subprocess.run(["pip", "install", "--upgrade", "yt-dlp"], check=True)
    print("yt-dlp muvaffaqiyatli yangilandi!")
except Exception as e:
    print(f"yt-dlp yangilashda xatolik: {e}")

# --- 1. RENDER UCHUN DUMMY SERVER ---
def run_dummy_server():
    PORT = 10000
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Dummy server {PORT}-portda ishlamoqda.")
            httpd.serve_forever()
    except Exception as e:
        print(f"Dummy server xatosi: {e}")

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 2. BOT SOZLAMALARI ---
BOT_TOKEN = "8378410376:AAEIVC8SRZd3534Klx9ho1NXuF_uwpevuXg"
bot = telebot.TeleBot(BOT_TOKEN)
user_downloads = {}

# --- 3. MAJBURIY OBUNANI TEKSHIRISH ---
def check_sub(user_id):
    channels = ["@Uzzsv7", "@ivella_x777"]
    for channel in channels:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            print(f"Kanal tekshirishda xatolik ({channel}): {e}")
            return False
    return True

# --- 4. ASOSIY SHAFFOF MENU TUGMALARI ---
def main_menu_inline():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📢 Loyiha Kanali", url="https://t.me/Uzzsv7"),
        types.InlineKeyboardButton("ℹ️ Bot Haqida", callback_data="about_bot"),
        types.InlineKeyboardButton("📖 Qoʻllanma", callback_data="help_bot"),
        types.InlineKeyboardButton("👑 Bot Yaratuvchisi", callback_data="creator_bot")
    )
    return markup

# --- 5. START BUYRUGʻI ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.set_chat_menu_button(message.chat.id, types.MenuButtonDefault())
    
    if check_sub(user_id):
        bot.send_message(
            message.chat.id,
            f"Salom {message.from_user.first_name}! 👋\n\n"
            f"Instagram havolasini yuboring, uni eng maksimal (Ultra HD/4K) sifatda yuklab beraman!\n\n"
            f"Yoki pastdagi tugmalar orqali onlayn foydalaning! 👇",
            reply_markup=main_menu_inline()
        )
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("1-Kanalga obuna boʻlish 📢", url="https://t.me/Uzzsv7"),
            types.InlineKeyboardButton("2-Kanalga obuna boʻlish 📢", url="https://t.me/ivella_x777"),
            types.InlineKeyboardButton("Tekshirish ✅", callback_data="check_subscription")
        )
        bot.send_message(message.chat.id, "Botdan foydalanish uchun kanallarimizga obuna boʻling!", reply_markup=markup)

# --- 6. CALLBACK (SHAFFOF TUGMALAR) FUNKSIYALARI ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data == "check_subscription":
        if check_sub(user_id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(
                call.message.chat.id,
                f"Rahmat! Obuna tasdiqlandi. Endi Instagram havolasini yuborishingiz mumkin. 🚀",
                reply_markup=main_menu_inline()
            )
        else:
            bot.answer_callback_query(call.id, "Siz hali barcha kanallarga obuna boʻlmadingiz! ❌", show_alert=True)
            
    elif call.data == "about_bot":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🤖 Bu bot Instagram'dan daxshatli tezlikda video, rasm va reellar yuklab berish uchun yaratilgan!")
        
    elif call.data == "help_bot":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📖 **Botdan foydalanish qoʻllanmasi:**\n\nInstagram ilovasidan istalgan video havolasini (linkini) nusxalab oling va botga shundoqqina yuboring. Bot uni avtomat yuklab beradi!")
        
    elif call.data == "creator_bot":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📲 Admin bilan aloqa", url="https://t.me/PM_Dostonbek"))
        bot.send_message(
            call.message.chat.id, 
            "👑 **Bot Yaratuvchisi Haqida:**\n\n"
            "Bu daxshatli va mukammal loyiha ortida IT olamida oʻz oʻrniga ega, eng toza va "
            "professional kodlarni yozadigan, oʻta iqtidorli dasturchi **Dostonbek** turibdi! 🚀\n\n"
            "Har qanday taklif, hamkorlik yoki professional bot buyurtmalari uchun loyiha egasiga murojaat qilishingiz mumkin:",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
    elif call.data.startswith("convert_"):
        target_id = int(call.data.split("_")[1])
        bot.answer_callback_query(call.id, "Videodan musiqa ajratilmoqda... 🎵")
        
        if target_id not in user_downloads:
            bot.send_message(call.message.chat.id, "❌ Xatolik: Havola topilmadi. Qaytadan urinib ko'ring.")
            return
            
        url = user_downloads[target_id]['url']
        audio_file = f"converted_{target_id}"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_file,
            'quiet': True,
            'geo_bypass': True,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1'
            },
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        wait_msg = bot.send_message(call.message.chat.id, "🎵 Musiqa tayyorlanmoqda...")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            final_mp3 = f"{audio_file}.mp3"
            with open(final_mp3, 'rb') as f:
                bot.send_audio(call.message.chat.id, f, caption="🎵 @Uzzsv7 va @ivella_x777 hamkorligida")
            bot.delete_message(call.message.chat.id, wait_msg.message_id)
            if os.path.exists(final_mp3):
                os.remove(final_mp3)
        except Exception as e:
            bot.edit_message_text("❌ Musiqani ajratishda xatolik boʻldi.", call.message.chat.id, wait_msg.message_id)

# --- 7. BUSTED-PROOF INSTAGRAM YUKLASH FUNKSIYASI ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        start(message)
        return

    url = message.text
    if "instagram.com" in url:
        user_downloads[user_id] = {'url': url}
        wait_msg = bot.send_message(message.chat.id, "🚀 Instagram'dan video yuklanmoqda, iltimos kuting...")
        
        try:
            filename = f"insta_{user_id}.mp4"
            
            # Instagram blokirovkasini aylanib o'tuvchi eng daxshatli sozlamalar (Mobile Headers Emulator):
            ydl_opts = {
                'format': 'best',
                'outtmpl': filename,
                'quiet': True,
                'no_warnings': True,
                'geo_bypass': True,  # Server joylashuvini yashirish
                'add_header': [
                    'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language: en-US,en;q=0.5'
                ],
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
                    'Referer': 'https://www.instagram.com/',
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Instagram Reels')[:350]
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🎵 Musiqasini ajratib olish (MP3)", callback_data=f"convert_{user_id}"),
                types.InlineKeyboardButton("🔗 Havolani yuklab olish", url=url),
                types.InlineKeyboardButton("📲 Videoni ulashish", switch_inline_query=f"Instagram video: {url}")
            )
            
            with open(filename, 'rb') as video:
                bot.send_video(
                    message.chat.id, 
                    video, 
                    caption=f"🎬 **Sarlavha:** {title}\n\n🤖 @Uzzsv7 va @ivella_x777 hamkorligida",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
            
            bot.delete_message(message.chat.id, wait_msg.message_id)
            if os.path.exists(filename):
                os.remove(filename)
                
        except Exception as e:
            print(f"Yuklash xatosi: {e}")
            bot.edit_message_text(
                "❌ Instagram videosini yuklab boʻlmadi.\n\n"
                "💡 **Maslahat:** Server IP manzili vaqtinchalik bloklangan boʻlishi mumkin. Bir necha daqiqadan soʻng qayta urinib koʻring yoki boshqa havola yuboring.", 
                message.chat.id, 
                wait_msg.message_id
            )
    else:
        bot.send_message(message.chat.id, "❌ Iltimos, toʻgʻri Instagram havolasini yuboring!")

print("Bot ishga tushdi...")
bot.polling(none_stop=True)

