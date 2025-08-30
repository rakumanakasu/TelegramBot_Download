---

# Telegram Bot Download

A simple **Telegram bot** that allows users to download videos and audio from YouTube links.
Supports **video download**, **audio formats**, and inline buttons.

---

## Features

* Download videos from YouTube links.
* Download audio .
* Inline buttons for easy selection of download type.
* Safe usage of **.env** to store your bot token.
* Temporary file cleanup after sending to keep storage light.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/rakumanakasu/TelegramBot_Download.git
cd TelegramBot_Download
```

---

### 2. Create `.env` file

```env
BOT_TOKEN=your_telegram_bot_token_here
```


---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt** should include:

```
pyTelegramBotAPI
python-dotenv
yt-dlp
```

---

### 4. Run the bot

```bash
python bot.py
```

* The bot will start polling for messages.
* Send a **YouTube link** to test video/audio download.

---

## Usage

* `/start` — Start the bot.
* Paste a YouTube link — Bot responds with inline buttons to download video or audio in your preferred format.

---

## Notes

* Make sure **FFmpeg** is installed on your system for best audio extraction.
* The bot uses a `downloads/` folder for temporary storage. Files are deleted after sending.


---

1️⃣ .env.example

file named .env.example in your project folder:

# Rename this file to .env and add your real bot token
BOT_TOKEN=your_telegram_bot_token_here

----

## License

This project is open-source and free to use.

---
