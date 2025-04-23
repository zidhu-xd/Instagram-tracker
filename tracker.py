import os
import time
import json
import logging
from datetime import datetime
from instagrapi import Client
from telegram.ext import Application
import asyncio

# Hardcoded credentials (replace with actual values)
INSTA_USERNAME = "titanabhi9"
INSTA_PASSWORD = "titanabhi123"
TARGET_USERNAME = "__.gou_ryy.__0_0"
TELEGRAM_TOKEN = "7813940268:AAHTnEJq9dBObZPxZ7K4qR18QgdQxbyfgl4"
TELEGRAM_CHAT_ID = "8110106197"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

async def send_telegram_message(message):
    try:
        # Initialize the Application for python-telegram-bot v22.0
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        await app.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        # Properly shut down the application to avoid hanging
        await app.shutdown()
    except Exception as e:
        logging.error(f"Telegram send failed: {e}")

async def track_instagram_account():
    # Validate credentials
    if not all([INSTA_USERNAME, INSTA_PASSWORD, TARGET_USERNAME, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        error_msg = "Missing required credentials. Please set INSTA_USERNAME, INSTA_PASSWORD, TARGET_USERNAME, TELEGRAM_TOKEN, and TELEGRAM_CHAT_ID."
        logging.error(error_msg)
        await send_telegram_message(f"❌ Error: {error_msg}")
        return

    cl = Client()
    try:
        # Instagram login with delay to avoid rate limits
        logging.info("Logging into Instagram...")
        cl.login(INSTA_USERNAME, INSTA_PASSWORD)
        time.sleep(5)  # Delay to avoid rate limiting

        # Get target user data
        logging.info(f"Fetching data for @{TARGET_USERNAME}...")
        user_id = cl.user_id_from_username(TARGET_USERNAME)
        user_info = cl.user_info(user_id)

        # Check if user_info is None or missing attributes
        if user_info is None:
            raise ValueError("User info could not be retrieved from Instagram")

        # Prepare message with safe attribute access
        bio = getattr(user_info, 'biography', 'N/A')[:100] if getattr(user_info, 'biography', None) else 'N/A'
        message = f"""
📊 Instagram Tracking Report ({datetime.now().strftime('%Y-%m-%d %H:%M')})

🔍 Account: @{TARGET_USERNAME}
👤 Name: {getattr(user_info, 'full_name', 'N/A')}
📝 Bio: {bio}...

📈 Stats:
• Followers: {getattr(user_info, 'follower_count', 0)}
• Following: {getattr(user_info, 'following_count', 0)}
• Posts: {getattr(user_info, 'media_count', 0)}
        """

        await send_telegram_message(message)

    except Exception as e:
        logging.error(f"Tracking failed: {e}")
        await send_telegram_message(f"❌ Error tracking @{TARGET_USERNAME}: {str(e)}")

if __name__ == "__main__":
    # Run the async function
    asyncio.run(track_instagram_account())
