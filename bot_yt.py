import telebot
from telebot import types
from dotenv import load_dotenv
import yt_dlp
import re
import os


load_dotenv()

# Get BOT_TOKEN from .env
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in .env file")

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Ensure downloads folder exists
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# URL regex pattern
url_pattern = re.compile(r'(https?://[^\s]+)')

# Temporary storage
message_urls = {}
search_results = {}

# --- Download functions ---
def download_video(url):
    ydl_opts = {'format': 'best', 'outtmpl': 'downloads/%(title)s.%(ext)s'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def download_audio(url, audio_format='mp3'):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'downloads/%(title)s.{audio_format}',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return f"downloads/{info['title']}.{audio_format}"

# --- Handle direct URLs ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    urls = url_pattern.findall(message.text)
    if urls:
        chat_id = message.chat.id
        message_urls[chat_id] = urls[0]

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("Download Video", callback_data="video"),
            types.InlineKeyboardButton("Download Audio MP3", callback_data="audio_mp3"),
            types.InlineKeyboardButton("Download Audio M4A", callback_data="audio_m4a"),
            types.InlineKeyboardButton("Download Audio WAV", callback_data="audio_wav")
        )
        bot.reply_to(message, "Choose download type:", reply_markup=keyboard)
    else:
        bot.reply_to(message, "No valid URL found. Or use /search <keywords> to search YouTube.")

# --- Search command ---
@bot.message_handler(commands=['search'])
def search_command(message):

    query = message.text[len("/search"):].strip()

    if not query:
        bot.reply_to(message, "Please provide a search query. Example:\n/search funny cats")
        return

    bot.reply_to(message, f"Searching YouTube for: {query}...")

    ydl_opts = {'quiet': True, 'extract_flat': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch5:{query}", download=False)
        videos = info['entries']

    chat_id = message.chat.id
    search_results[chat_id] = {}

    for idx, video in enumerate(videos):
        title = video['title']
        url = video['url']
        search_results[chat_id][str(idx)] = url

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("Video", callback_data=f"video_{idx}"),
            types.InlineKeyboardButton("Audio MP3", callback_data=f"audio_mp3_{idx}"),
            types.InlineKeyboardButton("Audio M4A", callback_data=f"audio_m4a_{idx}"),
            types.InlineKeyboardButton("Audio WAV", callback_data=f"audio_wav_{idx}")
        )
        bot.send_message(chat_id, f"{idx + 1}. {title}", reply_markup=keyboard)


# --- Handle inline button presses ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    data = call.data

    # Determine source: direct URL or search
    if chat_id in message_urls:
        url = message_urls[chat_id]
        del message_urls[chat_id]
    elif chat_id in search_results:
        parts = data.split("_")
        type_ = parts[0]
        idx = parts[1]
        url = search_results[chat_id].get(idx)
        if not url:
            bot.answer_callback_query(call.id, "URL not found.")
            return
    else:
        bot.answer_callback_query(call.id, "No URL found.")
        return

    bot.answer_callback_query(call.id, "Downloading...")

    try:
        if data.startswith("video"):
            file_path = download_video(url)
            with open(file_path, 'rb') as f:
                bot.send_video(chat_id, f)
        elif data.startswith("audio"):
            fmt = data.split("_")[1]  # mp3, m4a, wav
            file_path = download_audio(url, audio_format=fmt)
            with open(file_path, 'rb') as f:
                bot.send_audio(chat_id, f)
        os.remove(file_path)
    except Exception as e:
        bot.send_message(chat_id, f"Error: {e}")

print("Bot is running...")
bot.polling()