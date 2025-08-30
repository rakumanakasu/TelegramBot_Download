import os
import re
import yt_dlp
from telebot import TeleBot, types
from dotenv import load_dotenv

# Load .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN or ":" not in BOT_TOKEN:
    raise ValueError("Invalid Telegram bot token in .env")

bot = TeleBot(BOT_TOKEN)

if not os.path.exists('downloads'):
    os.makedirs('downloads')

url_pattern = re.compile(r'(https?://[^\s]+)')
message_urls = {}

# --- Download video ---
def download_video(url):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def download_audio_as_voice(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.ogg',
        'postprocessors': [],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# --- Handle messages ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    urls = url_pattern.findall(message.text)
    chat_id = message.chat.id

    if urls:
        message_urls[chat_id] = urls[0]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Download Video 🎬", callback_data="video"))
        keyboard.add(types.InlineKeyboardButton("Download Audio 🎵", callback_data="audio"))
        keyboard.add(types.InlineKeyboardButton("Send as Voice 🎤", callback_data="voice"))
        bot.send_message(chat_id, "Choose download type:", reply_markup=keyboard)
    else:
        bot.send_message(chat_id, "No valid YouTube URL found. Please send a valid link.")

# --- Handle button clicks ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    data = call.data

    if chat_id in message_urls:
        url = message_urls[chat_id]
        del message_urls[chat_id]
    else:
        bot.answer_callback_query(call.id, "No URL found.")
        return

    bot.answer_callback_query(call.id, "Downloading...")

    try:
        if data == "video":
            file_path = download_video(url)
            with open(file_path, 'rb') as f:
                bot.send_video(chat_id, f)
            os.remove(file_path)

        elif data == "audio":
            file_path = download_video(url)
            with open(file_path, 'rb') as f:
                bot.send_audio(chat_id, f)
            os.remove(file_path)

        elif data == "voice":
            file_path = download_audio_as_voice(url)
            with open(file_path, 'rb') as f:
                bot.send_voice(chat_id, f)
            os.remove(file_path)

    except Exception as e:
        bot.send_message(chat_id, f"Error: {e}")


print("Bot is running...")
bot.polling()
