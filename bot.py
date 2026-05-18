import http.server
import socketserver
import threading
import telebot
from telebot import types
import yt_dlp
import os
import subprocess

# --- 0. YT-DLP KUTUBXONASINI MAJBURIY YANGILASH ---
try:
    print("yt-dlp oxirgi versiyaga yangilanmoqda...")
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
            print(f"Dummy server {PORT}-portda muvaffaqiyatli ishlamoqda.")
            httpd.serve_forever()
    except Exception as e:
        print(f"Dummy server xatosi: {e}")

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 2. BOT SOZLAMALARI ---
BOT_TOKEN = "8378410376:AAEIVC8SRZd3534Klx9ho1NXuF_uwpevuXg"
bot = telebot.TeleBot(BOT_TOKEN)
user_downloads = {}

# --- 3. MAJBURIY OBUNA ---
def check_sub(user_id):
    channels = ["@Uzzsv7", "@ivella_x777"]
    for channel in channels:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            print(f"Kanal tekshirish xatosi: {e}")
            return False
    return True

# --- 4. SHAFFOF MENU TUGMALARI ---
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
            f"Instagram havolasini yuboring, uni oʻta yuqori (Original HD) sifatda yuklab beraman!\n\n"
            f"Yoki pastdagi tugmalardan foydalaning: 👇",
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

# --- 6. CALLBACK TUGMALARI ---
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
        bot.send_message(call.message.chat.id, "🤖 Bu bot Instagram'dan daxshatli tezlikda va original sifatda video yuklash uchun yaratilgan!")
        
    elif call.data == "help_bot":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📖 **Botdan foydalanish qoʻllanmasi:**\n\nInstagram'dan havola nusxalab botga yuboring. Tamom!")
        
    elif call.data == "creator_bot":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📲 Admin bilan aloqa", url="https://t.me/PM_Dostonbek"))
        bot.send_message(
            call.message.chat.id, 
            "👑 **Bot Yaratuvchisi Haqida:**\n\n"
            "Bu daxshatli va mukammal loyiha ortida IT olamida oʻz oʻrniga ega, eng toza va "
            "professional kodlarni yozadigan, oʻta iqtidorli dasturchi **Dostonbek** turibdi! 🚀",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
    elif call.data.startswith("convert_"):
        target_id = int(call.data.split("_")[1])
        bot.answer_callback_query(call.id, "Videodan musiqa ajratilmoqda... 🎵")
        
        if target_id not in user_downloads:
            bot.send_message(call.message.chat.id, "❌ Xatolik: Havola topilmadi. Qaytadan link yuboring.")
            return
            
        url = user_downloads[target_id]['url']
        audio_file = f"converted_{target_id}"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_file,
            'quiet': True,
            'nocheckcertificate': True,
            'no_color': True,
            'extractor_args': {'instagram': {'client_id': ['null']}},
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            },
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
            final_mp3 = f"{audio_file}.mp3"
            with open(final_mp3, 'rb') as f:
                bot.send_audio(call.message.chat.id, f, caption="🎵 @Uzzsv7 va @ivella_x777 hamkorligida")
            bot.delete_message(call.message.chat.id, wait_msg.message_id)
            if os.path.exists(final_mp3):
                os.remove(final_mp3)
        except Exception as e:
            bot.edit_message_text("❌ Musiqani ajratishda xatolik boʻldi.", call.message.chat.id, wait_msg.message_id)

# --- 7. TOʻGʻRIDAN-TOʻGʻRI VA BLOKLARNI SINDIRUVCHI INSTAGRAM YUKLAGICH ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        start(message)
        return

    url = message.text
    if "instagram.com" in url:
        # Havolani toza ko'rinishga keltirish (barcha keraksiz parametrlarni qirqib tashlaymiz)
        clean_url = url.split("?")[0]
        user_downloads[user_id] = {'url': clean_url}
        
        wait_msg = bot.send_message(message.chat.id, "🚀 Instagram'dan video yuklanmoqda, iltimos kuting...")
        
        try:
            filename = f"insta_{user_id}.mp4"
            
            # Instagram bloklarini 100% yakson qiluvchi maxsus yt-dlp konfiguratsiyasi:
            ydl_opts = {
                'format': 'best',
                'outtmpl': filename,
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'geo_bypass': True,
                # Instagram botlarni aniqlay olmaydigan eng so'nggi desktop brauzer imitatsiyasi
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1'
                },
                # Tarmoq argumentlarini almashtirish orqali cheklovlarni aylanib o'tish:
                'extractor_args': {
                    'instagram': {
                        'client_id': ['null'],
                        'embed': True
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=True)
                title = info.get('title', 'Instagram Reels')[:350]
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🎵 Musiqasini ajratib olish (MP3)", callback_data=f"convert_{user_id}"),
                types.InlineKeyboardButton("🔗 Havolani yuklab olish", url=clean_url),
                types.InlineKeyboardButton("📲 Videoni ulashish", switch_inline_query=f"Instagram video: {clean_url}")
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
            print(f"Asosiy yuklash xatosi: {e}")
            bot.edit_message_text(
                "❌ Instagram videosini yuklab boʻlmadi.\n\n"
                "💡 Havola xato, profil yopiq yoki ushbu video cheklangan. Boshqa ochiq profil havolasini yuborib ko'ring.", 
                message.chat.id, 
                wait_msg.message_id
            )
    else:
        bot.send_message(message.chat.id, "❌ Iltimos, toʻgʻri Instagram havolasini yuboring!")

print("Bot 100% mustahkam rejimda ishga tushdi...")
bot.polling(none_stop=True)

