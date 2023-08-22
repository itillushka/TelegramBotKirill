import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials

TOKEN = '6633230318:AAEPmoWn2SgZsenyflbzZEP2hJ_Fgg6-diM'
broker_password = "1234"
bot = telebot.TeleBot(TOKEN)
# Путь к файлу JSON с учетными данными для доступа к Google Таблицам
JSON_PATH = 'credentials.json'

# Создаем объект для работы с Google Таблицами
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, scope)
client = gspread.authorize(creds)

# ID Google Таблицы (взять из URL)
SPREADSHEET_ID_USER_DATA = '1Ru0mMLA8L6GyTPjvrFXIZ-dGN6u_CaHVsZiHVJo9R6w'
SPREADSHEET_ID_CARGO_DATA = '1Eph_4O0fJzbAITj98-1aigGct9YPyizM7WZ7dCDC-Pw'

# Словари для хранения данных о пользователях
user_data = {}
waiting_for_password = {}
chosen_cargo = {}
driver_data = {}


def is_user_registered(user_id):
    sheet = client.open_by_key(SPREADSHEET_ID_USER_DATA).get_worksheet(0)
    user_ids = sheet.col_values(1)[1:]

    if str(user_id) in user_ids:
        user_row = user_ids.index(str(user_id)) + 2  # Индекс строки с user_id, учитывая заголовок в первой строке
        user_role = sheet.cell(user_row, 2).value  # Значение ячейки с ролью пользователя
        return True, user_role
    else:
        return False, None


def get_user_data(user_id):
    sheet = client.open_by_key(SPREADSHEET_ID_USER_DATA).get_worksheet(0)
    user_cell = sheet.find(str(user_id))
    if user_cell:
        user_row = user_cell.row
        user_data_row = sheet.row_values(user_row)
        user_data = {
            "role": user_data_row[1],
            "name": user_data_row[2],
            "phone": user_data_row[3],
            "car_plate": user_data_row[4],
            "cargo_capacity": user_data_row[5],
            "dimensions": user_data_row[6],
            "body_type": user_data_row[7],
            "city": user_data_row[8],
            "distance": user_data_row[9],
            "ip_or_self_employed": user_data_row[10],
            "rent_or_own_car": user_data_row[11],
            "cargo_loading_type": user_data_row[12]
        }
        return user_data
    else:
        return {}


