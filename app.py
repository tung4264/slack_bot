import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
app = App(token=SLACK_BOT_TOKEN)

@app.event("app_mention")
def handle_app_mention(event, say):
    user = event.get("user")
    text = event.get("text")
    print(f"Nhận được: {text}")
    if "hey javis" in text.lower():
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}]
        )
        reply = response.choices[0].message.content
        say(f"<@{user}> {reply}")
    else:
        say(f"<@{user}> Gọi mình bằng 'hey javis' nha!")

if __name__ == "__main__":
    print("⚡ Bot Slack AI đang chạy...")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
