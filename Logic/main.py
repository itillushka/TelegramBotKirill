import gspread
import telebot
from oauth2client.service_account import ServiceAccountCredentials

import handlers

TOKEN = '6633230318:AAEPmoWn2SgZsenyflbzZEP2hJ_Fgg6-diM'
bot = telebot.TeleBot(TOKEN)
# Путь к файлу JSON с учетными данными для доступа к Google Таблицам
JSON_PATH = "Logic/credentials.json"

# Создаем объект для работы с Google Таблицами
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, scope)
client = gspread.authorize(creds)


# Обработчик команды /start
@bot.message_handler(commands=['start', 'menu'])
def start(message):
    handlers.start(message, bot)


@bot.callback_query_handler(func=lambda call: call.data in ["back"])
def back(call):
    chat_id_to_delete = call.message.chat.id
    message_id_to_delete = call.message.message_id

    # Удалите предыдущее сообщение
    bot.delete_message(chat_id_to_delete, message_id_to_delete)

    # Затем вызовите другой метод
    handlers.handle_driver_role(call, bot)



@bot.message_handler(commands=['broker1111'])
def broker(message):
    handlers.broker(message, bot)


@bot.message_handler(func=lambda message: message.text == "Диспетчерам")
def handle_broker_role(call):
    handlers.handle_broker_role(call, bot)


@bot.message_handler(func=lambda message: message.text == "Перевозчикам")
def handle_driver_role(call):
    handlers.handle_driver_role(call, bot)


@bot.message_handler(func=lambda message: message.text == "Сообщество")
def handle_community_button(message):
    handlers.handle_community(message, bot)


@bot.callback_query_handler(func=lambda call: call.data in ["start_driver"])
def start_driver(call):
    handlers.start_driver(call, bot)


@bot.callback_query_handler(func=lambda call: call.data in ["my_data", "view_cargo", "view_broker"])
def handle_driver_choice(call):
    handlers.handle_driver_choice(call, bot)


@bot.callback_query_handler(func=lambda call: call.data in ["view_history"])
def handle_history(call):
    handlers.handle_history(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cargo_"))
def handle_cargo_choice(call):
    handlers.handle_cargo_choice(call, bot)


@bot.callback_query_handler(func=lambda call: call.data == "finish")
def handle_finish(call):
    handlers.handle_finish(call, bot)


@bot.message_handler(func=lambda message: message.text == "Отправить груз")
def handle_cargo(message):
    handlers.handle_cargo(message, bot)


@bot.callback_query_handler(func=lambda call: call.data == "next_cargo")
def handle_cargo_questions(call):
    handlers.handle_cargo_questions(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith("history_"))
def handle_history_details(call):
    handlers.handle_history_details(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith("recent_history"))
def handle_recent_cargos(call):
    handlers.handle_recent_cargos(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith("unpaid_history"))
def handle_unpaid_cargos(call):
    handlers.handle_unpaid_cargos(call, bot)


@bot.callback_query_handler(func=lambda call: call.data == "update_notifications")
def update_notifications(call):
    handlers.handle_update_notifications(call, bot)


@bot.callback_query_handler(func=lambda call: call.data == "edit_data")
def update_notifications(call):
    handlers.handle_edit_data(call, bot)


try:
    bot.polling()
except gspread.exceptions.APIError:
    print("Отсутствие доступа к таблицам")
