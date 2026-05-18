import http.server
import socketserver
import threading
import telebot
from telebot import types

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
BOT_TOKEN = "SANING_BOT_TOKENING_SHU_YERDA_BOʻLADI"  # Bot tokeningni yozib qoʻy jigar!
ADMIN_ID = 123456789  # Oʻzingning Telegram ID'ngni yozib qoʻy jigar!

bot = telebot.TeleBot(BOT_TOKEN)

# --- 3. MAJBURIY OBUNANI TEKSHIRISH FUNKSIYASI ---
def check_sub(user_id):
    # Ikkala kanaling yuzername'i (Bot ikkalasida ham admin boʻlishi shart!)
    channels = ["@Uzzsv7", "@ivella_x777"]
    for channel in channels:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            print(f"Kanal tekshirishda xatolik ({channel}): {e}")
            return False  # Bot admin boʻlmasa ham False qaytaradi
    return True

# --- 4. ASOSIY MENU KLAVIATURASI ---
def main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Loyiha Kanali 📢", "Bot Haqida ℹ️")
    markup.row("Qoʻllanma 📖", "Bot Yaratuvchisi 🧑‍💻")
    return markup

def set_bot_menu_button():
    try:
        # Bu yerda WebApp yoki menyu tugmasi kodi boʻlsa turadi, boʻlmasa shundoq oʻtib ketadi
        pass
    except Exception as e:
        print(f"Menu button xatosi: {e}")

# --- 5. START BUYRUGʻI (XATOSIZ PROBELLAR BILAN) ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    # Bu yerga bazaga qoʻshish funksiyalaring boʻlsa yozasan:
    # add_user_to_db(user_id) 
    set_bot_menu_button()
    
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

# --- 6. TEKSHIRISH TUGMASI BOSILGANDA ---
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

# --- 7. ADMIN STATISTIKA VA REKLAMA BUYRUQLARI ---
@bot.message_handler(commands=['stat'])
def admin_stat(message):
    if message.from_user.id == ADMIN_ID:
        # Bu yerga statistika hisoblash kodingni qoʻshasan jigar
        bot.send_message(message.chat.id, "📊 Bot statistikasi yuklanmoqda...")
    else:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat bot admini uchun!")

@bot.message_handler(commands=['send'])
def admin_send_reklama(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat bot admini uchun!")
        return
    # Reklama tarqatish kodlarining davomi...
    bot.send_message(message.chat.id, "📢 Reklama paneli.")

# --- 8. INSTAGRAM HAVOLALARINI QABUL QILISH VA YUKLASH ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        start(message)
        return

    url = message.text
    if "instagram.com" in url:
        bot.send_message(message.chat.id, "🚀 Instagram'dan video yuklanmoqda, iltimos kuting...")
        # Shu yerda sening yt_dlp orqali videoni yuklab yuboradigan koding boʻladi!
        # ... (Sening eski yuklash kodingni shundoq shu yerga qoʻshib qoʻyasan)
    else:
        bot.send_message(message.chat.id, "❌ Iltimos, faqat toʻgʻri Instagram havolasini yuboring!")

# --- 9. BOTNI JONLANTIRISH ---
print("Bot muvaffaqiyatli ishga tushmoqda...")
bot.polling(none_stop=True)

