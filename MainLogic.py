import telebot
import openpyxl
from telebot import types

TOKEN = '6633230318:AAEPmoWn2SgZsenyflbzZEP2hJ_Fgg6-diM'
broker_password = "1234"
bot = telebot.TeleBot(TOKEN)
DATA = "Data/user_data.xlsx"
CARGO = "Data/cargo_data.xlsx"

# Словарь для хранения данных о пользователях
user_data = {}
waiting_for_password = {}
chosen_cargo = {}


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
@bot.message_handler(commands=['start', 'menu'])
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
    markup = types.InlineKeyboardMarkup(row_width=1)

    if is_user_registered(user_id):

        my_data_button = types.InlineKeyboardButton("Мои данные", callback_data="my_data")
        view_cargo_button = types.InlineKeyboardButton("Посмотреть грузы", callback_data="view_cargo")
        markup.add(my_data_button, view_cargo_button)

        bot.send_message(user_id, "Добро пожаловать в меню водителя", reply_markup=markup)
        return

    if role == "broker":
        user_data[user_id] = {"role": "Брокер"}
        waiting_for_password[user_id] = True
        bot.send_message(user_id, "Введите пароль для доступа к роли брокера:")
    elif role == "driver":
        start_button = types.InlineKeyboardButton("[🟢 Начать ]", callback_data="start_driver")
        markup.add(start_button)
        bot.send_message(user_id,"Добро пожаловать в панель новых водителей!",reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["start_driver"])
def start_driver(call):
    user_id = call.from_user.id
    status = call.data
    if status == "start_driver":
        user_data[user_id] = {"role": "Водитель"}
        bot.send_message(user_id, "Отлично! Пожалуйста, ответьте на несколько вопросов.")
        bot.send_message(user_id, "Ваше полное имя?")
        bot.register_next_step_handler(call.message, ask_age)

@bot.callback_query_handler(func=lambda call: call.data in ["my_data", "view_cargo"])
def handle_driver_choice(call):
    user_id = call.from_user.id
    choice = call.data

    if choice == "my_data":
        bot.send_message(user_id, "Данные")
    elif choice == "view_cargo":
        cargo_workbook = openpyxl.load_workbook(CARGO)
        cargo_sheet = cargo_workbook.active

        cargo_buttons = []
        for row in cargo_sheet.iter_rows(min_row=2, values_only=True):
            from_location = row[0]
            to_location = row[1]
            distance = row[2]
            weight = row[3]
            payment = row[4]

            cargo_info = f"Откуда: {from_location}\nКуда: {to_location}\nДистанция: {distance} км\n" \
                         f"Вес: {weight} кг\nОплата: {payment}"

            cargo_buttons.append(types.InlineKeyboardButton(f"Груз: {from_location} -> {to_location}",
                                                            callback_data=f"cargo_{from_location}_{to_location}"))

        # Добавляем кнопку "Готово" в конце списка грузов
        finish_button = types.InlineKeyboardButton("Готово✅", callback_data="finish")
        cargo_buttons.append(finish_button)

        cargo_buttons_markup = types.InlineKeyboardMarkup(row_width=1)
        cargo_buttons_markup.add(*cargo_buttons)

        bot.send_message(user_id, "Выберите груз:", reply_markup=cargo_buttons_markup)



@bot.callback_query_handler(func=lambda call: call.data.startswith("cargo_"))
def handle_cargo_choice(call):
    user_id = call.from_user.id
    cargo_data = call.data.split("_")[1:]  # Разделяем данные о грузе из callback_data
    cargo_key = "_".join(cargo_data)  # Создаем уникальный ключ для груза

    if user_id not in chosen_cargo:
        chosen_cargo[user_id] = []

    if cargo_key == "finish":
        # Если выбрана кнопка "Готово", обрабатываем завершение выбора грузов
        if user_id in chosen_cargo and chosen_cargo[user_id]:
            chosen_cargo_rows = chosen_cargo[user_id]

            # Добавление номеров строк выбранных грузов в столбец "Груз и номер груза"
            for cargo_row in chosen_cargo_rows:
                add_chosen_cargo(user_id, cargo_row)

            chosen_cargo[user_id] = []  # Очищаем список выбранных грузов
            bot.send_message(user_id, "Спасибо за выбор! Мы с вами свяжемся.")
        else:
            bot.send_message(user_id, "Вы еще не выбрали грузы.")
    else:
        # Иначе, добавляем выбранный груз
        chosen_cargo[user_id].append(cargo_key)
        bot.answer_callback_query(call.id, text="Груз добавлен в выбранные!")



@bot.callback_query_handler(func=lambda call: call.data == "finish")
def handle_finish(call):
    user_id = call.from_user.id
    if user_id in chosen_cargo and chosen_cargo[user_id]:
        chosen_cargo_rows = chosen_cargo[user_id]

        # Добавление номеров строк выбранных грузов в столбец "Груз и номер груза"
        for cargo_row in chosen_cargo_rows:
            add_chosen_cargo(user_id, cargo_row)

        chosen_cargo[user_id] = []  # Очищаем список выбранных грузов
        bot.send_message(user_id, "Спасибо за выбор! Мы с вами свяжемся.")
    else:
        bot.send_message(user_id, "Вы еще не выбрали грузы.")

def add_chosen_cargo(user_id, cargo_row):
    workbook = openpyxl.load_workbook(DATA)
    sheet = workbook.active

    # Найдем строку, где user_id совпадает
    for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        if row[0] == user_id:
            user_row = idx  # Индекс строки, где нашли совпадение

            # Получим номер последнего заполненного столбца в текущей строке
            last_column = sheet.max_column

            # Запишем груз в следующий столбец
            sheet.cell(row=user_row, column=last_column + 1, value=cargo_row)
            break  # Прерываем цикл, так как нашли нужную строку

    workbook.save(DATA)
    workbook.close()


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
