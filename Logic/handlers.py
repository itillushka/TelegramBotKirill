from telebot import types

import add_data
import dialog
import user_dict
import user_utils


def start(message, bot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    broker_button = types.KeyboardButton("🚚 Перевозчикам")
    driver_button = types.KeyboardButton("📞 Диспетчерам")
    cargo_button = types.KeyboardButton("📦 Отправить груз")
    community_button = types.KeyboardButton("👥 Сообщество")
    markup.add(broker_button, driver_button, cargo_button, community_button)

    with open(user_dict.START_PHOTO, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="Приветствую в нашем боте! Пожалуйста выберите раздел:",
                       reply_markup=markup)


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
        view_history_button = types.InlineKeyboardButton("История заказов", callback_data="view_history")
        markup.add(my_data_button, view_cargo_button, view_broker_button, view_history_button)

        bot.send_message(user_id, "Добро пожаловать в меню водителя!", reply_markup=markup)

    elif registered and user_role == "Брокер":
        bot.send_message(user_id, "Вы не имеете доступа к роли Перевозчика.")
    elif not registered:
        start_button = types.InlineKeyboardButton("🟢 Начать", callback_data="start_driver")
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(start_button)
        with open(user_dict.REGISTRATION_PHOTO, 'rb') as photo:
            bot.send_photo(user_id, photo, caption="Пожалуйста, ответьте на несколько вопросов:", reply_markup=markup)

def is_single_number(volume_str):
    # Проверяем, содержит ли строка символ "/"
    return '/' not in volume_str
def handle_driver_choice(call, bot):
    user_id = call.from_user.id
    choice = call.data

    if choice == "my_data":
        user_data_get = user_utils.get_displayed_user_data(user_utils.get_user_data(user_id))
        if user_data_get:
            markup = types.InlineKeyboardMarkup(row_width=2)
            edit_button = types.InlineKeyboardButton("Изменить", callback_data="edit_data")
            back_button = types.InlineKeyboardButton("Назад", callback_data="back")
            markup.add(edit_button, back_button)
            response = "👤 Ваши данные:\n"
            for key, value in user_data_get.items():
                response += f"✅ {key.capitalize()}: {value}\n"

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=response,
                                  reply_markup=markup)
            # with open(user_dict.USER_DATA_PHOTO, 'rb') as photo:
            #    bot.send_photo(user_id, photo, caption=response, reply_markup=markup)
        else:
            bot.send_message(user_id, "🚫 Ваши данные не найдены.")
    elif choice == "view_cargo":
        user_data = user_utils.get_user_data(user_id)
        if user_data and user_data["role"] == "Водитель":
            residence_city = user_data["city"]  # Город проживания водителя
            cargo_type = user_data["loadtype"]  # Тип загрузки водителя
            car_payload = float(user_data["payload"])
            car_volume = user_data["dimensions"]
            car_distance = float(user_data["distance"])

            # Разбиваем текстовое значение размерности кузова на отдельные числа
            car_dimensions = car_volume.split('/')
            car_dimensions = [float(dim) for dim in car_dimensions]

            sheet = user_utils.client.open_by_key(user_utils.SPREADSHEET_ID_APPROVED_CARGO_DATA).get_worksheet(0)

            cargo_buttons = []
            cargo_data = sheet.get_all_values()[1:]  # Пропускаем заголовок

            for row in cargo_data:
                from_location = row[1]
                cargo_row_type = row[6]  # Тип загрузки из таблицы
                cargo_volume = row[4]  # Объем груза из таблицы
                cargo_weight = float(row[5])  # Вес груза из таблицы
                cargo_distance = float(row[3])

                # Разбиваем текстовое значение размерности груза на отдельные числа
                cargo_dimensions = cargo_volume.split('/')
                cargo_dimensions = [float(dim) for dim in cargo_dimensions]

                if is_single_number(cargo_volume):
                    # Если объем груза представлен одним числом, сравниваем его с общим объемом кузова
                    cargo_volume_float = float(cargo_volume)
                    car_volume_float = car_dimensions[0] * car_dimensions[1] * car_dimensions[2]
                    if (
                            from_location == residence_city
                            and cargo_row_type == cargo_type
                            and cargo_weight <= car_payload
                            and cargo_volume_float <= car_volume_float
                            and car_distance >= cargo_distance
                    ):
                        cargo_id = row[0]
                        to_location = row[2]
                        cargo_buttons.append(types.InlineKeyboardButton(f"Груз: {from_location} -> {to_location}",
                                                                        callback_data=f"cargo_{cargo_id}"))
                else:
                    # В противном случае, сравниваем размерности груза и кузова как ранее
                    if (
                            from_location == residence_city
                            and cargo_row_type == cargo_type
                            and cargo_weight <= car_payload
                            and all(cargo_dim <= car_dim for cargo_dim, car_dim in zip(cargo_dimensions, car_dimensions))
                            and (cargo_dimensions[0] * cargo_dimensions[1] * cargo_dimensions[2]) <= (
                            car_dimensions[0] * car_dimensions[1] * car_dimensions[2])
                            and car_distance >= cargo_distance
                    ):
                        cargo_id = row[0]
                        to_location = row[2]
                        cargo_buttons.append(types.InlineKeyboardButton(f"Груз: {from_location} -> {to_location}",
                                                                        callback_data=f"cargo_{cargo_id}"))

            # Добавляем кнопку "Готово" в конце списка грузов
            finish_button = types.InlineKeyboardButton("Готово✅", callback_data="finish")
            cargo_buttons.append(finish_button)

            cargo_buttons_markup = types.InlineKeyboardMarkup(row_width=1)
            cargo_buttons_markup.add(*cargo_buttons)

            with open(user_dict.CARGO_LIST_PHOTO, 'rb') as photo:
                bot.send_photo(user_id, photo, caption="Выберите груз:", reply_markup=cargo_buttons_markup)
        else:
            bot.send_message(user_id, "У вас нет доступа к выбору грузов.")
    elif choice == "view_broker":
        user_data = user_utils.get_user_data(user_id)
        if user_data and user_data["role"] == "Водитель":
            broker_id = user_data["broker_id"]  # Получаем айди диспетчера из данных водителя
            if broker_id:
                broker_data = user_utils.get_broker_data(broker_id)
                if broker_data:
                    phone_buttons_markup = types.InlineKeyboardMarkup(row_width=1)
                    phone_button = types.InlineKeyboardButton(f"Позвонить: +{broker_data['phone']}",
                                                              url=f"http://onmap.uz/tel/{broker_data['phone']}")
                    phone_buttons_markup.add(phone_button)
                    response = f"Данные диспетчера:" \
                               f"\n\nФИО: {broker_data['fullname']}\n" \
                               f"Телефон: {broker_data['phone']}\n" \
                               f"Telegram: {broker_data['telegram']}"
                    with open(user_dict.BROKER_PHOTO, 'rb') as photo:
                        bot.send_photo(user_id, photo, caption=response, reply_markup=phone_buttons_markup)

                else:
                    bot.send_message(user_id, "Диспетчер не найден.")
            else:
                bot.send_message(user_id, "Извините, к вам еще не привязан диспетчер, подождите.")
        else:
            bot.send_message(user_id, "У вас нет доступа к данным диспетчера.")


