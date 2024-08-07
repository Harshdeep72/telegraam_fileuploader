import telebot
import os
from mega import Mega
from flask import Flask, request

# Use the token obtained from BotFather
TELEGRAM_BOT_TOKEN = os.environ['7298924629:AAGLM1sKKeDpsJXBfwGKW-ZW7PFNzkP6yAE']

# MEGA account credentials
MEGA_EMAIL = os.environ['MEGA_EMAIL']
MEGA_PASSWORD = os.environ['MEGA_PASSWORD']

# Initialize the Telegram bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Initialize MEGA instance and login
mega = Mega()
m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)

# Define the file path to save the files temporarily
TEMP_DOWNLOAD_PATH = 'downloads'

if not os.path.exists(TEMP_DOWNLOAD_PATH):
    os.makedirs(TEMP_DOWNLOAD_PATH)

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_name = message.document.file_name
        file_path = os.path.join(TEMP_DOWNLOAD_PATH, file_name)

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Upload to MEGA
        m.upload(file_path)
        bot.reply_to(message, "File has been uploaded to your MEGA account!")

        # Remove the file after upload
        os.remove(file_path)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Forward any file to me and I will upload it to your MEGA account.")

app = Flask(__name__)

@app.route('/' + TELEGRAM_BOT_TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://telegraam-fileuploader.vercel.app/' + TELEGRAM_BOT_TOKEN)
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
