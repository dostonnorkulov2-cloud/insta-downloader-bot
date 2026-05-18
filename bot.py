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
ADMIN_ID = 123456789  # Oʻzingning Telegram ID raqamingni yozib qoʻy jigar!

bot = telebot.TeleBot(BOT_TOKEN)
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

# --- 4. START BUYRUGʻI (ESKI 4 TA TUGMA BUTKUL YOʻQOTILDI) ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    # Ortiqcha eski menu buttonlarni Telegram xotirasidan butkul tozalash:
    bot.set_chat_menu_button(message.chat.id, types.MenuButtonDefault())
    
    if check_sub(user_id):
        # Hech qanday pastki matnli klaviatura yo'q, shundoq toza xabar boradi!
        bot.send_message(
            message.chat.id,
            f"Salom {message.from_user.first_name}! 👋\n\nInstagram havolasini yuboring, uni eng maksimal sifatda yuklab beraman.",
            reply_markup=types.ReplyKeyboardRemove() # Eski matnli tugmalarni o'chirib tashlaydi!
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

# --- 5. TEKSHIRISH TUGMASI BOSILGANDA (CALLBACK) ---
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    user_id = call.from_user.id
    if check_sub(user_id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            "Rahmat! Obuna tasdiqlandi. Endi Instagram havolasini yuborishingiz mumkin. 🚀",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        bot.answer_callback_query(call.id, "Siz hali barcha kanallarga obuna boʻlmadingiz! ❌", show_alert=True)

# --- 6. TUGMADAN MUSIQANI AJRATIB OLISH (CONVERT TO MP3) ---
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
            
        final_mp3 = audio_file if os.path.exists(audio_file) else f"{audio_file}.mp3"

        with open(final_mp3, 'rb') as f:
            bot.send_audio(call.message.chat.id, f, caption="🎵 @Uzzsv7 va @ivella_x777 hamkorligida tayyorlandi.")
            
        bot.delete_message(call.message.chat.id, wait_msg.message_id)
        
        if os.path.exists(final_mp3):
            os.remove(final_mp3)
    except Exception as e:
        print(e)
        bot.edit_message_text("❌ Musiqani ajratish jarayonida xatolik boʻldi.", call.message.chat.id, wait_msg.message_id)

# --- 7. INSTAGRAM HAVOLALARINI QABUL QILISH VA YUKLASH ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        start(message)
        return

    url = message.text

    if "instagram.com" in url:
        user_downloads[user_id] = {'url': url}
        wait_msg = bot.send_message(message.chat.id, "🚀 Instagram'dan eng maksimal Ultra HD sifatda yuklanmoqda...")
        
        try:
            filename = f"insta_{user_id}.mp4"
            # Render xotirasi va tezligi uchun eng optimal yuklash sozlamasi:
            ydl_opts = {
                'format': 'best',
                'outtmpl': filename,
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Instagram Reels')[:350]
            
            # --- MANA OʻSHA SEN AYTGAN 3 TA SHAFFOF (INLINE) TUGMA ---
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🎵 Musiqasini ajratib olish (MP3)", callback_data=f"convert_{user_id}"),
                types.InlineKeyboardButton("🔗 Havolani yuklab olish", url=url),
                types.InlineKeyboardButton("📲 Videoni ulashish", switch_inline_query=f"Instagram'dagi daxshatli video: {url}")
            )
            
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
            bot.edit_message_text("❌ Instagram videosini yuklab boʻlmadi. Havola xato, profil yopiq yoki yt_dlp yangilanishi kerak.", message.chat.id, wait_msg.message_id)
    else:
        bot.send_message(message.chat.id, "❌ Iltimos, faqat toʻgʻri Instagram havolasini yuboring!")

# --- 8. BOTNI JONLANTIRISH ---
print("Bot muvaffaqiyatli ishga tushmoqda...")
bot.polling(none_stop=True)

