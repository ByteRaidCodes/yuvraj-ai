import os
os.system("pip install openai==1.30.0 python-telegram-bot==20.3")

from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Load tokens safely
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# --- Force Join Settings ---
CHANNEL_ID = -1002090323246          # <<< REPLACE WITH YOUR CHANNEL ID
JOIN_LINK = "https://t.me/CodeTweakz"  # <<< REPLACE WITH YOUR CHANNEL LINK

client = OpenAI(api_key=OPENAI_KEY)


# -------------------------------
# FORCE JOIN CHECK FUNCTION
# -------------------------------
async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)

        # If user not joined or kicked
        if member.status in ["left", "kicked"]:
            await update.message.reply_text(
                f"🚫 To use this bot, you must join our channel first:\n\n👉 {JOIN_LINK}"
            )
            return False

        return True

    except Exception as e:
        await update.message.reply_text(
            f"⚠️ Please join our channel first:\n👉 {JOIN_LINK}"
        )
        return False



# -------------------------------
# AI FUNCTION
# -------------------------------
async def ai_response(text):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Yuvraj AI created by Yuvraj."},
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ Error: {str(e)}"



# -------------------------------
# MAIN MESSAGE HANDLER
# -------------------------------
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # 🔒 FORCE JOIN CHECK
    if not await force_join(update, context):
        return   # stop message processing

    # Typing message
    await update.message.reply_text("💬 Working on it...")

    # Generate reply
    reply = await ai_response(update.message.text)

    # Send final answer
    await update.message.reply_text(reply)



# -------------------------------
# RUN BOT
# -------------------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
app.run_polling()
