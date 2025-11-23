import os
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Load tokens safely
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# AI function
async def ai_response(text):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Yuvraj AI made by Yuvraj."},
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Error: {str(e)}"

# Message handler
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Yuvraj AI is typing...")
    reply = await ai_response(update.message.text)
    await update.message.reply_text(reply)

# Run bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
app.run_polling()
