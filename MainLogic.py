import telebot
import openpyxl
from telebot import types

TOKEN = '6633230318:AAEPmoWn2SgZsenyflbzZEP2hJ_Fgg6-diM'
broker_password = "1234"
bot = telebot.TeleBot(TOKEN)
DATA = "Data/user_data.xlsx"

# Словарь для хранения данных о пользователях
user_data = {}
waiting_for_password = {}


def is_user_registered(user_id):
    workbook = openpyxl.load_workbook(DATA)
    sheet = workbook.active
    for row in sheet.iter_rows(min_row=1, values_only=True):
        print(row)
        if row[0] == user_id:
            workbook.close()
            return True
    workbook.close()
    return False
# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    broker_button = types.InlineKeyboardButton("[🚚 Перевозчикам]",callback_data="driver")
    driver_button = types.InlineKeyboardButton("[ 📞 Диспетчерам]",callback_data="broker")
    cargo_button = types.InlineKeyboardButton("[ 📦 Отправить груз]",callback_data="cargo")
    markup.add(broker_button, driver_button, cargo_button)
    bot.send_message(message.chat.id, "Приветствую в нашем боте! Пожалуйста выберите раздел:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["broker", "driver"])
def handle_role_choice(call):
    user_id = call.from_user.id
    role = call.data

    if is_user_registered(user_id):
        bot.send_message(user_id, "У вас уже есть роль.")
        return

    if role == "broker":
        user_data[user_id] = {"role": "Брокер"}
        waiting_for_password[user_id] = True
        bot.send_message(user_id, "Введите пароль для доступа к роли брокера:")
    elif role == "driver":
        user_data[user_id] = {"role": "Водитель"}
        bot.send_message(user_id, "Отлично! Пожалуйста, ответьте на несколько вопросов.")
        bot.send_message(user_id, "Ваше полное имя?")
        bot.register_next_step_handler(call.message, ask_age)

# Обработчик ввода пароля
@bot.message_handler(func=lambda message: waiting_for_password.get(message.from_user.id))
def check_broker_password(message):
    user_id = message.from_user.id
    password = message.text

    if password == broker_password:
        add_to_excel(user_id, **user_data[user_id])
        bot.send_message(user_id, "Пароль верный. Теперь вы брокер.")
        waiting_for_password[user_id] = False

    else:
        bot.send_message(user_id, "Пароль неверный. Попробуйте еще раз или выберите другую роль.")

def ask_age(message):
    user_id = message.from_user.id
    user_data[user_id]["name"] = message.text

    bot.send_message(message.chat.id, "Ваш возраст?")
    bot.register_next_step_handler(message, ask_car)


def ask_car(message):
    user_id = message.from_user.id
    user_data[user_id]["age"] = message.text

    bot.send_message(message.chat.id, "Какая у вас машина?")
    bot.register_next_step_handler(message, ask_city)


def ask_city(message):
    user_id = message.from_user.id
    user_data[user_id]["car"] = message.text

    bot.send_message(message.chat.id, "Из какого вы города?")
    bot.register_next_step_handler(message, ask_distance)


def ask_distance(message):
    user_id = message.from_user.id
    user_data[user_id]["city"] = message.text

    bot.send_message(message.chat.id, "На какую дистанцию готовы ездить? (в километрах)")
    bot.register_next_step_handler(message, save_driver_info)


def save_driver_info(message):
    user_id = message.from_user.id
    user_data[user_id]["distance"] = message.text

    # Добавление информации в Excel таблицу
    add_to_excel(user_id, **user_data[user_id])

    bot.send_message(message.chat.id, "Спасибо! Ваша информация сохранена.")


def add_to_excel(user_id, **data):
    workbook = openpyxl.load_workbook(DATA)
    sheet = workbook.active

    sheet.append([user_id, data.get("role"), data.get("name"), data.get("age"), data.get("car"), data.get("city"),
                  data.get("distance")])
    workbook.save(DATA)
    workbook.close()


bot.polling()