# Обработчик команды /start
@bot.message_handler(commands=['start', 'menu'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    broker_button = types.InlineKeyboardButton(" 🚚 Перевозчикам", callback_data="driver")
    driver_button = types.InlineKeyboardButton(" 📞 Диспетчерам", callback_data="broker")
    cargo_button = types.InlineKeyboardButton(" 📦 Отправить груз", callback_data="cargo")
    markup.add(broker_button, driver_button, cargo_button)
    bot.send_message(message.chat.id, "Приветствую в нашем боте! Пожалуйста выберите раздел:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "broker")
def handle_broker_role(call):
    user_id = call.from_user.id
    bot.send_message(user_id,
                     "Спасибо, что хотите пополнить нашу команду диспетчеров!\nПрошу вас заполнить Гугл форму, чтобы мы узнали о вас побольше!")

    # Создаем кнопку для перенаправления на сайт Google
    markup = types.InlineKeyboardMarkup(row_width=1)
    google_button = types.InlineKeyboardButton("Перейти к Гугл форме", url="https://www.google.com")
    markup.add(google_button)

    # Отправляем сообщение с кнопкой
    bot.send_message(user_id, "Для заполнения формы, перейдите по ссылке ниже:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "driver")
def handle_driver_role(call):
    user_id = call.from_user.id
    registered, user_role = is_user_registered(user_id)

    if registered and user_role == "Водитель":
        markup = types.InlineKeyboardMarkup(row_width=1)
        my_data_button = types.InlineKeyboardButton("Мои данные", callback_data="my_data")
        view_cargo_button = types.InlineKeyboardButton("Посмотреть грузы", callback_data="view_cargo")
        markup.add(my_data_button, view_cargo_button)
        bot.send_message(user_id, "Добро пожаловать в меню водителя", reply_markup=markup)
    elif registered and user_role == "Брокер":
        bot.send_message(user_id, "Вы не имеете доступа к роли Перевозчика.")
    elif not registered:
        start_button = types.InlineKeyboardButton("[🟢 Начать ]", callback_data="start_driver")
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(start_button)
        bot.send_message(user_id, "Добро пожаловать в панель новых водителей!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["start_driver"])
def start_driver(call):
    user_id = call.from_user.id
    status = call.data
    if status == "start_driver":
        user_data[user_id] = {"role": "Водитель"}
        driver_data[user_id] = {}  # Создаем пустой словарь для данных водителя
        bot.send_message(user_id, "Отлично! Пожалуйста, ответьте на несколько вопросов.")
        bot.send_message(user_id, "Ваше полное имя?")
        bot.register_next_step_handler(call.message, ask_phone)


@bot.callback_query_handler(func=lambda call: call.data in ["my_data", "view_cargo"])
def handle_driver_choice(call):
    user_id = call.from_user.id
    choice = call.data

    if choice == "my_data":
        user_data = get_user_data(user_id)

        if user_data:
            response = "👤 Ваши данные:\n"
            for key, value in user_data.items():
                response += f"✅ {key.capitalize()}: {value}\n"
            bot.send_message(user_id, response)
        else:
            bot.send_message(user_id, "🚫 Ваши данные не найдены.")
    elif choice == "view_cargo":
        sheet = client.open_by_key(SPREADSHEET_ID_CARGO_DATA).get_worksheet(0)  # Открываем первый лист

        cargo_buttons = []
        cargo_data = sheet.get_all_values()[1:]  # Пропускаем заголовок

        for row in cargo_data:
            cargo_id = row[0]
            from_location = row[1]
            to_location = row[2]
            cargo_buttons.append(types.InlineKeyboardButton(f"Груз: {from_location} -> {to_location}",
                                                            callback_data=f"cargo_{cargo_id}"))

        # Добавляем кнопку "Готово" в конце списка грузов
        finish_button = types.InlineKeyboardButton("Готово✅", callback_data="finish")
        cargo_buttons.append(finish_button)

        cargo_buttons_markup = types.InlineKeyboardMarkup(row_width=1)
        cargo_buttons_markup.add(*cargo_buttons)

        bot.send_message(user_id, "Выберите груз:", reply_markup=cargo_buttons_markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cargo_"))
def handle_cargo_choice(call):
    user_id = call.from_user.id
    cargo_id = call.data.split("_")[1]  # Получаем идентификатор груза из callback_data

    if user_id not in chosen_cargo:
        chosen_cargo[user_id] = []

    if cargo_id == "finish":
        # Если выбрана кнопка "Готово", обрабатываем завершение выбора грузов
        if user_id in chosen_cargo and chosen_cargo[user_id]:
            chosen_cargo_rows = chosen_cargo[user_id]

            # Добавление номеров строк выбранных грузов в столбец "Груз и номер груза"
            for cargo_row in chosen_cargo_rows:
                add_chosen_cargo(user_id, cargo_row)

            chosen_cargo[user_id] = []  # Очищаем список выбранных грузов
            bot.send_message(user_id, "Спасибо за выбор! Мы с вами свяжемся. 🚚")
        else:
            bot.send_message(user_id, "Вы еще не выбрали грузы. 🚫")
    else:
        # Иначе, добавляем выбранный груз
        chosen_cargo[user_id].append(cargo_id)
        bot.answer_callback_query(call.id, text="Груз добавлен в выбранные! ✅")


@bot.callback_query_handler(func=lambda call: call.data == "finish")
def handle_finish(call):
    user_id = call.from_user.id
    if user_id in chosen_cargo and chosen_cargo[user_id]:
        chosen_cargo_ids = chosen_cargo[user_id]  # Получаем идентификаторы грузов

        # Добавление идентификаторов выбранных грузов в столбец "Груз и номер груза"
        for cargo_id in chosen_cargo_ids:
            add_chosen_cargo(user_id, cargo_id)

        chosen_cargo[user_id] = []  # Очищаем список выбранных грузов
        bot.send_message(user_id, "Спасибо за выбор! Мы с вами свяжемся. 🚚")
    else:
        bot.send_message(user_id, "Вы еще не выбрали грузы. 🚫")



def add_chosen_cargo(user_id, cargo_id):
    sheet = client.open_by_key(SPREADSHEET_ID_USER_DATA).get_worksheet(0)

    # Найдем строку, где user_id совпадает
    for idx, row in enumerate(sheet.get_all_values(), start=1):
        if row[0] == str(user_id):
            user_row = idx  # Индекс строки, где нашли совпадение

            # Получаем номер последнего столбца выбранных грузов
            last_cargo_column = len(row)

            # Добавляем идентификатор груза в следующий столбец
            print(cargo_id)
            sheet.update_cell(user_row, last_cargo_column + 1, cargo_id)
            break  # Прерываем цикл, так как нашли нужную строку


def ask_phone(message):
    user_id = message.from_user.id
    driver_data[user_id]["name"] = message.text

    bot.send_message(message.chat.id, "Ваш телефон?")
    bot.register_next_step_handler(message, ask_car_number)


def ask_car_number(message):
    user_id = message.from_user.id
    driver_data[user_id]["phone"] = message.text

    bot.send_message(message.chat.id, "Государственный знак машины?")
    bot.register_next_step_handler(message, ask_cargo_capacity)


def ask_cargo_capacity(message):
    user_id = message.from_user.id
    driver_data[user_id]["car_number"] = message.text

    bot.send_message(message.chat.id, "Грузоподъемность машины?")
    bot.register_next_step_handler(message, ask_dimensions)


def ask_dimensions(message):
    user_id = message.from_user.id
    driver_data[user_id]["cargo_capacity"] = message.text

    bot.send_message(message.chat.id, "Длина/Ширина/Высота машины?")
    bot.register_next_step_handler(message, ask_body_type)


def ask_body_type(message):
    user_id = message.from_user.id
    driver_data[user_id]["dimensions"] = message.text

    bot.send_message(message.chat.id, "Тип кузова?")
    bot.register_next_step_handler(message, ask_residence_city)


def ask_residence_city(message):
    user_id = message.from_user.id
    driver_data[user_id]["body_type"] = message.text

    bot.send_message(message.chat.id, "Город проживания?")
    bot.register_next_step_handler(message, ask_distance_to_travel)


def ask_distance_to_travel(message):
    user_id = message.from_user.id
    driver_data[user_id]["residence_city"] = message.text

    bot.send_message(message.chat.id, "Дистанция, на которую готовы ездить? (в километрах)")
    bot.register_next_step_handler(message, ask_employment_type)


def ask_employment_type(message):
    user_id = message.from_user.id
    driver_data[user_id]["distance_to_travel"] = message.text

    bot.send_message(message.chat.id, "Вы являетесь ИП или самозанятым?")
    bot.register_next_step_handler(message, ask_car_ownership)


def ask_car_ownership(message):
    user_id = message.from_user.id
    driver_data[user_id]["employment_type"] = message.text

    bot.send_message(message.chat.id, "У вас машина в аренде или личная?")
    bot.register_next_step_handler(message, save_driver_info)


def save_driver_info(message):
    user_id = message.from_user.id
    driver_data[user_id]["car_ownership"] = message.text

    bot.send_message(message.chat.id, "Какой у вас тип загрузки? Задний/верхний/боковой?")
    bot.register_next_step_handler(message, ask_cargo_loading_type)


def ask_cargo_loading_type(message):
    user_id = message.from_user.id
    driver_data[user_id]["cargo_loading_type"] = message.text

    add_driver_to_google_sheets(user_id, **driver_data[user_id])  # Добавляем данные о водителе в таблицу
    bot.send_message(user_id, "Спасибо! Ваши данные сохранены.")


def add_driver_to_google_sheets(user_id, **data):
    sheet = client.open_by_key(SPREADSHEET_ID_USER_DATA).get_worksheet(0)  # Открываем первый лист

    driver_info = [
        user_id,
        "Водитель",
        data["name"],
        data["phone"],
        data["car_number"],
        data["cargo_capacity"],
        data["dimensions"],
        data["body_type"],
        data["residence_city"],
        data["distance_to_travel"],
        data["employment_type"],
        data["car_ownership"],
        data["cargo_loading_type"]
    ]

    sheet.append_row(driver_info)


@bot.callback_query_handler(func=lambda call: call.data == "cargo")
def handle_cargo(call):
    user_id = call.from_user.id
    user_data[user_id] = {}
    bot.send_message(user_id, "Введите данные о грузе.\n\n1. Откуда?")

    bot.register_next_step_handler(call.message, ask_cargo_from)


def ask_cargo_from(message):
    user_id = message.from_user.id
    user_data[user_id]["cargo_from"] = message.text
    bot.send_message(user_id, "2. Куда?")
    bot.register_next_step_handler(message, ask_cargo_to)


def ask_cargo_to(message):
    user_id = message.from_user.id
    user_data[user_id]["cargo_to"] = message.text
    bot.send_message(user_id, "3. Дистанция (в километрах)?")
    bot.register_next_step_handler(message, ask_cargo_distance)


def ask_cargo_distance(message):
    user_id = message.from_user.id
    user_data[user_id]["cargo_distance"] = message.text
    bot.send_message(user_id, "4. Вес груза (в кг)?")
    bot.register_next_step_handler(message, ask_cargo_weight)


def ask_cargo_weight(message):
    user_id = message.from_user.id
    user_data[user_id]["cargo_weight"] = message.text
    bot.send_message(user_id, "5. Оплата (в рублях)?")
    bot.register_next_step_handler(message, save_cargo_info)


def save_cargo_info(message):
    user_id = message.from_user.id
    cargo_info = {
        "from_location": user_data[user_id]["cargo_from"],
        "to_location": user_data[user_id]["cargo_to"],
        "distance": user_data[user_id]["cargo_distance"],
        "weight": user_data[user_id]["cargo_weight"],
        "payment": message.text
    }

    add_cargo_to_google_sheets(**cargo_info)
    bot.send_message(user_id, "Спасибо! Данные о грузе сохранены.")


def add_cargo_to_google_sheets(from_location, to_location, distance, weight, payment):
    sheet = client.open_by_key(SPREADSHEET_ID_CARGO_DATA).get_worksheet(0)  # Открываем лист

    # Получаем текущее количество строк в таблице
    num_rows = len(sheet.get_all_values()) + 1

    # Генерируем идентификатор в формате "Xcrg", где X - порядковый номер груза
    cargo_id = f"{num_rows - 1}crg"

    cargo_info = [cargo_id, from_location, to_location, distance, weight, payment]
    sheet.append_row(cargo_info)



bot.polling()
