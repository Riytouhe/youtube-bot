#!/usr/bin/env python3
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DOWNLOAD_PATH = "/tmp/youtube_downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🎬 *YouTube Bot - 24/7 Running* ☁️
Send YouTube URL to download!
    """, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send YouTube URL\nChoose Video or Audio")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not any(x in url for x in ['youtube.com', 'youtu.be']):
        await update.message.reply_text("❌ Invalid URL")
        return
    keyboard = [['📹 Video', '🎵 Audio']]
    await update.message.reply_text("Choose:", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    context.user_data['url'] = url

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    url = context.user_data.get('url')
    if not url:
        await update.message.reply_text("Send URL first")
        return
    
    await update.message.reply_text("⏳ Downloading...")
    try:
        if '📹' in choice:
            opts = {'format': 'best[ext=mp4]/best', 'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s')}
        else:
            opts = {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}], 'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s')}
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            await update.message.reply_text(f"✅ Done: {info.get('title', 'Video')}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: handle_url(u, c) if any(x in u.message.text for x in ['youtube.com', 'youtu.be']) else handle_choice(u, c)))
    app.add_error_handler(error_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
