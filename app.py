import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Cấu hình OpenAI client sử dụng OpenRouter
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

app = App(token=SLACK_BOT_TOKEN)

@app.event("app_mention")
def handle_app_mention(event, say):
    user = event.get("user")
    text = event.get("text")
    print(f"Nhận được: {text}")
    if "hey javis" in text.lower():
        try:
            response = client.chat.completions.create(
                model="meta-llama/llama-3.1-8b-instruct:free",  # Thay bằng Model ID bạn muốn sử dụng
                messages=[{"role": "user", "content": text}]
            )
            reply = response.choices[0].message.content
        except Exception as e:
            print(f"Lỗi gọi OpenRouter: {e}")
            reply = "Xin lỗi, mình không gọi được OpenRouter lúc này. Hãy thử lại sau nhé."
        say(f"<@{user}> {reply}")
    else:
        say(f"<@{user}> Gọi mình bằng 'hey javis' nha!")

if __name__ == "__main__":
    print("⚡ Bot Slack AI đang chạy với OpenRouter...")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
