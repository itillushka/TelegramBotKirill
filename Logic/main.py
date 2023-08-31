import gspread
import telebot
from oauth2client.service_account import ServiceAccountCredentials

import handlers

TOKEN = '6633230318:AAEPmoWn2SgZsenyflbzZEP2hJ_Fgg6-diM'
bot = telebot.TeleBot(TOKEN)
# Путь к файлу JSON с учетными данными для доступа к Google Таблицам
JSON_PATH = "../credentials.json"

# Создаем объект для работы с Google Таблицами
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, scope)
client = gspread.authorize(creds)

# ID Google Таблицы (взять из URL)
SPREADSHEET_ID_USER_DATA = '1Ru0mMLA8L6GyTPjvrFXIZ-dGN6u_CaHVsZiHVJo9R6w'
SPREADSHEET_ID_CARGO_DATA = '1Eph_4O0fJzbAITj98-1aigGct9YPyizM7WZ7dCDC-Pw'
SPREADSHEET_ID_BROKER_DATA = '11kHyKE8x1xfMzojRvofHKZkUoK7NIHNhetwhWPlhrV8'
SPREADSHEET_ID_CARGO_HISTORY_DATA = '13ljzO69p1gdKyd7p9QbigiPT_L06R5Qf2GLgBsoGCKI'


# Обработчик команды /start
@bot.message_handler(commands=['start', 'menu'])
def start(message):
    handlers.start(message, bot)


@bot.callback_query_handler(func=lambda call: call.data == "broker")
def handle_broker_role(call):
    handlers.handle_broker_role(call, bot)


@bot.callback_query_handler(func=lambda call: call.data == "driver")
def handle_driver_role(call):
    handlers.handle_driver_role(call, bot)


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


@bot.callback_query_handler(func=lambda call: call.data == "cargo")
def handle_cargo(call):
    handlers.handle_cargo(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith("history_"))
def handle_history_details(call):
    handlers.handle_history_details(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith("recent_history"))
def handle_recent_cargos(call):
    handlers.handle_recent_cargos(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith("unpaid_history"))
def handle_unpaid_cargos(call):
    handlers.handle_unpaid_cargos(call, bot)


try:
    bot.polling()
except gspread.exceptions.APIError:
    print("Отсутствие доступа к таблицам")
