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
Memory: bot remembers your name & chat context.
"""

ABOUT_MSG = """
💀 **Sevr0c–Moros AI**
Made by: @iamorosss & @sevr0c
Educational use only.
"""

# DB files
DB_FILE = "users.json"
MEMORY_FILE = "memory.json"

# ---------------- MEMORY SYSTEM ----------------

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    return json.load(open(MEMORY_FILE))

def save_memory(data):
    json.dump(data, open(MEMORY_FILE, "w"))

def remember(uid, role, message):
    memory = load_memory()
    if str(uid) not in memory:
        memory[str(uid)] = {"name": None, "history": []}

    memory[str(uid)]["history"].append({"role": role, "content": message})
    memory[str(uid)]["history"] = memory[str(uid)]["history"][-5:]   # last 5 msgs only

    save_memory(memory)

def set_username(uid, name):
    memory = load_memory()
    if str(uid) not in memory:
        memory[str(uid)] = {"name": name, "history": []}
    else:
        memory[str(uid)]["name"] = name
    save_memory(memory)

def get_memory(uid):
    memory = load_memory()
    if str(uid) not in memory:
        return None
    return memory[str(uid)]

# ---------------- USER SYSTEM ----------------

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

# ---------------- FORCE JOIN ----------------

async def is_joined_all(user_id, context):
    for cid, emoji, url in CHANNELS:
        try:
            m = await context.bot.get_chat_member(cid, user_id)
            if m.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

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

async def callback_handler(update, context):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    if not await is_joined_all(uid, context):
        await q.answer("❌ Not joined all!", show_alert=True)
        return

    await q.edit_message_reply_markup(
        InlineKeyboardMarkup([[InlineKeyboardButton("🟢 JOINED ✔", callback_data="done")]])
    )

    await context.bot.send_message(q.message.chat_id, "✅ Verified! You can now use the bot.")

# ---------------- AI SYSTEM ----------------

async def ai_response(uid, text):
    memory = get_memory(uid)

    # detect rename
    if text.lower().startswith("call me "):
        name = text[8:].strip()
        set_username(uid, name)
        return f"🔥 Okay! I'll remember your name **{name}**."

    # build message list for GPT
    messages = [{"role": "system", "content": "You are Yuvraj AI created by Yuvraj."}]

    if memory:
        if memory["name"]:
            messages.append({"role": "system", "content": f"User's name is {memory['name']}."})

        for item in memory["history"]:
            messages.append(item)

    messages.append({"role": "user", "content": text})

    try:
        out = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages
        )

        reply = out.choices[0].message.content

        remember(uid, "user", text)
        remember(uid, "assistant", reply)

        return reply

    except Exception as e:
        return f"❌ AI Error: {e}"

# ---------------- MAIN HANDLER ----------------

async def main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    uid = update.message.from_user.id
    add_user(uid)

    # Force join check
    if not await is_joined_all(uid, context):
        await send_force_join(update, context)
        return

    # ---------------- FIX: REPLY-TO MESSAGE MEMORY ----------------
    if update.message.reply_to_message:
        replied_text = update.message.reply_to_message.text
        if replied_text:
            remember(uid, "assistant", replied_text)  # bot's previous answer
        remember(uid, "user", msg)  # user's reply continuing convo
    # ---------------------------------------------------------------

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

    # BROADCAST
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

    # NORMAL CHAT
    await update.message.reply_text("💬 Thinking...")
    reply = await ai_response(uid, msg)
    await update.message.reply_text(reply, parse_mode="Markdown")

# ---------------- RUN BOT ----------------

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CallbackQueryHandler(callback_handler, pattern="check_join"))
app.add_handler(MessageHandler(filters.TEXT, main_handler))
app.run_polling()
