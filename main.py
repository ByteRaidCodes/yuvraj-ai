import os
import json
os.system("pip install openai==1.30.0 python-telegram-bot==20.3")

from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Load tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=OPENAI_KEY)

# Owners
OWNER_IDS = [8180209483, 7926496057]

# Banner image
PHOTO_PATH = "https://i.postimg.cc/76L59xVj/03cf19b6-e979-4d2f-9d6f-3ba2469e60c2.jpg"

# Channels
CHANNELS = [
    (-1002090323246, "⚡", "https://t.me/CodeTweakz"),
    (-1002145075313, "🔥", "https://t.me/Scripts0x"),
    (-1003279886990, "💎", "https://t.me/techmoros"),
    (-1002733321153, "🚀", "https://t.me/MethRoot"),
]

# Texts
CAPTION = """
💀 **Welcome to the Sevr0c–Moros AI ⚡**
Join all channels to access tools, scripts, & hacking resources.
"""
STATUS_MSG = """
💀 Sevr0c–Moros AI Status
━━━━━━━━━━━━━━━━━━
⚡ Bot is LIVE
🟢 No maintenance
🔥 All features working
"""
HELP_MSG = """
🛠 **Sevr0c–Moros AI Help**
/help – show commands
/about – about the bot
/start – status
/img (prompt) – generate AI images
"""
ABOUT_MSG = """
💀 **Sevr0c–Moros AI**
Made by: @iamorosss & @sevr0c
Educational use only.
"""

# User DB
DB_FILE = "users.json"

def load_users():
    if not os.path.exists(DB_FILE):
        return []
    return json.load(open(DB_FILE))

def save_users(users):
    json.dump(users, open(DB_FILE, "w"))

def add_user(uid):
    users = load_users()
    if uid not in users:
        users.append(uid)
        save_users(users)

# Check join
async def is_joined_all(user_id, context):
    for cid, emoji, url in CHANNELS:
        try:
            member = await context.bot.get_chat_member(cid, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# Force join UI
async def send_force_join(update, context):
    keyboard = [
        [
            InlineKeyboardButton("⚡ Join", url=CHANNELS[0][2]),
            InlineKeyboardButton("🔥 Join", url=CHANNELS[1][2]),
        ],
        [
            InlineKeyboardButton("💎 Join", url=CHANNELS[2][2]),
            InlineKeyboardButton("🚀 Join", url=CHANNELS[3][2]),
        ],
        [InlineKeyboardButton("⭕ JOINED ❌", callback_data="check_join")]
    ]
    await update.message.reply_photo(
        photo=PHOTO_PATH,
        caption=CAPTION,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Callback JOIN button
async def callback_handler(update, context):
    q = update.callback_query
    await q.answer()
    user = q.from_user.id

    if not await is_joined_all(user, context):
        await q.answer("❌ Not joined all!", show_alert=True)
        return

    await q.edit_message_reply_markup(
        InlineKeyboardMarkup([[InlineKeyboardButton("🟢 JOINED ✔", callback_data="done")]])
    )
    await context.bot.send_message(q.message.chat_id, "✅ Verified! You can now use the bot.")

# AI respond
async def ai_response(text):
    try:
        out = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Yuvraj AI created by Yuvraj."},
                {"role": "user", "content": text}
            ]
        )
        return out.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# 📸 IMAGE TO TEXT (VISION)
async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    # force join check
    if not await is_joined_all(uid, context):
        await send_force_join(update, context)
        return

    file = await update.message.photo[-1].get_file()
    img_bytes = await file.download_as_bytearray()

    await update.message.reply_text("🧠 Reading your image...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI that describes photos and extracts text."},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Describe this image & extract visible text."},
                        {"type": "input_image", "image": img_bytes}
                    ]
                }
            ]
        )

        result = response.choices[0].message.content
        await update.message.reply_text(f"📄 **Image Result:**\n{result}", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# 👉 MAIN HANDLER (commands + AI + IMG GEN)
async def main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    uid = update.message.from_user.id
    add_user(uid)

    if not await is_joined_all(uid, context):
        await send_force_join(update, context)
        return

    # COMMANDS
    if msg.startswith("/start"):
        await update.message.reply_text(STATUS_MSG, parse_mode="Markdown")
        return

    if msg.startswith("/help"):
        await update.message.reply_text(HELP_MSG, parse_mode="Markdown")
        return

    if msg.startswith("/about"):
        await update.message.reply_text(ABOUT_MSG, parse_mode="Markdown")
        return

    # OWNER BROADCAST
    if msg.startswith("/broadcast"):
        if uid not in OWNER_IDS:
            await update.message.reply_text("❌ Not allowed.")
            return

        text = msg.replace("/broadcast", "").strip()
        users = load_users()
        count = 0

        for u in users:
            try:
                await context.bot.send_message(u, f"📢 {text}")
                count += 1
            except:
                pass

        await update.message.reply_text(f"Broadcast sent to {count} users.")
        return

    # IMAGE GENERATOR
    if msg.startswith("/img"):
        prompt = msg.replace("/img", "").strip()

        if prompt == "":
            await update.message.reply_text("🖼️ Use: `/img cat wearing sunglasses`", parse_mode="Markdown")
            return

        await update.message.reply_text("🎨 Creating image... wait 5 sec...")

        try:
            img = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024"
            )

            image_url = img.data[0].url

            await update.message.reply_photo(
                photo=image_url,
                caption=f"🎨 **Generated Image:**\n`{prompt}`",
                parse_mode="Markdown"
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
        return

    # AI CHAT
    await update.message.reply_text("💬 Working on it...")
    reply = await ai_response(msg)
    await update.message.reply_text(reply)

# RUN BOT
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CallbackQueryHandler(callback_handler, pattern="check_join"))
app.add_handler(MessageHandler(filters.PHOTO, image_handler))
app.add_handler(MessageHandler(filters.TEXT, main_handler))
app.run_polling()
