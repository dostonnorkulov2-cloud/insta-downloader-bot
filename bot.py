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

# --- 2. BOT VA ADMIN SOZLAMALARI (TOKEN GʻISHTDEK JOYIDA!) ---
BOT_TOKEN = "8378410376:AAEIVC8SRZd3534Klx9ho1NXuF_uwpevuXg"
ADMIN_ID = 123456789  # Oʻzingning Telegram ID raqamingni shunga almashtirib qoʻysang boʻladi, jigar!

bot = telebot.TeleBot(BOT_TOKEN)

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

# --- 4. ASOSIY MENU KLAVIATURASI ---
def main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Loyiha Kanali 📢", "Bot Haqida ℹ️")
    markup.row("Qoʻllanma 📖", "Bot Yaratuvchisi 🧑‍💻")
    return markup

def set_bot_menu_button():
    try:
        pass
    except Exception as e:
        print(f"Menu button xatosi: {e}")

# --- 5. START BUYRUGʻI ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
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
        bot.send_message(message.chat.id, "📊 Bot statistikasi yuklanmoqda...")
    else:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat bot admini uchun!")

@bot.message_handler(commands=['send'])
def admin_send_reklama(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat bot admini uchun!")
        return
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
        # Sening yt_dlp video yuklash koding shu yerda ishlaydi jigar!
    else:
        bot.send_message(message.chat.id, "❌ Iltimos, faqat toʻgʻri Instagram havolasini yuboring!")

# --- 9. BOTNI JONLANTIRISH ---
print("Bot muvaffaqiyatli ishga tushmoqda...")
bot.polling(none_stop=True)

