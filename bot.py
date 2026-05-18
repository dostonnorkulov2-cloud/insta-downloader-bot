import http.server
import socketserver
import threading
import telebot
from telebot import types
import requests

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

# --- 4. SHAFFOF MENU ---
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
        bot.answer_callback_query(call.id, "Musiqa ajratilmoqda... 🎵")
        
        if target_id not in user_downloads:
            bot.send_message(call.message.chat.id, "❌ Xatolik: Havola muddati tugagan.")
            return
            
        audio_url = user_downloads[target_id]['audio_url']
        try:
            bot.send_audio(call.message.chat.id, audio_url, caption="🎵 @Uzzsv7 va @ivella_x777 hamkorligida")
        except Exception as e:
            bot.send_message(call.message.chat.id, "❌ Musiqani yuborib bo'lmadi.")

# --- 7. COBALT PROXY INFRASTRUKTURASI BILAN INSTAGRAM YUKLASH ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        start(message)
        return

    url = message.text
    if "instagram.com" in url:
        wait_msg = bot.send_message(message.chat.id, "🚀 Instagram'dan video yuklanmoqda, iltimos kuting...")
        
        # Dunyodagi eng kuchli Cobalt yuklash API-si (Hech qachon bloklanmaydi):
        cobalt_api = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Referer": "https://cobalt.tools/"
        }
        payload = {
            "url": url,
            "videoQuality": "max",  # Ultra HD/4K sifatda sug'urib olish
            "audioFormat": "mp3",
            "isAudioOnly": False
        }
        
        try:
            response = requests.post(cobalt_api, json=payload, headers=headers, timeout=15).json()
            video_url = response.get("url")
            
            if video_url:
                # MP3 tugmasi uchun ma'lumotlarni saqlaymiz
                user_downloads[user_id] = {'audio_url': video_url}
                
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton("🎵 Musiqasini ajratib olish (MP3)", callback_data=f"convert_{user_id}"),
                    types.InlineKeyboardButton("🔗 Havolani yuklab olish", url=url),
                    types.InlineKeyboardButton("📲 Videoni ulashish", switch_inline_query=f"Instagram video: {url}")
                )
                
                bot.send_video(
                    message.chat.id, 
                    video_url, 
                    caption=f"🎬 **Instagram Reels**\n\n🤖 @Uzzsv7 va @ivella_x777 hamkorligida",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
                bot.delete_message(message.chat.id, wait_msg.message_id)
                return
            else:
                raise Exception("Cobalt xatosi")
                
        except Exception as e:
            print(f"Cobalt xatosi: {e}")
            # --- ZAXIRA (BACKUP API) TIZIMI ---
            try:
                backup_url = f"https://api.bhg.ooo/instagram?url={url}"
                res = requests.get(backup_url, timeout=12).json()
                direct_url = res.get("url") or res.get("data", [{}])[0].get("url")
                
                if direct_url:
                    user_downloads[user_id] = {'audio_url': direct_url}
                    markup = types.InlineKeyboardMarkup(row_width=1)
                    markup.add(
                        types.InlineKeyboardButton("🎵 Musiqasini ajratib olish (MP3)", callback_data=f"convert_{user_id}"),
                        types.InlineKeyboardButton("🔗 Havolani yuklab olish", url=url)
                    )
                    bot.send_video(
                        message.chat.id, 
                        direct_url, 
                        caption=f"🎬 **Instagram Reels (Zaxira liniyasi)**\n\n🤖 @Uzzsv7 va @ivella_x777 hamkorligida",
                        reply_markup=markup,
                        parse_mode="Markdown"
                    )
                    bot.delete_message(message.chat.id, wait_msg.message_id)
                else:
                    bot.edit_message_text("❌ Instagram videosini yuklab boʻlmadi. Havola xato yoki profil yopiq.", message.chat.id, wait_msg.message_id)
            except Exception as err:
                bot.edit_message_text("❌ Serverda uzilish yuz berdi. Bir necha daqiqadan so'ng qayta urinib ko'ring.", message.chat.id, wait_msg.message_id)
    else:
        bot.send_message(message.chat.id, "❌ Iltimos, toʻgʻri Instagram havolasini yuboring!")

print("Bot 100% professional rejimda ishga tushdi...")
bot.polling(none_stop=True)

