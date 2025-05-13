from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
import requests, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

client = WebClient(token=SLACK_BOT_TOKEN)
verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return "Unauthorized", 403

    data = request.get_json()

    # ✅ Slack gửi yêu cầu xác minh (challenge)
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data.get("challenge")})

    # ✅ Xử lý mention bot
    if "event" in data:
        event = data["event"]
        if event.get("type") == "app_mention":
            user_input = event.get("text").split('>', 1)[-1].strip()
            channel = event.get("channel")

            # Gửi đến Hugging Face
            response_text = query_huggingface(user_input)

            # Trả lời trong Slack
            client.chat_postMessage(channel=channel, text=response_text)

    return jsonify({"status": "ok"})

def query_huggingface(prompt):
    HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": f"<s>[INST] {prompt} [/INST]",
        "parameters": {"max_new_tokens": 200}
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()[0]['generated_text']
        return "Javis không thể trả lời lúc này."
    except:
        return "Lỗi khi gọi AI."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
