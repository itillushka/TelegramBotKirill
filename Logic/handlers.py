from telebot import types

import add_data
import dialog
import user_dict
import user_utils


def start(message, bot):
    markup = types.InlineKeyboardMarkup(row_width=1)
    broker_button = types.InlineKeyboardButton(" 🚚 Перевозчикам", callback_data="driver")
    driver_button = types.InlineKeyboardButton(" 📞 Диспетчерам", callback_data="broker")
    cargo_button = types.InlineKeyboardButton(" 📦 Отправить груз", callback_data="cargo")
    community_button = types.InlineKeyboardButton(" 👥 Сообщество", url="https://t.me/+j7plDmEkx9wyN2Iy")
    markup.add(broker_button, driver_button, cargo_button, community_button)
    bot.send_message(message.chat.id, "Приветствую в нашем боте! Пожалуйста выберите раздел:", reply_markup=markup)


def start_driver(call, bot):
    user_id = call.from_user.id
    status = call.data
    if status == "start_driver":
        user_dict.user_data[user_id] = {"role": "Водитель"}
        user_dict.driver_data[user_id] = {}  # Создаем пустой словарь для данных водителя
        bot.send_message(user_id, "Отлично! Пожалуйста, ответьте на несколько вопросов.")
        bot.send_message(user_id, "Ваше полное имя?")
        bot.register_next_step_handler(call.message, dialog.ask_phone, bot)


def handle_broker_role(call, bot):
    user_id = call.from_user.id
    bot.send_message(user_id,
                     "Спасибо, что хотите пополнить нашу команду диспетчеров!\nПрошу вас заполнить Гугл форму, "
                     "чтобы мы узнали о вас побольше!")
    # Создаем кнопку для перенаправления на сайт Google
    markup = types.InlineKeyboardMarkup(row_width=1)
    google_button = types.InlineKeyboardButton("Перейти к Гугл форме", url="https://forms.gle/rDtNM8sN8JRiaJpp6")
    markup.add(google_button)

    # Отправляем сообщение с кнопкой
    bot.send_message(user_id, "Для заполнения формы, перейдите по ссылке ниже:", reply_markup=markup)


def handle_driver_role(call, bot):
    user_id = call.from_user.id
    registered, user_role = user_utils.is_user_registered(user_id)

    if registered and user_role == "Водитель":
        markup = types.InlineKeyboardMarkup(row_width=1)
        my_data_button = types.InlineKeyboardButton("Мои данные", callback_data="my_data")
        view_cargo_button = types.InlineKeyboardButton("Посмотреть грузы", callback_data="view_cargo")
        view_broker_button = types.InlineKeyboardButton("Мой диспетчер", callback_data="view_broker")
        markup.add(my_data_button, view_cargo_button, view_broker_button)
        bot.send_message(user_id, "Добро пожаловать в меню водителя", reply_markup=markup)
    elif registered and user_role == "Брокер":
        bot.send_message(user_id, "Вы не имеете доступа к роли Перевозчика.")
    elif not registered:
        start_button = types.InlineKeyboardButton("[🟢 Начать ]", callback_data="start_driver")
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(start_button)
        bot.send_message(user_id, "Добро пожаловать в панель новых водителей!", reply_markup=markup)


def handle_driver_choice(call, bot):
    user_id = call.from_user.id
    choice = call.data

    if choice == "my_data":
        user_data_get = user_utils.get_displayed_user_data(user_utils.get_user_data(user_id))
        if user_data_get:
            response = "👤 Ваши данные:\n"
            for key, value in user_data_get.items():
                response += f"✅ {key.capitalize()}: {value}\n"
            bot.send_message(user_id, response)
        else:
            bot.send_message(user_id, "🚫 Ваши данные не найдены.")
    elif choice == "view_cargo":
        user_data = user_utils.get_user_data(user_id)
        if user_data and user_data["role"] == "Водитель":
            residence_city = user_data["city"]  # Город проживания водителя
            sheet = user_utils.client.open_by_key(user_utils.SPREADSHEET_ID_CARGO_DATA).get_worksheet(0)

            cargo_buttons = []
            cargo_data = sheet.get_all_values()[1:]  # Пропускаем заголовок

            for row in cargo_data:
                from_location = row[1]
                if from_location == residence_city:
                    cargo_id = row[0]
                    to_location = row[2]
                    cargo_buttons.append(types.InlineKeyboardButton(f"Груз: {from_location} -> {to_location}",
                                                                    callback_data=f"cargo_{cargo_id}"))

            # Добавляем кнопку "Готово" в конце списка грузов
            finish_button = types.InlineKeyboardButton("Готово✅", callback_data="finish")
            cargo_buttons.append(finish_button)

            cargo_buttons_markup = types.InlineKeyboardMarkup(row_width=1)
            cargo_buttons_markup.add(*cargo_buttons)

            bot.send_message(user_id, "Выберите груз:", reply_markup=cargo_buttons_markup)
        else:
            bot.send_message(user_id, "У вас нет доступа к выбору грузов.")
    elif choice == "view_broker":
        bot.send_message(user_id, "Данные диспетчера")


def handle_cargo_choice(call, bot):
    user_id = call.from_user.id
    cargo_id = call.data.split("_")[1]  # Получаем идентификатор груза из callback_data

    if user_id not in user_dict.chosen_cargo:
        user_dict.chosen_cargo[user_id] = []

    if cargo_id == "finish":
        handle_finish(call, bot)
    else:
        # Иначе, добавляем выбранный груз
        user_dict.chosen_cargo[user_id].append(cargo_id)
        bot.answer_callback_query(call.id, text="Груз добавлен в выбранные! ✅")


def handle_finish(call, bot):
    user_id = call.from_user.id
    if user_id in user_dict.chosen_cargo and user_dict.chosen_cargo[user_id]:
        chosen_cargo_ids = user_dict.chosen_cargo[user_id]  # Получаем идентификаторы грузов

        # Добавление идентификаторов выбранных грузов в столбец "Груз и номер груза"
        for cargo_id in chosen_cargo_ids:
            add_data.add_chosen_cargo(user_id, cargo_id)

        user_dict.chosen_cargo[user_id] = []  # Очищаем список выбранных грузов
        bot.send_message(user_id, "Спасибо за выбор! Мы с вами свяжемся. 🚚")
    else:
        bot.send_message(user_id, "Вы еще не выбрали грузы. 🚫")


def handle_cargo(call, bot):
    user_id = call.from_user.id
    user_dict.user_data[user_id] = {}
    bot.send_message(user_id, "Введите данные о грузе.\n\n1. Откуда?")

    bot.register_next_step_handler(call.message, dialog.ask_cargo_from, bot)
