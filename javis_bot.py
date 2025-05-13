from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
import requests, os
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

app = Flask(__name__)
client = WebClient(token=SLACK_BOT_TOKEN)
verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def query_huggingface(prompt):
    payload = {
        "inputs": f"<s>[INST] {prompt} [/INST]",
        "parameters": {"max_new_tokens": 200, "temperature": 0.7}
    }
    response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()[0]['generated_text']
    return "Xin lỗi, Javis không thể phản hồi lúc này."

@app.route("/slack/events", methods=["POST"])
def slack_events():
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return "Invalid request", 403

    data = request.json
    if "event" in data:
        event = data["event"]
        if event.get("type") == "app_mention":
            user_input = event.get("text").split('>', 1)[-1].strip()
            channel = event.get("channel")
            response_text = query_huggingface(user_input)
            client.chat_postMessage(channel=channel, text=response_text)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
