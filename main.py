import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv("7325333749:AAGuciHvW6E0NJg4vlSk4L7jBi2la-oD37A")
openai.api_key = os.getenv("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")

async def ai_response(text):
    response = openai.ChatCompletion.create(
        model="gpt-5.1-mini",
        messages=[{"role": "user", "content": text}]
    )
    return response.choices[0].message["content"]

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Thinking...")
    reply = await ai_response(update.message.text)
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))

app.run_polling()