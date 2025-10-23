# -*- coding: utf-8 -*-
import os
import json
import hashlib
import hmac
from urllib.parse import parse_qs
from flask import Flask, jsonify, request
from flask_cors import CORS
import telebot
import random
import time

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # временно *, потом укажи свой домен

# --- Telegram Bot Token из переменных окружения ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set.")

bot = telebot.TeleBot(BOT_TOKEN)

# --- Временная база данных пользователей ---
users_db = {}

# --- Вспомогательные функции для проверки initData ---
def _check_webapp_signature(init_data: str, bot_token: str) -> bool:
    parsed_data = parse_qs(init_data)
    hash_value = parsed_data.pop('hash', [None])[0]
    if not hash_value:
        return False

    data_check_string_parts = []
    for key in sorted(parsed_data.keys()):
        data_check_string_parts.append(f"{key}={parsed_data[key][0]}")
    data_check_string = "\n".join(data_check_string_parts)

    secret_key = hmac.new(
        key="WebAppData".encode(),
        msg=bot_token.encode(),
        digestmod=hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    return calculated_hash == hash_value

def get_user_from_init_data(init_data: str, bot_token: str):
    if not _check_webapp_signature(init_data, bot_token):
        return None
    parsed_data = parse_qs(init_data)
    user_data_str = parsed_data.get('user', [None])[0]
    if not user_data_str:
        return None
    return json.loads(user_data_str)

# --- Webhook для Telegram ---
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '!', 200
    return 'Content-Type Error', 403

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.set_webhook(url=f"https://{request.host}/{BOT_TOKEN}")
    return "Вебхук установлен!" if s else "Ошибка установки вебхука."

# --- /start для бота ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    webapp_info = telebot.types.WebAppInfo(f"https://{request.host}/index.html")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text="🎁 Играть в GiftUp!", web_app=webapp_info))
    bot.send_message(message.chat.id, "Привет! Нажми кнопку, чтобы начать играть в GiftUp! Casino.", reply_markup=keyboard)

# --- API для Mini App ---

@app.route("/api/get_user_data", methods=['GET'])
def get_user_data():
    init_data = request.args.get('initData')
    user_info = get_user_from_init_data(init_data, BOT_TOKEN)
    if not user_info:
        return jsonify({"success": False, "message": "Неверные данные пользователя."}), 403

    user_id = user_info['id']
    if user_id not in users_db:
        users_db[user_id] = {'balance': 500.0, 'name': user_info.get('first_name', 'Игрок'),
                             'photo_url': user_info.get('photo_url', ''), 'inventory': [], 'last_crash_bet': 0}

    u = users_db[user_id]
    return jsonify({
        "success": True,
        "user_id": user_id,
        "user_name": u['name'],
        "user_avatar_url": u['photo_url'],
        "balance": u['balance'],
        "inventory_count": len(u['inventory'])
    })

@app.route("/api/generate_crash", methods=['POST'])
def generate_crash():
    data = request.json
    init_data = data.get('initData')
    user_info = get_user_from_init_data(init_data, BOT_TOKEN)
    if not user_info:
        return jsonify({"success": False, "message": "Неверные данные пользователя."}), 403

    user_id = user_info['id']
    bet = float(data.get('bet', 0))
    if user_id not in users_db or users_db[user_id]['balance'] < bet or bet <= 0:
        return jsonify({"success": False, "message": "Недостаточно средств или некорректная ставка."}), 400

    users_db[user_id]['balance'] -= bet
    users_db[user_id]['last_crash_bet'] = bet

    crash_point = round(max(1.01, -1 / (random.random() - 1.01)), 2)

    return jsonify({
        "success": True,
        "crash_point": crash_point,
        "new_balance": users_db[user_id]['balance']
    })

@app.route("/api/cashout_crash", methods=['POST'])
def cashout_crash():
    data = request.json
    init_data = data.get('initData')
    user_info = get_user_from_init_data(init_data, BOT_TOKEN)
    if not user_info:
        return jsonify({"success": False, "message": "Неверные данные пользователя."}), 403

    user_id = user_info['id']
    multiplier = float(data.get('cashout_multiplier', 1.0))
    if user_id not in users_db:
        return jsonify({"success": False, "message": "Пользователь не найден."}), 400

    bet = users_db[user_id]['last_crash_bet']
    if bet == 0:
        return jsonify({"success": False, "message": "Нет активной ставки для вывода."}), 400

    win_amount = bet * multiplier
    users_db[user_id]['balance'] += win_amount
    users_db[user_id]['last_crash_bet'] = 0

    return jsonify({
        "success": True,
        "new_balance": users_db[user_id]['balance'],
        "won_amount": win_amount
    })

# --- Заглушки для депозитов и кейсов ---
@app.route("/api/deposit/<method>", methods=['POST'])
def deposit_stub(method):
    return jsonify({"success": True, "message": f"{method}: В разработке."})

@app.route("/api/open_case", methods=['POST'])
def open_case():
    return jsonify({"success": True, "message": "Открытие кейсов: В разработке."})

@app.route("/api/sell_inventory", methods=['POST'])
def sell_inventory():
    return jsonify({"success": True, "message": "Продажа инвентаря: В разработке."})

# --- Локальный запуск ---
if __name__ == "__main__":
    print("Запуск локального сервера Flask...")
    app.run(host="0.0.0.0", port=5000, debug=True)
