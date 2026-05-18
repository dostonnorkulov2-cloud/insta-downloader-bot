import telebot
from telebot import types
import yt_dlp
import os
import shutil
import requests
import time

TOKEN = '8378410376:AAEIVC8SRZd3534Klx9ho1NXuF_uwpevuXg'
bot = telebot.TeleBot(TOKEN)
CHANNEL_ID = '@Uzzsv7'
ADMIN_ID = 6666622831  # 👑 Admin ID

# Mutloq barqaror va muammosiz ochiladigan Google Web App sifatida qo'yildi
WEB_APP_URL = "https://www.google.com"

user_downloads = {}
user_cooldowns = {}
USERS_FILE = "users.txt"

def add_user_to_db(user_id):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            f.write("")
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_users_count():
    if not os.path.exists(USERS_FILE):
        return 0
    with open(USERS_FILE, "r") as f:
        return len(f.read().splitlines())

def get_free_space():
    try:
        total, used, free = shutil.disk_usage("/data/data/com.termux/files/home")
        free_gb = free / (1024 * 1024 * 1024)
        if free_gb >= 1:
            return f"{free_gb:.2f} GB"
        else:
            return f"{free / (1024 * 1024):.2f} MB"
    except:
        return "Aniqlab bo'lmadi"

def recognize_audio_via_api(filename):
    try:
        short_audio = f"short_{filename}"
        os.system(f"ffmpeg -i {filename} -ss 00:00:00 -t 10 -acodec copy {short_audio} -y")
        with open(short_audio, 'rb') as f:
            files = {'file': f}
            response = requests.post('https://api.audd.io/', files=files, data={'api_token': 'test'})
            res_json = response.json()
        if os.path.exists(short_audio): os.remove(short_audio)
        if res_json.get('status') == 'success' and res_json.get('result'):
            result = res_json['result']
            return result.get('artist', "Noma'lum"), result.get('title', "Noma'lum")
    except:
        pass
    return "Noma'lum ijrochi", "Noma'lum musiqa"

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📢 Loyiha Kanali", url="https://t.me/Uzzsv7"),
        types.InlineKeyboardButton("ℹ️ Bot Haqida", callback_data="about_bot")
    )
    markup.add(
        types.InlineKeyboardButton("🌐 Onlayn Qidiruv (Web App)", web_app=types.WebAppInfo(url=WEB_APP_URL))
    )
    markup.add(
        types.InlineKeyboardButton("📖 Qo'llanma", callback_data="help_bot"),
        types.InlineKeyboardButton("👑 Bot Yaratuvchisi", callback_data="creator_bot")
    )
    return markup