def handle_cargo_choice(call, bot):
    user_id = call.from_user.id
    cargo_id = call.data.split("_")[1]  # Получаем идентификатор груза из callback_data

    if user_id not in user_dict.chosen_cargo:
        user_dict.chosen_cargo[user_id] = []

    if cargo_id == "finish":
        handle_finish(call, bot)
    elif cargo_id not in user_dict.chosen_cargo[user_id]:
        # Проверяем, не выбран ли уже этот груз в текущей сессии
        cargo_already_chosen = cargo_id in user_dict.chosen_cargo[user_id]

        # Проверяем, не выбирал ли пользователь этот груз ранее
        cargo_already_selected = user_utils.check_if_cargo_already_selected(user_id, cargo_id)

        if not cargo_already_chosen and not cargo_already_selected:
            user_dict.chosen_cargo[user_id].append(cargo_id)
            bot.answer_callback_query(call.id, text="Груз добавлен в выбранные! ✅")
        elif cargo_already_chosen:
            bot.answer_callback_query(call.id, text="Этот груз уже выбран в текущей сессии! ❌")
        elif cargo_already_selected:
            bot.answer_callback_query(call.id, text="Этот груз уже был выбран ранее! ❌")


def handle_finish(call, bot):
    user_id = call.from_user.id
    if user_id in user_dict.chosen_cargo and user_dict.chosen_cargo[user_id]:
        chosen_cargo_ids = user_dict.chosen_cargo[user_id]  # Получаем идентификаторы грузов

        # Добавление идентификаторов выбранных грузов в столбец "Груз и номер груза"
        add_data.add_chosen_cargo(user_id, chosen_cargo_ids)

        user_dict.chosen_cargo[user_id] = []  # Очищаем список выбранных грузов
        bot.send_message(user_id, "Спасибо за выбор! Мы с вами свяжемся. 🚚")
    else:
        bot.send_message(user_id, "Вы еще не выбрали грузы. 🚫")


