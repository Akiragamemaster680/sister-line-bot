from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
openai.api_key = os.environ["OPENAI_API_KEY"]

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text

    prompt = f"""あなたは懺悔室で悩みを聞いてくれる優しいシスターです。
ユーザーが話す悩みに対して、まず共感し、やさしく、そして神の愛に満ちた励ましを返してください。
悩み: {user_input}
シスター:"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたはカトリック教会のシスターです。"},
            {"role": "user", "content": prompt}
        ]
    )
    reply = response["choices"][0]["message"]["content"]
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

from waitress import serve
serve(app, host="0.0.0.0", port=3000)
