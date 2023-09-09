import add_data
import user_dict

def delete_previous_question_and_answer(user_id, bot, message_id):
    try:
        bot.delete_message(user_id, message_id - 1)  # Удаляем предыдущий вопрос
        bot.delete_message(user_id, message_id)      # Удаляем предыдущий ответ
    except Exception as e:
        pass  # Обработка ошибок, если сообщения уже удалены или не существуют
def ask_phone(message, bot):
    user_id = message.from_user.id
    user_dict.driver_data[user_id]["name"] = message.text

    bot.send_message(message.chat.id, "Ваш телефон?")
    bot.register_next_step_handler(message, ask_car_number, bot)


def ask_car_number(message, bot):
    user_id = message.from_user.id
    user_dict.driver_data[user_id]["phone"] = message.text

    bot.send_message(message.chat.id, "Государственный знак машины?")
    bot.register_next_step_handler(message, ask_cargo_capacity, bot)


def ask_cargo_capacity(message, bot):
    user_id = message.from_user.id
    user_dict.driver_data[user_id]["car_number"] = message.text

    bot.send_message(message.chat.id, "Грузоподъемность машины?")
    bot.register_next_step_handler(message, ask_dimensions, bot)


def ask_dimensions(message, bot):
    user_id = message.from_user.id
    user_dict.driver_data[user_id]["cargo_capacity"] = message.text

    bot.send_message(message.chat.id, "Длина/Ширина/Высота машины?")
    bot.register_next_step_handler(message, ask_body_type, bot)


def ask_body_type(message, bot):
    user_id = message.from_user.id
    user_dict.driver_data[user_id]["dimensions"] = message.text

    bot.send_message(message.chat.id, "Тип кузова?")
    bot.register_next_step_handler(message, ask_residence_city, bot)


def ask_residence_city(message, bot):
    user_id = message.from_user.id
    user_dict.driver_data[user_id]["body_type"] = message.text

    bot.send_message(message.chat.id, "Город проживания?")
    bot.register_next_step_handler(message, ask_distance_to_travel, bot)


def ask_distance_to_travel(message, bot):
    user_id = message.from_user.id
    user_dict.driver_data[user_id]["residence_city"] = message.text

    bot.send_message(message.chat.id, "Дистанция, на которую готовы ездить? (в километрах)")
    bot.register_next_step_handler(message, ask_employment_type, bot)


def ask_employment_type(message, bot):
    user_id = message.from_user.id
    user_dict.driver_data[user_id]["distance_to_travel"] = message.text

    bot.send_message(message.chat.id, "Вы являетесь ИП или самозанятым?")
    bot.register_next_step_handler(message, ask_car_ownership, bot)


def ask_car_ownership(message, bot):
    user_id = message.from_user.id
    user_dict.driver_data[user_id]["employment_type"] = message.text

    bot.send_message(message.chat.id, "У вас машина в аренде или личная?")
    bot.register_next_step_handler(message, save_driver_info, bot)


def save_driver_info(message, bot):
    user_id = message.from_user.id
    user_dict.driver_data[user_id]["car_ownership"] = message.text

    bot.send_message(message.chat.id, "Какой у вас тип загрузки? Задний/верхний/боковой?")
    bot.register_next_step_handler(message, ask_cargo_loading_type, bot)


def ask_cargo_loading_type(message, bot):
    user_id = message.from_user.id
    user_dict.driver_data[user_id]["cargo_loading_type"] = message.text

    add_data.add_driver_to_google_sheets(user_id,
                                         **user_dict.driver_data[user_id])  # Добавляем данные о водителе в таблицу
    bot.send_message(user_id, "Спасибо! Ваши данные сохранены.")
    for i in range(24):
        bot.delete_message(message.chat.id, message.message_id - i)