def handle_cargo(call, bot):
    user_id = call.from_user.id
    user_dict.user_data[user_id] = {}
    with open(user_dict.CARGO_PHOTO, 'rb') as photo:
        bot.send_photo(user_id, photo, caption="Введите данные о грузе.\n\n1. Откуда?")
    bot.register_next_step_handler(call, dialog.ask_cargo_from, bot)


def handle_history(call, bot):
    user_id = call.from_user.id
    user_data = user_utils.get_user_data(user_id)

    if user_data and user_data["role"] == "Водитель":
        markup = types.InlineKeyboardMarkup(row_width=1)

        recent_button = types.InlineKeyboardButton("📆 Недавние", callback_data="recent_history")
        unpaid_button = types.InlineKeyboardButton("💲 Неоплаченные", callback_data="unpaid_history")

        cargo_buttons = []

        history_data = user_utils.get_cargo_history(user_id)
        if history_data:
            for cargo_id, status in history_data.items():
                cargo_button = types.InlineKeyboardButton(
                    f"Заказ {cargo_id} - Подробнее", callback_data=f"history_{cargo_id}"
                )
                cargo_buttons.append(cargo_button)
        else:
            cargo_buttons.append(types.InlineKeyboardButton("История заказов пуста.", callback_data="dummy"))

        markup.add(recent_button, unpaid_button, *cargo_buttons)
        with open(user_dict.CARGO_HISTORY_PHOTO, 'rb') as photo:
            bot.send_photo(user_id, photo, caption="📚 История заказов:", reply_markup=markup)

    else:
        bot.send_message(user_id, "У вас нет доступа к истории заказов.")


def handle_history_details(call, bot):
    user_id = call.from_user.id
    cargo_id = call.data.split("_")[1]  # Получаем идентификатор груза из callback_data
    cargo_details = user_utils.get_cargo_details(cargo_id)
    cargo_history_status = user_utils.get_cargo_history_status(cargo_id)

    if cargo_details and cargo_history_status:
        response = f"📦 Подробности заказа {cargo_id}:\n\n"
        response += f"Город отправки: {cargo_details['from_location']}\n"
        response += f"Город доставки: {cargo_details['to_location']}\n"
        response += f"Статус: {cargo_history_status}\n"
        response += f"Описание: {cargo_details['comments']}\n"
        bot.send_message(user_id, response)
    else:
        bot.send_message(user_id, f"Информация о заказе {cargo_id} не найдена.")


def handle_recent_cargos(call, bot):
    user_id = call.from_user.id
    # Retrieve the last 7 cargos for the driver (modify as needed)
    recent_cargos = user_utils.get_recent_cargos(user_id, 7)
    response = "📆 Последние 7 грузов:\n"
    for cargo_id, cargo_status in recent_cargos.items():
        cargo_details = user_utils.get_cargo_details(cargo_id)
        if cargo_details:
            response += f"📦 Груз {cargo_id}:\n"
            response += f"Откуда: {cargo_details['from_location']}\n"
            response += f"Куда: {cargo_details['to_location']}\n"
            response += f"Комментарии: {cargo_details['comments']}\n"
            response += f"Статус: {cargo_status}\n\n"
    bot.send_message(user_id, response)


def handle_unpaid_cargos(call, bot):
    user_id = call.from_user.id
    # Retrieve all unpaid cargos for the driver
    unpaid_cargos = user_utils.get_unpaid_cargos(user_id)
    response = "💲 Неоплаченные грузы:\n"
    for cargo_id, cargo_status in unpaid_cargos.items():
        cargo_details = user_utils.get_cargo_details(cargo_id)
        if cargo_details:
            response += f"📦 Груз {cargo_id}:\n"
            response += f"Откуда: {cargo_details['from_location']}\n"
            response += f"Куда: {cargo_details['to_location']}\n"
            response += f"Комментарии: {cargo_details['comments']}\n"
            response += f"Статус: {cargo_status}\n\n"
    bot.send_message(user_id, response)


def handle_community(message, bot):
    community_link = "https://t.me/+j7plDmEkx9wyN2Iy"  # Ссылка на сообщество
    bot.send_message(message.chat.id, f"Добро пожаловать в наше сообщество!\n{community_link}")


def broker(message, bot):
    markup = types.InlineKeyboardMarkup()
    update_button = types.InlineKeyboardButton("Обновить рассылку", callback_data="update_notifications")
    markup.add(update_button)
    bot.send_message(message.chat.id, "Админ панель", reply_markup=markup)


def handle_update_notifications(call, bot):
    add_data.update_cargo_notifications(call, bot)
    bot.send_message(call.from_user.id, "Рассылка обновлена!")


def handle_edit_data(call, bot):
    user_id = call.from_user.id
    bot.send_message(user_id, "Пожалуйста обратитесь к администрации за этими контактными данными:")
