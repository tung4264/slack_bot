# import os
# from slack_bolt import App
# from slack_bolt.adapter.socket_mode import SocketModeHandler
# from openai import OpenAI
# from dotenv import load_dotenv
#
# load_dotenv()
#
# SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
# SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
#
# # Khởi tạo client OpenAI dùng OpenRouter
# client = OpenAI(
#     api_key=OPENROUTER_API_KEY,
#     base_url="https://openrouter.ai/api/v1"
# )
#
# app = App(token=SLACK_BOT_TOKEN)
#
# @app.event("app_mention")
# def handle_app_mention(event, say):
#     user = event.get("user")
#     text = event.get("text")
#     print(f"Nhận được: {text}")
#     try:
#         response = client.chat.completions.create(
#             model="meta-llama/llama-3.1-8b-instruct:free",  # Mô hình miễn phí từ OpenRouter
#             messages=[{"role": "user", "content": text}]
#         )
#         reply = response.choices[0].message.content
#     except Exception as e:
#         print(f"Lỗi gọi OpenRouter: {e}")
#         reply = "Mình đang gặp sự cố khi gọi AI. Vui lòng thử lại sau nhé."
#     say(f"<@{user}> {reply}")
#
# if __name__ == "__main__":
#     print("⚡ Bot Slack AI đang chạy với OpenRouter...")
#     SocketModeHandler(app, SLACK_APP_TOKEN).start()


import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Model Hugging Face để sử dụng
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

app = App(token=SLACK_BOT_TOKEN)

def query_huggingface(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "return_full_text": False
        }
    }
    response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        generated = response.json()
        if isinstance(generated, list):
            return generated[0]['generated_text']
        else:
            return "Không hiểu phản hồi từ HuggingFace."
    else:
        print(f"Error {response.status_code}: {response.text}")
        return "Mình không thể gọi HuggingFace API lúc này."

@app.event("app_mention")
def handle_app_mention(event, say):
    user = event.get("user")
    text = event.get("text")
    print(f"Nhận được: {text}")
    # Loại bỏ mention (@bot) khỏi text
    cleaned_text = text.split('>', 1)[-1].strip()

    reply = query_huggingface(cleaned_text)
    say(f"<@{user}> {reply}")

if __name__ == "__main__":
    print("⚡ Slackbot AI đang chạy với HuggingFace...")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
