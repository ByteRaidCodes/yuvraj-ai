import os
os.system("pip install openai==1.30.0 python-telegram-bot==20.3")

from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters, CallbackQueryHandler

# Load tokens safely
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=OPENAI_KEY)

# --- 4 CHANNEL FORCE JOIN SETTINGS ---
CHANNELS = [
    (-1002090323246, "⚡", "https://t.me/CodeTweakz"),
    (-1002145075313, "🔥", "https://t.me/Scripts0x"),
    (-1003279886990, "💎", "https://t.me/techmoros"),
    (-1002733321153, "🚀", "https://t.me/MethRoot"),
]

# -----------------------------------------------
# CHECK IF USER JOINED ALL REQUIRED CHANNELS
# -----------------------------------------------
async def is_joined_all(update, context):
    user_id = update.message.from_user.id

    for channel_id, emoji, link in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel_id, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False

    return True


# -----------------------------------------------
# SEND INLINE BUTTON 2×2 GRID FORCE JOIN UI
# -----------------------------------------------
async def send_force_join(update):

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

    await update.message.reply_text(
        "**📢 Must Join All Channels Before Using The Bot**\n"
        "Please join all channels below and then tap **JOINED**:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# -----------------------------------------------
# CALLBACK: WHEN USER PRESSES "JOINED"
# -----------------------------------------------
async def callback_handler(update, context):
    query = update.callback_query
    await query.answer()

    # user pressed the JOINED button → verify membership
    user = query.from_user.id

    all_joined = True
    for channel_id, emoji, link in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel_id, user)
            if member.status in ["left", "kicked"]:
                all_joined = False
                break
        except:
            all_joined = False
            break

    # If NOT joined → show POPUP alert
    if not all_joined:
        await query.answer(
            "❌ You have not joined ALL channels!\nJoin all and tap JOINED again.",
            show_alert=True
        )
        return

    # If joined successfully → convert to green success button
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

    # 🔒 FORCE JOIN CHECK
    if not await is_joined_all(update, context):
        await send_force_join(update)
        return

    # Typing message
    await update.message.reply_text("💬 Working on it...")

    # Get AI response
    reply = await ai_response(update.message.text)

    # Final send
    await update.message.reply_text(reply)


# -----------------------------------------------
# RUN BOT
# -----------------------------------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CallbackQueryHandler(callback_handler, pattern="check_join"))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))

app.run_polling()
