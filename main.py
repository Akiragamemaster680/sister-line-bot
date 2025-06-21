import openai, os
openai.api_key = os.getenv("OPENAI_API_KEY")

@handler.add(MessageEvent, message=TextMessage)
def sister(event):
    user_text = event.message.text
    prompt = (
        "あなたは懺悔室の優しいシスターです。"
        "ユーザーの悩みに共感し、温かい励ましを与えてください。\n"
        f"悩み: {user_text}"
    )

    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",   # 必要なら gpt-4o-mini 等に変更
        messages=[
            {"role": "system", "content": "あなたは心優しいシスター"},
            {"role": "user",   "content": prompt}
        ]
    )
    reply = res.choices[0].message.content.strip()
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )
