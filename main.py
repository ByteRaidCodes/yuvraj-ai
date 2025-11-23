import os
os.system("pip install openai==1.30.0 python-telegram-bot==20.3")

from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters, CallbackQueryHandler

# Load tokens safely
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=OPENAI_KEY)

# Banner image (PostImages direct link)
PHOTO_PATH = "https://i.postimg.cc/76L59xVj/03cf19b6-e979-4d2f-9d6f-3ba2469e60c2.jpg"

# --- 4 CHANNEL FORCE JOIN SETTINGS ---
CHANNELS = [
    (-1002090323246, "⚡", "https://t.me/CodeTweakz"),
    (-1002145075313, "🔥", "https://t.me/Scripts0x"),
    (-1003279886990, "💎", "https://t.me/techmoros"),
    (-1002733321153, "🚀", "https://t.me/MethRoot"),
]

# Custom caption you provided
CAPTION = """
💀 **Welcome to the Sevr0c–Moros AI ⚡**

Inside this channel, you’ll get access to advanced scripts, ethical hacking tutorials, powerful methods, hidden tricks, important security tools, active lessons, and real techniques used by professionals.

We drop content that actually works — no fake stuff, no useless noise.

If you want practical hacking knowledge, real-world tips, updated methods, and exclusive scripts, this is the right place.

⚠️ **Everything taught here is for ethical & educational purposes only.**

👉 **Join now and unlock the skills others hide.**
"""

# status message for users who already joined
STATUS_MSG = """
💀 Sevr0c–Moros AI Status
━━━━━━━━━━━━━━━━━━
⚡ Bot is LIVE
🟢 No maintenance
🔥 All features working
"""

# -----------------------------------------------
# CHECK IF USER JOINED ALL REQUIRED CHANNELS
# -----------------------------------------------
async def is_joined_all(user_id, context):
    for channel_id, emoji, link in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel_id, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# -----------------------------------------------
# SEND INLINE BUTTON 2×2 GRID FORCE JOIN UI + IMAGE
# -----------------------------------------------
async def send_force_join(update, context):

    keyboard = [
        [
            InlineKeyboardButton(text=f"{CHANNELS[0][1]} Join", url=CHANNELS[0][2]),
            InlineKeyboardButton(text=f"{CHANNELS[1][1]} Join", url=CHANNELS[1][2]),
        ],
        [
            InlineKeyboardButton(text=f"{CHANNELS[2][1]} Join", url=CHANNELS[2][2]),
            InlineKeyboardButton(text=f"{CHANNELS[3][1]} Join", url=CHANNELS[3][2]),
        ],
        [
            InlineKeyboardButton(text="⭕ JOINED ❌", callback_data="check_join")
        ]
    ]

    await update.message.reply_photo(
        photo=PHOTO_PATH,
        caption=CAPTION,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# -----------------------------------------------
# START COMMAND (WELCOME OR STATUS BASED ON JOIN)
# -----------------------------------------------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # If NOT joined => show force join banner
    if not await is_joined_all(user_id, context):
        await send_force_join(update, context)
        return

    # If already joined => show bot status message
    await update.message.reply_text(STATUS_MSG, parse_mode="Markdown")

# -----------------------------------------------
# CALLBACK: WHEN USER PRESSES "JOINED"
# -----------------------------------------------
async def callback_handler(update, context):
    query = update.callback_query
    await query.answer()

    user = query.from_user.id
    joined = await is_joined_all(user, context)

    if not joined:
        await query.answer(
            "❌ You have not joined ALL channels!\nJoin all and tap JOINED again.",
            show_alert=True
        )
        return

    # If joined successfully → change button
    await query.edit_message_reply_markup(
        InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="🟢 JOINED ✔", callback_data="none")]]
        )
    )

    await query.message.reply_text("✅ Verified! You can now use the bot.")

# -----------------------------------------------
# AI FUNCTION
# -----------------------------------------------
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

# -----------------------------------------------
# MAIN MESSAGE HANDLER
# -----------------------------------------------
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    if not await is_joined_all(user_id, context):
        await send_force_join(update, context)
        return

    await update.message.reply_text("💬 Working on it...")

    reply = await ai_response(update.message.text)

    await update.message.reply_text(reply)

# -----------------------------------------------
# RUN BOT
# -----------------------------------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start_cmd))
app.add_handler(CallbackQueryHandler(callback_handler, pattern="check_join"))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))

app.run_polling()