def ask_cargo_from(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_from"] = message.text
    bot.send_message(user_id, "2. Куда?")
    bot.register_next_step_handler(message, ask_cargo_to, bot)

    # Удаляем предыдущий вопрос и ответ
    delete_previous_question_and_answer(user_id, bot, message.message_id)


def ask_cargo_to(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_to"] = message.text
    bot.send_message(user_id, "2. Какая дистанция до места доставки (в километрах)?")
    bot.register_next_step_handler(message, ask_cargo_distance, bot)

    # Удаляем предыдущий вопрос и ответ
    delete_previous_question_and_answer(user_id, bot, message.message_id)


def ask_cargo_distance(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_distance"] = message.text
    bot.send_message(user_id,
                     "3. Объем груза в метрах кубических, если не знаете, то введите размерность по примеру '2.1/4.2/2.0'")
    bot.register_next_step_handler(message, ask_cargo_volume, bot)

    # Удаляем предыдущий вопрос и ответ
    delete_previous_question_and_answer(user_id, bot, message.message_id)


def ask_cargo_volume(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_volume"] = message.text

    # Разделяем текст сообщения по символу "/", если он присутствует
    volume_input = message.text.split("/")

    # Инициализируем переменную для хранения объема
    cargo_volume = 0

    if len(volume_input) == 1:
        # Если введен только одно число, сохраняем его как объем
        cargo_volume = volume_input[0]
    elif len(volume_input) >= 2:
        # Если введено два или более числа, попробуем перемножить их
        try:
            cargo_volume = float(volume_input[0]) * float(volume_input[1])
        except ValueError:
            # Если не удалось перемножить числа, оставляем значение нулевым
            cargo_volume = 0

    user_dict.user_data[user_id]["cargo_volume"] = cargo_volume

    bot.send_message(user_id, "4. Тип загрузки (Верхний/Задний/Боковой)?")
    bot.register_next_step_handler(message, ask_cargo_loadtype, bot)

    # Удаляем предыдущий вопрос и ответ
    delete_previous_question_and_answer(user_id, bot, message.message_id)


def ask_cargo_loadtype(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_loadtype"] = message.text
    bot.send_message(user_id, "5. Вес груза в тоннах?")
    bot.register_next_step_handler(message, ask_cargo_weight, bot)


def ask_cargo_weight(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_weight"] = message.text
    bot.send_message(user_id, "6. Описание груза?")
    bot.register_next_step_handler(message, ask_cargo_description, bot)


def ask_cargo_description(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_description"] = message.text
    bot.send_message(user_id, "7. Оплата (в рублях)?")
    bot.register_next_step_handler(message, ask_cargo_payment, bot)


def ask_cargo_payment(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_payment"] = message.text
    bot.send_message(user_id, "8. Каков тип оплаты? НДС, без НДС, на карту, наличными")
    bot.register_next_step_handler(message, ask_payment_type, bot)


def ask_payment_type(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["payment_type"] = message.text
    bot.send_message(user_id, "9. Контакты (телефон и ФИО) через запятую.?")  # Ваш вопрос о типе оплаты
    bot.register_next_step_handler(message, ask_cargo_contacts, bot)


def ask_cargo_contacts(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_contacts"] = message.text
    bot.send_message(user_id, "Комментарии к заказу?")  # Ваш вопрос о комментариях к заказу
    bot.register_next_step_handler(message, save_cargo_info, bot)


def save_cargo_info(message, bot):
    user_id = message.from_user.id
    cargo_info = {
        "from_location": user_dict.user_data[user_id]["cargo_from"],
        "to_location": user_dict.user_data[user_id]["cargo_to"],
        "distance": user_dict.user_data[user_id]["cargo_distance"],
        "volume": user_dict.user_data[user_id]["cargo_volume"],
        "weight": user_dict.user_data[user_id]["cargo_weight"],
        "loadtype": user_dict.user_data[user_id]["cargo_loadtype"],
        "description": user_dict.user_data[user_id]["cargo_description"],
        "payment": user_dict.user_data[user_id]["cargo_payment"],
        "paymenttype": user_dict.user_data[user_id]["payment_type"],
        "contacts": user_dict.user_data[user_id]["cargo_contacts"],
        "comments": message.text
    }

    add_data.add_cargo_to_google_sheets(**cargo_info, bot=bot)
    bot.send_message(user_id, "Спасибо! Данные о грузе сохранены.")


