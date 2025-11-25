import os
os.system("pip install openai==1.30.0 python-telegram-bot==20.3 dnspython requests")
import json
import requests
import socket
import dns.resolver

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
/osint – open OSINT tools menu
"""

ABOUT_MSG = """
💀 **Sevr0c–Moros AI**
Made by: @iamorosss & @sevr0c

⚠️ Educational use only.
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

# Pending OSINT input
pending_osint = {}

# ---------------- OSINT MENU ---------------- #

def osint_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌐 IP Lookup", callback_data="osint_ip"),
            InlineKeyboardButton("📞 Phone Info", callback_data="osint_phone"),
        ],
        [
            InlineKeyboardButton("📧 Email Check", callback_data="osint_email"),
            InlineKeyboardButton("👤 Username OSINT", callback_data="osint_user"),
        ],
        [
            InlineKeyboardButton("🌍 Domain Lookup", callback_data="osint_domain"),
            InlineKeyboardButton("⬅️ Back", callback_data="osint_back"),
        ]
    ])

async def osint_input_handler(update, context, tool):
    text = update.message.text

    if tool == "ip":
        try:
            r = requests.get(f"http://ip-api.com/json/{text}").json()
            reply = f"""
🌐 **IP Lookup Result**
Country: {r.get('country')}
Region: {r.get('regionName')}
City: {r.get('city')}
ZIP: {r.get('zip')}
ISP: {r.get('isp')}
"""
        except:
            reply = "❌ Invalid IP / API error."
        return reply

    if tool == "phone":
        reply = f"""
📞 **Phone Lookup**
Number: {text}
⚠️ Demo result only:
Country: India
Carrier: Airtel
Valid: True
"""
        return reply

    if tool == "email":
        domain = text.split("@")[-1]
        try:
            dns.resolver.resolve(domain, "MX")
            valid = True
        except:
            valid = False
        reply = f"""
📧 **Email Check**
Email: {text}
Domain Valid: {"Yes" if valid else "No"}
"""
        return reply

    if tool == "user":
        reply = f"""
👤 **Username OSINT**
Username: {text}

Instagram: https://instagram.com/{text}
GitHub: https://github.com/{text}
Twitter: https://twitter.com/{text}
Reddit: https://reddit.com/u/{text}
TikTok: https://tiktok.com/@{text}
"""
        return reply

    if tool == "domain":
        try:
            ip = socket.gethostbyname(text)
        except:
            ip = "Error"
        reply = f"""
🌍 **Domain Lookup**
Domain: {text}
IP: {ip}
"""
        return reply

# ------------------------------------------------ #

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

# Callback JOIN button + OSINT buttons
async def callback_handler(update, context):
    q = update.callback_query
    user = q.from_user.id
    data = q.data

    await q.answer()

    # OSINT CALLBACKS
    if data.startswith("osint_"):
        tool = data.replace("osint_", "")

        if tool == "back":
            await context.bot.send_message(q.message.chat_id, "OSINT Menu:", reply_markup=osint_menu())
            return

        pending_osint[user] = tool
        await context.bot.send_message(q.message.chat_id, f"🔍 Enter data for **{tool}**:")
        return

    # FORCE JOIN CHECK
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

# MAIN HANDLER
async def main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    uid = update.message.from_user.id

    add_user(uid)

    if not await is_joined_all(uid, context):
        await send_force_join(update, context)
        return

    # OSINT input handler
    if uid in pending_osint:
        tool = pending_osint.pop(uid)
        result = await osint_input_handler(update, context, tool)
        await update.message.reply_text(result, parse_mode="Markdown")
        return

    # Commands
    if msg.startswith("/start"):
        await update.message.reply_text(STATUS_MSG, parse_mode="Markdown")
        return

    if msg.startswith("/help"):
        await update.message.reply_text(HELP_MSG, parse_mode="Markdown")
        return

    if msg.startswith("/about"):
        await update.message.reply_text(ABOUT_MSG, parse_mode="Markdown")
        return

    if msg.startswith("/osint"):
        await update.message.reply_text("🛰️ **OSINT Tools Menu**", reply_markup=osint_menu(), parse_mode="Markdown")
        return

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

    # AI reply
    await update.message.reply_text("💬 Working on it...")
    reply = await ai_response(msg)
    await update.message.reply_text(reply)

# RUN BOT
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(filters.TEXT, main_handler))
app.run_polling()


