import os
import time
import json
import logging
from datetime import datetime
from instagrapi import Client
from telegram import Bot
from telegram.error import TelegramError

# Load secrets
INSTA_USERNAME = os.getenv('INSTA_USERNAME')
INSTA_PASSWORD = os.getenv('INSTA_PASSWORD')
TARGET_USERNAME = os.getenv('TARGET_USERNAME')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def send_telegram_message(message):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except TelegramError as e:
        logging.error(f"Telegram send failed: {e}")

def track_instagram_account():
    cl = Client()
    try:
        # Instagram login
        cl.login(INSTA_USERNAME, INSTA_PASSWORD)
        
        # Get target user data
        user_id = cl.user_id_from_username(TARGET_USERNAME)
        user_info = cl.user_info(user_id)
        
        # Prepare message
        message = f"""
📊 Instagram Tracking Report ({datetime.now().strftime('%Y-%m-%d %H:%M')})
        
🔍 Account: @{TARGET_USERNAME}
👤 Name: {user_info.full_name}
📝 Bio: {user_info.biography[:100]}...
        
📈 Stats:
• Followers: {user_info.follower_count}
• Following: {user_info.following_count}
• Posts: {user_info.media_count}
        """
        
        send_telegram_message(message)
        
    except Exception as e:
        logging.error(f"Tracking failed: {e}")
        send_telegram_message(f"❌ Error tracking @{TARGET_USERNAME}: {str(e)}")

if __name__ == "__main__":
    track_instagram_account()
