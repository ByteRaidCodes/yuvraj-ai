import os
import json
os.system("pip install openai==1.30.0 python-telegram-bot==20.3")

from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters, CallbackQueryHandler

# Load tokens safely
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=OPENAI_KEY)

# OWNER IDS
OWNER_IDS = [8180209483, 7926496057]

# Banner image
PHOTO_PATH = "https://i.postimg.cc/76L59xVj/03cf19b6-e979-4d2f-9d6f-3ba2469e60c2.jpg"

# Force join channels
CHANNELS = [
    (-1002090323246, "⚡", "https://t.me/CodeTweakz"),
    (-1002145075313, "🔥", "https://t.me/Scripts0x"),
    (-1003279886990, "💎", "https://t.me/techmoros"),
    (-1002733321153, "🚀", "https://t.me/MethRoot"),
]

# Caption for force join
CAPTION = """
💀 **Welcome to the Sevr0c–Moros AI ⚡**
Inside this channel, you'll get access to advanced scripts, ethical hacking tutorials, powerful methods, hidden tricks, security tools, and real techniques used by professionals.

⚠️ **Everything is for educational use only.**
👉 Join all channels to unlock everything.
"""

# Status response
STATUS_MSG = """
💀 Sevr0c–Moros AI Status
━━━━━━━━━━━━━━━━━━
⚡ Bot is LIVE
🟢 No maintenance
🔥 All features working
"""

# Help menu
HELP_MSG = """
🛠 **Sevr0c–Moros AI Help Menu**
━━━━━━━━━━━━━━━━━━
/start – Start bot / check status
/help – List all commands
/about – About this bot
/broadcast – Owner-only (send message to all users)
"""

# About menu
ABOUT_MSG = """
💀 **Sevr0c–Moros AI**
━━━━━━━━━━━━━━━━━━
⚡ High-performance AI bot  
🔥 Ethical hacking | Tools | Scripts  
💠 Optimized for speed & accuracy  

👑 **Creators:**
• Owner – @iamorosss  
• Admin – @sevr0c  

⚠️ Educational & ethical use only.
"""

# Database file
DB_FILE = "users.json"

def load_users():
    if not os.path.exists(DB_FILE):
        return []
    return json.load(open(DB_FILE, "r"))

def save_users(users):
    json.dump(users, open(DB_FILE, "w"))

def add_user(uid):
    users = load_users()
    if uid not in users:
        users.append(uid)
        save_users(users)

# Check if user joined all channels
async def is_joined_all(user_id, context):
    for channel_id, emoji, link in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel_id, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# Send force join panel
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

# /start command
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    add_user(user_id)

    if not await is_joined_all(user_id, context):
        await send_force_join(update, context)
        return

    await update.message.reply_text(STATUS_MSG, parse_mode="Markdown")

# Callback JOIN check
async def callback_handler(update, context):
    query = update.callback_query
    await query.answer()

    user = query.from_user.id
    add_user(user)

    if not await is_joined_all(user, context):
        await query.answer("❌ You haven't joined all channels!", show_alert=True)
        return

    await query.edit_message_reply_markup(
        InlineKeyboardMarkup([[InlineKeyboardButton("🟢 JOINED ✔", callback_data="none")]])
    )

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="✅ Verified! You can now use the bot."
    )

# AI replying
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
        return f"❌ Error: {e}"

# Fallback command handler (ALWAYS WORKS)
async def fallback_commands(update, context):
    text = update.message.text.lower()

    if text.startswith("/help"):
        await update.message.reply_text(HELP_MSG, parse_mode="Markdown")
        return

    if text.startswith("/about"):
        await update.message.reply_text(ABOUT_MSG, parse_mode="Markdown")
        return

    # AI reply
    reply = await ai_response(update.message.text)
    await update.message.reply_text(reply)

# /broadcast
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id

    if user not in OWNER_IDS:
        await update.message.reply_text("❌ Only owners can use broadcast.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Usage:\n/broadcast your text")
        return

    msg = " ".join(context.args)

    users = load_users()
    sent = 0
    for uid in users:
        try:
            await context.bot.send_message(uid, f"📢 **Broadcast:**\n{msg}", parse_mode="Markdown")
            sent += 1
        except:
            pass

    await update.message.reply_text(f"✅ Sent to {sent} users.")

# RUN BOT
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start_cmd))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CallbackQueryHandler(callback_handler, pattern="check_join"))

# Fallback command handler for help/about always works
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), fallback_commands))

app.run_polling()
