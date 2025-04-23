import os
import time
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import json

# Configuration
CONFIG = {
    'my_username': 'titanabhi9',
    'my_password': 'titanabhi123',
    'target_username': '__.gou_ryy.__0_0',
    'check_interval': 3600,  # Check every hour (in seconds)
    'log_file': 'instagram_tracker.log',
    'data_file': 'instagram_data.json'
}

def load_previous_data():
    if os.path.exists(CONFIG['data_file']):
        with open(CONFIG['data_file'], 'r') as f:
            return json.load(f)
    return None

def save_current_data(data):
    with open(CONFIG['data_file'], 'w') as f:
        json.dump(data, f, indent=2)

def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry, end='')
    with open(CONFIG['log_file'], 'a') as f:
        f.write(log_entry)

def initialize_client():
    cl = Client()
    try:
        cl.login(CONFIG['my_username'], CONFIG['my_password'])
        log_message("Successfully logged in to Instagram")
        return cl
    except Exception as e:
        log_message(f"Login failed: {str(e)}")
        return None

def get_user_data(cl, username):
    try:
        user_id = cl.user_id_from_username(username)
        user_info = cl.user_info(user_id)
        
        followers = cl.user_followers(user_id).keys()
        following = cl.user_following(user_id).keys()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'user_id': user_id,
            'full_name': user_info.full_name,
            'biography': user_info.biography,
            'follower_count': user_info.follower_count,
            'following_count': user_info.following_count,
            'media_count': user_info.media_count,
            'followers': list(followers),
            'following': list(following),
            'is_private': user_info.is_private,
            'profile_pic_url': user_info.profile_pic_url
        }
    except Exception as e:
        log_message(f"Error getting user data: {str(e)}")
        return None

def compare_data(old_data, new_data):
    changes = []
    
    if not old_data:
        changes.append("Initial data collection")
        return changes
    
    # Compare basic info
    if old_data['full_name'] != new_data['full_name']:
        changes.append(f"Name changed from '{old_data['full_name']}' to '{new_data['full_name']}'")
    
    if old_data['biography'] != new_data['biography']:
        changes.append("Bio has changed")
    
    # Compare counts
    if old_data['follower_count'] != new_data['follower_count']:
        diff = new_data['follower_count'] - old_data['follower_count']
        changes.append(f"Follower count changed by {diff} (now {new_data['follower_count']})")
    
    if old_data['following_count'] != new_data['following_count']:
        diff = new_data['following_count'] - old_data['following_count']
        changes.append(f"Following count changed by {diff} (now {new_data['following_count']})")
    
    if old_data['media_count'] != new_data['media_count']:
        diff = new_data['media_count'] - old_data['media_count']
        changes.append(f"Post count changed by {diff} (now {new_data['media_count']})")
    
    # Compare followers list
    old_followers = set(old_data['followers'])
    new_followers = set(new_data['followers'])
    
    lost_followers = old_followers - new_followers
    gained_followers = new_followers - old_followers
    
    if lost_followers:
        changes.append(f"Lost {len(lost_followers)} followers")
    
    if gained_followers:
        changes.append(f"Gained {len(gained_followers)} new followers")
    
    # Compare following list
    old_following = set(old_data['following'])
    new_following = set(new_data['following'])
    
    unfollowed = old_following - new_following
    new_following_added = new_following - old_following
    
    if unfollowed:
        changes.append(f"Unfollowed {len(unfollowed)} accounts")
    
    if new_following_added:
        changes.append(f"Started following {len(new_following_added)} new accounts")
    
    return changes

def main():
    log_message("Instagram Tracker started")
    
    previous_data = load_previous_data()
    cl = initialize_client()
    
    if not cl:
        return
    
    try:
        while True:
            current_data = get_user_data(cl, CONFIG['target_username'])
            
            if current_data:
                changes = compare_data(previous_data, current_data)
                
                if changes:
                    log_message(f"Changes detected for {CONFIG['target_username']}:")
                    for change in changes:
                        log_message(f"- {change}")
                    
                    # Save the current state
                    save_current_data(current_data)
                    previous_data = current_data
                else:
                    log_message(f"No changes detected for {CONFIG['target_username']}")
            
            time.sleep(CONFIG['check_interval'])
    
    except KeyboardInterrupt:
        log_message("Tracker stopped by user")
    except Exception as e:
        log_message(f"Tracker stopped due to error: {str(e)}")
    finally:
        cl.logout()

if __name__ == "__main__":
    main()
