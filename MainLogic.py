import os
import pandas as pd
import telebot
from telebot import types

TOKEN = "6633230318:AAEPmoWn2SgZsenyflbzZEP2hJ_Fgg6-diM"
DATA_FILE = "Data/user_data.xlsx"
BROKER_PASSWORD = "1234"
AUTHORIZED_BROKERS = set()

bot = telebot.TeleBot(TOKEN)

DRIVER_QUESTIONS = [
    "Ваше полное имя?",
    "Ваш возраст?",
    "Какая у вас машина?",
    "Из какого вы города?",
    "На какую дистанцию готовы ездить? (в километрах)"
]


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons = [types.KeyboardButton(text="Брокер"), types.KeyboardButton(text="Водитель")]
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, "Привет! Выберите вашу роль:", reply_markup=keyboard)
    bot.register_next_step_handler(message, select_role)


def select_role(message):
    user_id = message.from_user.id
    role = message.text.lower()

    if role == "брокер":
        bot.send_message(user_id, "Введите пароль для доступа к роли 'брокер':")
        bot.register_next_step_handler(message, verify_password)
    elif role == "водитель":
        bot.send_message(user_id, DRIVER_QUESTIONS[0])
        bot.register_next_step_handler(message, driver_details)
    else:
        keyboard = types.ReplyKeyboardRemove()
        bot.send_message(user_id, "Пожалуйста, выберите 'Брокер' или 'Водитель'.", reply_markup=keyboard)


def driver_details(message):
    user_id = message.from_user.id
    current_question_index = message.chat.id

    if not hasattr(bot, 'user_data'):
        bot.user_data = {}
    if "driver_question_index" not in bot.user_data:
        bot.user_data["driver_question_index"] = 0
    if "question_data" not in bot.user_data:
        bot.user_data["question_data"] = {}

    bot.user_data["question_data"][current_question_index + 1] = message.text

    if current_question_index + 1 < len(DRIVER_QUESTIONS):
        next_question = DRIVER_QUESTIONS[current_question_index + 1]
        bot.user_data["driver_question_index"] = current_question_index + 1
        bot.send_message(user_id, next_question)
        bot.register_next_step_handler(message, driver_details)
    else:
        save_driver_info(user_id, bot.user_data)
        bot.send_message(user_id, "Информация сохранена. Спасибо!")
        bot.user_data = {}


def save_broker_info(user_id, cargo):
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["User ID", "Role", "Cargo", "Car"])
    else:
        df = pd.read_excel(DATA_FILE)

    new_row = pd.DataFrame({"User ID": [user_id], "Role": ["Брокер"], "Cargo": [cargo], "Car": [""]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)

    bot.send_message(user_id, "Информация сохранена. Спасибо!")


def save_driver_info(user_id, user_data):
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["User ID"] + [f"Question {i + 1}" for i in range(len(DRIVER_QUESTIONS))])
    else:
        df = pd.read_excel(DATA_FILE)

    new_row = {"User ID": user_id}
    for i, question in enumerate(DRIVER_QUESTIONS):
        new_row[f"Question {i + 1}"] = user_data["question_data"].get(i + 1, "")

    new_row_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_row_df], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)


def verify_password(message):
    user_id = message.from_user.id
    password = message.text.strip()
    if password == BROKER_PASSWORD:
        bot.user_data["authorized_broker"] = True
        bot.send_message(user_id, "Пароль верен. Теперь введите ваш груз:")
        bot.register_next_step_handler(message, add_cargo)
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        buttons = [types.KeyboardButton(text="Брокер"), types.KeyboardButton(text="Водитель")]
        keyboard.add(*buttons)
        bot.send_message(user_id, "Неверный пароль. Выберите 'Брокер' или 'Водитель'.", reply_markup=keyboard)


def add_cargo(message):
    user_id = message.from_user.id
    cargo = message.text
    role = bot.user_data.get("role")

    if role == "брокер":
        if bot.user_data.get("authorized_broker"):
            save_broker_info(user_id, cargo)
            bot.user_data = {}
        else:
            bot.send_message(user_id, "Введите пароль для доступа к роли 'брокер':")
            bot.register_next_step_handler(message, verify_password)
    else:
        keyboard = types.ReplyKeyboardRemove()
        bot.send_message(user_id, "Пожалуйста, выберите 'Брокер' или 'Водитель'.", reply_markup=keyboard)


if __name__ == "__main__":
    bot.polling(none_stop=True)
