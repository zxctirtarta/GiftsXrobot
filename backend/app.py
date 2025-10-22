from flask import Flask, request, jsonify
import telebot
import random
import json

app = Flask(__name__)

# ✅ Т Т Т (уже готов!)
BOT_TOKEN = '8376293649:AAEfNUQNIrPKS37B1cM5pbvyuuzIUvV1F0Y'
bot = telebot.TeleBot(BOT_TOKEN)

# бнови этот URL после деплоя mini-app!
MINI_APP_URL = 'https://giftsxrobot-mini.vercel.app'

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Error', 403

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = request.url_root + 'webhook'
    bot.remove_webhook()
    bot.set_webhook(webhook_url)
    return '✅ ебхук установлен!'

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(
        text='🎰 грать в Crash Gifts', 
        web_app=telebot.types.WebAppInfo(url=MINI_APP_URL)
    )
    markup.add(button)
    bot.send_message(
        message.chat.id, 
        '🎉 обро пожаловать в Crash Gifts Casino!\n'
        '💎 грай в Crash и выигрывай TON!\n\n'
        'ажми кнопку ниже и начинай 🚀',
        reply_markup=markup
    )

@app.route('/api/generate_crash', methods=['GET'])
def generate_crash():
    r = random.random()
    if r < 0.01:        # 1% шанс
        crash = random.uniform(50, 100)
    elif r < 0.05:      # 4% шанс
        crash = random.uniform(10, 50)
    elif r < 0.2:       # 15% шанс
        crash = random.uniform(5, 10)
    elif r < 0.5:       # 30% шанс
        crash = random.uniform(2, 5)
    else:               # 50% шанс
        crash = random.uniform(1.01, 2)
    return jsonify({'crash_point': round(crash, 2)})

@app.route('/')
def index():
    return '🚀 GiftsXrobot Casino Bot работает!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