def set_bot_menu_button():
    try:
        bot.set_chat_menu_button(menu_button=types.MenuButtonWebApp(
            type="web_app",
            text="🌐 Web App",
            web_app=types.WebAppInfo(url=WEB_APP_URL)
        ))
    except Exception as e:
        print(f"Menu button xatosi: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    add_user_to_db(user_id)
    set_bot_menu_button()
    
    if check_sub(user_id):
        bot.send_message(
            message.chat.id, 
            f"Salom {message.from_user.first_name}! 👋\n\nInstagram havolasini yuboring, uni eng maksimal sifatda yuklab beraman!\n\nYoki pastdagi Web App tugmalari orqali onlayn foydalaning! 👇",
            reply_markup=main_menu_markup()
        )
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Kanalga obuna bo'lish", url="https://t.me/Uzzsv7"))
        markup.add(types.InlineKeyboardButton("Tekshirish ✅", callback_data="check"))
        bot.send_message(message.chat.id, "Botdan foydalanish uchun kanalimizga obuna bo'ling!", reply_markup=markup)

@bot.message_handler(commands=['stat'])
def admin_stat(message):
    if message.from_user.id == ADMIN_ID:
        count = get_users_count()
        space = get_free_space()
        bot.send_message(message.chat.id, f"📊 Bot Statistikasi:\n\n👥 Jami foydalanuvchilar: {count} ta\n📦 Termux xotirasi: {space}")
    else:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat bot admini uchun!")

@bot.message_handler(commands=['send'])
def admin_send_reklama(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Bu buyruq faqat bot admini uchun!")
        return
    text_to_send = message.text.replace("/send", "").strip()
    if not text_to_send:
        bot.send_message(message.chat.id, "⚠️ Foydalanish: /send Reklama matni ko'rinishida yozing.")
        return
    if not os.path.exists(USERS_FILE):
        bot.send_message(message.chat.id, "❌ Foydalanuvchilar bazasi bo'sh!")
        return
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    wait_msg = bot.send_message(message.chat.id, f"🚀 {len(users)} ta foydalanuvchiga reklama yuborilmoqda...")
    success, failed = 0, 0
    for u_id in users:
        try:
            bot.send_message(int(u_id), text_to_send)
            success += 1
            time.sleep(0.05)
        except:
            failed += 1
    bot.edit_message_text(f"✅ Reklama tarqatish yakunlandi!\n\n👍 Yetkazildi: {success} ta\n👎 Bloklaganlar: {failed} ta", message.chat.id, wait_msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data in ["check", "about_bot", "help_bot", "creator_bot", "already_mp3"])
def handle_menu_callbacks(call):
    if call.data == "check":
        if check_sub(call.from_user.id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            set_bot_menu_button()
            bot.send_message(call.message.chat.id, "Rahmat! Instagram havolasini yuborishingiz mumkin. ✨", reply_markup=main_menu_markup())
        else:
            bot.answer_callback_query(call.id, "Siz hali obuna bo'lmadingiz! ❌", show_alert=True)
    elif call.data == "about_bot":
        bot.send_message(call.message.chat.id, "ℹ️ Bot Haqida:\n\nUshbu bot Instagram ijtimoiy tarmog'idan videolarni eng yuqori sifatda yuklash va MP3 formatga o'tkazish uchun maxsus yaratilgan.")
        bot.answer_callback_query(call.id)
    elif call.data == "help_bot":
        bot.send_message(call.message.chat.id, "📖 Foydalanish Qo'llanmasi:\n\nInstagram linkini nusxalab botga tashlang yoki pastdagi Web App tugmasi orqali onlayn interfeysni oching!")
        bot.answer_callback_query(call.id)
    elif call.data == "creator_bot":
        creator_markup = types.InlineKeyboardMarkup()
        creator_markup.add(types.InlineKeyboardButton("✍️ Admin bilan aloqa", url="https://t.me/PM_Dostonbek"))
        caption_creator = (
            "👑 Loyiha Muallifi: @PM_Dostonbek\n\n"
            "✨ Ushbu super-botning ortida tunni kunga ulab, eng so'nggi texnologiyalarni va "
            "zamonaviy Web App tizimini uyg'unlashtirgan daxshat dasturchi turibdi! 🦾🔥"
        )
        bot.send_message(call.message.chat.id, caption_creator, reply_markup=creator_markup)
        bot.answer_callback_query(call.id)
    elif call.data == "already_mp3":
        bot.answer_callback_query(call.id, "Bu fayl o'zi allaqachon MP3 formatda! 🎧", show_alert=True)

@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def handle_instagram_links(message):
    user_id = message.from_user.id
    add_user_to_db(user_id)
    if not check_sub(user_id):
        start(message)
        return
    current_time = time.time()
    if user_id in user_cooldowns and current_time - user_cooldowns[user_id] < 7:
        remaining = int(7 - (current_time - user_cooldowns[user_id]))
        bot.reply_to(message, f"⚠️ Iltimos, spam qilmang! Yana {remaining} soniya kuting.")
        return
    user_cooldowns[user_id] = current_time
    url = message.text
    user_downloads[user_id] = {'url': url}
    wait_msg = bot.send_message(message.chat.id, "🚀 Instagram'dan eng maksimal Ultra HD sifatda yuklanmoqda...")
    filename = f"insta_{user_id}.mp4"
    ydl_opts = {'format': 'bestvideo+bestaudio/best', 'outtmpl': filename, 'quiet': True, 'no_warnings': True, 'http_headers': {'User-Agent': 'Mozilla/5.0'}}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        title = info.get('title', 'Instagram Reels')[:350]
        free_space = get_free_space()
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🎵 Musiqasini ajratib olish (MP3)", callback_data=f"convert_{user_id}"),
            types.InlineKeyboardButton("🔗 Havolani yuklab olish", url=url),
            types.InlineKeyboardButton("📤 Videoni ulashish", switch_inline_query=f"Instagram'dagi daxshat video: {url}")
        )
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"📝 Izoh: {title}\n📦 Serverda joy: {free_space}\n\n✅ @Uzzsv7 kanali uchun maxsus.", reply_markup=markup)
        bot.delete_message(message.chat.id, wait_msg.message_id)
        if os.path.exists(filename): os.remove(filename)
    except Exception as e:
        print(e)
        bot.edit_message_text("❌ Instagram videosini yuklab bo'lmadi. Havola xato yoki profil yopiq.", message.chat.id, wait_msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("convert_"))
def convert_to_mp3_callback(call):
    user_id = int(call.data.split("_")[1])
    bot.answer_callback_query(call.id, "Videodan musiqa ajratilmoqda... ⏳")
    if user_id not in user_downloads: return
    url = user_downloads[user_id]['url']
    audio_file = f"converted_{user_id}"
    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': f"{audio_file}.%(ext)s", 'quiet': True, 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}
    wait_msg = bot.send_message(call.message.chat.id, "🎵 Musiqa yuqori sifatda tayyorlanmoqda...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        final_mp3 = f"{audio_file}.mp3"
        artist, song_title = recognize_audio_via_api(final_mp3)
        free_space = get_free_space()
        extra_markup = types.InlineKeyboardMarkup(row_width=1)
        extra_markup.add(types.InlineKeyboardButton("🎵 Musiqasini ajratib olish (MP3)", callback_data="already_mp3"), types.InlineKeyboardButton("🔗 Havolani yuklab olish", url=url), types.InlineKeyboardButton("📤 Videoni ulashish", switch_inline_query=f"Daxshat video ekan: {url}"))
        with open(final_mp3, 'rb') as f:
            bot.send_audio(call.message.chat.id, f, performer=artist, title=song_title, caption=f"✅ 🎵 {artist} - {song_title}\n📦 Serverda joy: {free_space}\n\n@Uzzsv7 loyihasi.", reply_markup=extra_markup)
        if os.path.exists(final_mp3): os.remove(final_mp3)
        bot.delete_message(call.message.chat.id, wait_msg.message_id)
    except Exception as e:
        print(e)
        bot.edit_message_text("❌ Musiqani ajratish jarayonida xatolik bo'ldi.", call.message.chat.id, wait_msg.message_id)

bot.polling(none_stop=True)

