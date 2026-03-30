#!/usr/bin/env python3
"""
Telegram YouTube Video Downloader Bot
Downloads directly to Gallery (DCIM folder)
"""

import os
import subprocess
import sys
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = "8688559022:AAHjt_9PFSedzF68TjsxBxPxrg9b9OQoqIQ"  # Get from @BotFather

# Save directly to Gallery
DOWNLOAD_PATH = "/storage/emulated/0/DCIM/YouTube"

def install_requirements():
    """Install required packages"""
    packages = ['python-telegram-bot', 'yt-dlp']
    
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} already installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🎬 *YouTube Video Downloader Bot* 🎬

Welcome! Videos download directly to your Gallery.

*How to use:*
1. Send me a YouTube URL
2. Choose format: Video or Audio
3. Check your Gallery app! 🎥

*Commands:*
/start - Show this message
/help - Get help
/gallery - Open Gallery

Just send me a YouTube link to get started! 🚀
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
*Help Guide*

📝 *Supported Formats:*
• MP4 Video (best quality)
• MP3 Audio only

🔗 *How to send links:*
Just paste any YouTube URL:
• youtube.com/watch?v=...
• youtu.be/...
• Short links supported

📱 *Where do files go?*
Videos go to: *Gallery → DCIM → YouTube* folder
They'll appear automatically in your Gallery app!

⚙️ *Features:*
• Auto-detects best quality
• Saves to Gallery automatically
• Shows progress updates

❓ *Issues?*
If download fails, check:
• Internet connection
• Valid YouTube link
• Storage space available

Use /gallery to open Gallery app
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def gallery_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gallery command"""
    gallery_text = """
📸 *Gallery Location*

Your downloaded videos are in:

📁 Gallery App → DCIM → YouTube

*To access:*
1. Open Gallery/Photos app
2. Look for "YouTube" folder in DCIM
3. Your videos are there!

*Or open Files:*
1. File Manager
2. Internal Storage → DCIM → YouTube

All new downloads appear here automatically! ✨
    """
    await update.message.reply_text(gallery_text, parse_mode='Markdown')

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle YouTube URLs"""
    url = update.message.text.strip()
    
    # Validate URL
    if not any(x in url for x in ['youtube.com', 'youtu.be']):
        await update.message.reply_text("❌ Please send a valid YouTube URL")
        return
    
    # Ask user to choose format
    keyboard = [
        ['📹 Download Video (MP4)', '🎵 Download Audio (MP3)']
    ]
    
    await update.message.reply_text(
        "Choose download format:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )
    
    # Store URL for next message
    context.user_data['youtube_url'] = url

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle format choice"""
    choice = update.message.text
    url = context.user_data.get('youtube_url')
    
    if not url:
        await update.message.reply_text("❌ No URL found. Please send a YouTube link first.")
        return
    
    await update.message.reply_text("⏳ Starting download... This may take a moment.")
    
    try:
        if '📹' in choice or 'Video' in choice:
            success = await download_video(url, update, context)
        elif '🎵' in choice or 'Audio' in choice:
            success = await download_audio(url, update, context)
        else:
            await update.message.reply_text("❌ Invalid choice")
            return
            
        if success:
            await update.message.reply_text(
                "✅ Download completed!\n\n"
                "📸 Check your Gallery:\n"
                "Gallery → DCIM → YouTube\n\n"
                "Use /gallery for help"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def download_video(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Download video from YouTube to Gallery"""
    try:
        import yt_dlp
        
        # Create DCIM/YouTube folder if it doesn't exist
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await update.message.reply_text("📥 Downloading video...")
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Video')
            
            await update.message.reply_text(
                f"✅ Downloaded: *{title}*\n\n"
                f"📸 Saved to Gallery!\n"
                f"📁 Folder: DCIM/YouTube",
                parse_mode='Markdown'
            )
            return True
            
    except Exception as e:
        await update.message.reply_text(f"❌ Video download failed: {str(e)}")
        return False

async def download_audio(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Download audio from YouTube to Gallery"""
    try:
        import yt_dlp
        
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s'),
            'quiet': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await update.message.reply_text("📥 Downloading audio...")
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Audio')
            
            await update.message.reply_text(
                f"✅ Downloaded: *{title}*\n\n"
                f"🎵 Format: MP3 (192kbps)\n"
                f"📸 Saved to Gallery!\n"
                f"📁 Folder: DCIM/YouTube",
                parse_mode='Markdown'
            )
            return True
            
    except Exception as e:
        await update.message.reply_text(f"❌ Audio download failed: {str(e)}")
        return False

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        await update.message.reply_text(
            "❌ An error occurred. Please try again or use /help"
        )
    except:
        pass

def main():
    """Start the bot"""
    print("=" * 50)
    print("   Telegram YouTube → Gallery Bot")
    print("=" * 50)
    
    # Install requirements
    print("\nInstalling dependencies...")
    install_requirements()
    
    # Create folder
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    print(f"✓ Gallery folder created: {DOWNLOAD_PATH}")
    
    # Check token
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n❌ ERROR: Please set your Telegram bot token!")
        print("\nHow to get a token:")
        print("1. Open Telegram and search for @BotFather")
        print("2. Start chat and type /newbot")
        print("3. Follow instructions to create bot")
        print("4. Copy the token and replace in the code")
        return
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("gallery", gallery_command))
    
    # Message handlers
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda u, c: handle_url(u, c) if any(x in u.message.text for x in ['youtube.com', 'youtu.be']) else handle_choice(u, c)
    ))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    print("✓ Bot is running!")
    print(f"✓ Downloads go to: {DOWNLOAD_PATH}")
    print("✓ Press Ctrl+C to stop\n")
    
    # Start polling
    application.run_polling()

if __name__ == '__main__':
    main()
