# main.py  ----------------------------------------------
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from waitress import serve
import openai, os, traceback

app = Flask(__name__)

# ★ 環境変数（Render の Environment で設定）
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler      = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
openai.api_key = os.getenv("OPENAI_API_KEY")

# ------------------------------------------------------
@app.route("/callback", methods=["POST"])
def callback():
    """LINE からの Webhook を受け取るエンドポイント"""
    signature = request.headers.get("X-Line-Signature", "")
    body      = request.get_data(as_text=True)

    # --- デバッグ用ログ -----------------------------
    print("◆ Callback hit")               # ← これが Logs に出れば届いている
    print(body)                            # ペイロード内容
    # -----------------------------------------------

    try:
        handler.handle(body, signature)

    except InvalidSignatureError as e:
        # シークレットが違うとここで 400
        print("Signature error:", e)
        return "invalid signature", 400

    except LineBotApiError as e:
        # LINE 側へ返信失敗（トークン誤りなど）
        print("LineBotApiError:", e)
        return "OK", 200                  # LINE へは 200 を返して既定文を抑止

    except Exception as e:
        # OpenAI 失敗などその他の例外
        print("Internal error:", e)
        traceback.print_exc()
        return "OK", 200                  # 同上

    return "OK", 200

# ------------------------------------------------------
@handler.add(MessageEvent, message=TextMessage)
def sister(event):
    """ユーザーの悩みにシスターが応える"""
    user_text = event.message.text
    prompt = (
        "あなたは懺悔室の優しいシスターです。口調はあらあらって感じで優しい雰囲気をまとっています。"
        "文章は80~120文字にして、ユーザーの悩みにまず共感し、次に温かい励ましを与えてください。\n"
        f"悩み: {user_text}"
    )

    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",   # 速さとコスト重視。gpt-4o-mini 等に替えてもOK
        messages=[
            {"role": "system", "content": "あなたは心優しいシスターです。"},
            {"role": "user",   "content": prompt}
        ],
        timeout=10              # 10 秒で打ち切り → LINE の30秒制限対策
    )

    reply = res.choices[0].message.content.strip()

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# ------------------------------------------------------
if __name__ == "__main__":
    # Render が自動で PORT を渡すので環境変数優先
    port = int(os.environ.get("PORT", 3000))
    serve(app, host="0.0.0.0", port=port)
# ------------------------------------------------------
