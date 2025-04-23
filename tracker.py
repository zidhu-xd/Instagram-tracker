import os
import time
import json
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tracker.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables from GitHub Secrets
INSTA_USERNAME = os.getenv('INSTA_USERNAME')
INSTA_PASSWORD = os.getenv('INSTA_PASSWORD')
TARGET_USERNAME = os.getenv('TARGET_USERNAME')

# Configuration
CONFIG = {
    'data_file': 'data.json',
    'check_interval': 60,  # Seconds between checks (for testing)
    'max_retries': 3
}

def load_previous_data():
    try:
        if os.path.exists(CONFIG['data_file']):
            with open(CONFIG['data_file'], 'r') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading previous data: {e}")
    return None

def save_current_data(data):
    try:
        with open(CONFIG['data_file'], 'w') as f:
            json.dump(data, f, indent=2)
        logging.info("Data saved successfully")
    except Exception as e:
        logging.error(f"Error saving data: {e}")

def initialize_client():
    cl = Client()
    cl.delay_range = [2, 5]  # More human-like behavior
    
    # Load session if exists to avoid frequent logins
    session_file = 'session.json'
    try:
        if os.path.exists(session_file):
            cl.load_settings(session_file)
    except Exception as e:
        logging.warning(f"Couldn't load session: {e}")

    for attempt in range(CONFIG['max_retries']):
        try:
            cl.login(INSTA_USERNAME, INSTA_PASSWORD)
            cl.dump_settings(session_file)
            logging.info("Login successful")
            return cl
        except ChallengeRequired:
            logging.error("Challenge required! Check your Instagram for verification")
            break
        except LoginRequired as e:
            logging.warning(f"Login failed (attempt {attempt + 1}): {e}")
            time.sleep(10)
    return None

def get_user_data(cl, username):
    try:
        user_id = cl.user_id_from_username(username)
        user_info = cl.user_info(user_id)
        
        # Get limited follower/following data to avoid rate limits
        followers = list(cl.user_followers(user_id, amount=20).keys())
        following = list(cl.user_following(user_id, amount=20).keys())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'user_id': user_id,
            'full_name': user_info.full_name,
            'biography': user_info.biography,
            'follower_count': user_info.follower_count,
            'following_count': user_info.following_count,
            'media_count': user_info.media_count,
            'recent_followers': followers,
            'recent_following': following,
            'is_private': user_info.is_private,
            'profile_pic_url': user_info.profile_pic_url
        }
    except Exception as e:
        logging.error(f"Error getting user data: {e}")
        return None

def compare_data(old_data, new_data):
    changes = []
    if not old_data:
        return ["Initial data collection"]
    
    # Simple comparison to avoid GitHub Actions timeouts
    for field in ['full_name', 'biography', 'follower_count', 'following_count', 'media_count']:
        if old_data.get(field) != new_data.get(field):
            changes.append(f"{field} changed from {old_data.get(field)} to {new_data.get(field)}")
    
    return changes

def main():
    logging.info("Starting Instagram Tracker")
    
    cl = initialize_client()
    if not cl:
        return
    
    try:
        previous_data = load_previous_data()
        current_data = get_user_data(cl, TARGET_USERNAME)
        
        if current_data:
            changes = compare_data(previous_data, current_data)
            if changes:
                logging.info("Changes detected:")
                for change in changes:
                    logging.info(change)
                save_current_data(current_data)
            else:
                logging.info("No changes detected")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
    finally:
        logging.info("Script completed")

if __name__ == "__main__":
    main()
