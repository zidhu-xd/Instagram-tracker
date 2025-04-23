# app.py
from flask import Flask, request
import pandas as pd
import requests
import os

app = Flask(__name__)

BOT_TOKEN = "7813940268:AAHTnEJq9dBObZPxZ7K4qR18QgdQxbyfgl4"
CHAT_ID = "8110106197"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

@app.route("/compare", methods=["POST"])
def compare():
    if 'following' not in request.files or 'followers' not in request.files:
        return "Both files are required", 400

    following_file = request.files['following']
    followers_file = request.files['followers']

    following_df = pd.read_csv(following_file)
    followers_df = pd.read_csv(followers_file)

    following_set = set(following_df['userName'])
    followers_set = set(followers_df['userName'])

    not_following_back = following_set - followers_set
    not_followed_by_you = followers_set - following_set

    message = "<b>Comparison Result:</b>\n\n"
    message += f"<b>Not Following You Back ({len(not_following_back)}):</b>\n"
    for user in list(not_following_back)[:20]:
        message += f"• {user}\n"

    message += f"\n<b>You Don't Follow Back ({len(not_followed_by_you)}):</b>\n"
    for user in list(not_followed_by_you)[:20]:
        message += f"• {user}\n"

    send_telegram_message(message)

    return "Comparison complete. Results sent to Telegram."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
