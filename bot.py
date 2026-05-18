import http.server
import socketserver
import threading
import telebot
from telebot import types
import yt_dlp
import os

# --- 1. RENDER UCHUN DUMMY SERVER (PORT TIMEOUT XATOSINI TUZATISH) ---
def run_dummy_server():
    PORT = 10000
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Dummy server {PORT}-portda muvaffaqiyatli ishga tushdi.")
            httpd.serve_forever()
    except Exception as e:
        print(f"Dummy server xatosi: {e}")

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 2. BOT VA ADMIN SOZLAMALARI ---
BOT_TOKEN = "8378410376:AAEIVC8SRZd3534Klx9ho1NXuF_uwpevuXg"
ADMIN_ID = 123456789  # Oʻzingning Telegram ID raqamingni shunga almashtirib qoʻy jigar!

bot = telebot.TeleBot(BOT_TOKEN)

# Foydalanuvchi ma'lumotlarini vaqtinchalik saqlash uchun lugʻat
user_downloads = {}

# --- 3. MAJBURIY OBUNANI TEKSHIRISH FUNKSIYASI ---
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

# --- 4. ASOSIY MENU KLAVIATURASI (PASTDAGI MATNLI TUGMALAR) ---
def main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Loyiha Kanali 📢", "Bot Haqida ℹ️")
    markup.row("Qoʻllanma 📖", "Bot Yaratuvchisi 🧑‍💻")
    return markup

# --- 5. START BUYRUGʻI ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    if check_sub(user_id):
        bot.send_message(
            message.chat.id,
            f"Salom {message.from_user.first_name}! 👋\n\nInstagram havolasini yuboring, uni eng maksimal sifatda yuklab beraman.",
            reply_markup=main_menu_markup()
        )
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("1-Kanalga obuna boʻlish 📢", url="https://t.me/Uzzsv7"),
            types.InlineKeyboardButton("2-Kanalga obuna boʻlish 📢", url="https://t.me/ivella_x777"),
            types.InlineKeyboardButton("Tekshirish ✅", callback_data="check")
        )
        bot.send_message(
            message.chat.id, 
            "Botdan foydalanish uchun kanallarimizga obuna boʻling!", 
            reply_markup=markup
        )

# --- 6. TEKSHIRISH TUGMASI BOSILGANDA (CALLBACK) ---
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    user_id = call.from_user.id
    if check_sub(user_id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            "Rahmat! Obuna tasdiqlandi. Endi Instagram havolasini yuborishingiz mumkin. 🚀",
            reply_markup=main_menu_markup()
        )
    else:
        bot.answer_callback_query(call.id, "Siz hali barcha kanallarga obuna boʻlmadingiz! ❌", show_alert=True)

# --- 7. TUGMADAN MUSIQANI AJRATIB OLISH (CONVERT TO MP3) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("convert_"))
def convert_to_mp3_callback(call):
    user_id = int(call.data.split("_")[1])
    bot.answer_callback_query(call.id, "Videodan musiqa ajratilmoqda... 🎵")
    
    if user_id not in user_downloads:
        bot.send_message(call.message.chat.id, "❌ Xatolik: Havola topilmadi. Iltimos, linkni qaytadan yuboring.")
        return
        
    url = user_downloads[user_id]['url']
    audio_file = f"converted_{user_id}.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': audio_file,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    wait_msg = bot.send_message(call.message.chat.id, "🎵 Musiqa yuqori sifatda tayyorlanmoqda...")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        final_mp3 = f"{audio_file}.mp3" if not audio_file.endswith(".mp3") else audio_file
        # Agar yt_dlp avtomat .mp3 qo'shgan bo'lsa tekshiramiz
        if not os.path.exists(final_mp3) and os.path.exists(f"{audio_file}.mp3"):
            final_mp3 = f"{audio_file}.mp3"

        with open(final_mp3, 'rb') as f:
            bot.send_audio(call.message.chat.id, f, caption="🎵 @Uzzsv7 va @ivella_x777 hamkorligida tayyorlandi.")
            
        bot.delete_message(call.message.chat.id, wait_msg.message_id)
        
        if os.path.exists(final_mp3):
            os.remove(final_mp3)
    except Exception as e:
        print(e)
        bot.edit_message_text("❌ Musiqani ajratish jarayonida xatolik boʻldi.", call.message.chat.id, wait_msg.message_id)

# --- 8. INSTAGRAM HAVOLALARINI QABUL QILISH, TEXT TUGMALARI VA YUKLASH ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        start(message)
        return

    text = message.text

    # Pastdagi menyu tugmalari bosilganda:
    if text == "Loyiha Kanali 📢":
        bot.send_message(message.chat.id, "Bizning rasmiy kanallarimiz: @Uzzsv7 va @ivella_x777 🚀")
    elif text == "Bot Haqida ℹ️":
        bot.send_message(message.chat.id, "🤖 Bu bot Instagram'dan daxshatli tezlikda video va reellar yuklab berish uchun yaratilgan!")
    elif text == "Qoʻllanma 📖":
        bot.send_message(message.chat.id, "📖 Botdan foydalanish uchun shunchaki Instagram video havolasini (linkini) shu yerga yuboring.")
    elif text == "Bot Yaratuvchisi 🧑‍💻":
        bot.send_message(message.chat.id, "🧑‍💻 Bot yaratuvchisi va admin: @dostonnorkulov2")
    
    # Instagram havolasi kelganda (Oʻsha sen aytgan 3 ta shaffof tugma shu yerda):
    elif "instagram.com" in text:
        url = text
        user_downloads[user_id] = {'url': url} # Musiqa ajratish uchun saqlab qo'yamiz
        
        wait_msg = bot.send_message(message.chat.id, "🚀 Instagram'dan eng maksimal Ultra HD sifatda yuklanmoqda...")
        
        try:
            filename = f"insta_{user_id}.mp4"
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': filename,
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Instagram Reels')[:350]
            
            # --- MANA OʻSHA SIZ AYTGAN 3 TA SHAFFOF (INLINE) TUGMA ---
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🎵 Musiqasini ajratib olish (MP3)", callback_data=f"convert_{user_id}"),
                types.InlineKeyboardButton("🔗 Havolani yuklab olish", url=url),
                types.InlineKeyboardButton("📲 Videoni ulashish", switch_inline_query=f"Instagram'dagi daxshatli video: {url}")
            )
            
            # Videoni yuborish va tagiga inline tugmalarni biriktirish
            with open(filename, 'rb') as video:
                bot.send_video(
                    message.chat.id, 
                    video, 
                    caption=f"🎬 **Sarlavha:** {title}\n\n🤖 Serverda joy: Free Space\n@Uzzsv7 va @ivella_x777 hamkorligida",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
            
            bot.delete_message(message.chat.id, wait_msg.message_id)
            
            if os.path.exists(filename):
                os.remove(filename)
                
        except Exception as e:
            print(e)
            bot.edit_message_text("❌ Instagram videosini yuklab boʻlmadi. Havola xato yoki profil yopiq.", message.chat.id, wait_msg.message_id)
    
    else:
        bot.send_message(message.chat.id, "❌ Iltimos, faqat toʻgʻri Instagram havolasini yuboring yoki menyudan foydalaning!")

# --- 9. BOTNI JONLANTIRISH ---
print("Bot muvaffaqiyatli ishga tushmoqda...")
bot.polling(none_stop=True)

