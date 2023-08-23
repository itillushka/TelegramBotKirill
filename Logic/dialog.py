import user_dict, add_data


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


def ask_cargo_from(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_from"] = message.text
    bot.send_message(user_id, "2. Куда?")
    bot.register_next_step_handler(message, ask_cargo_to, bot)


def ask_cargo_to(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_to"] = message.text
    bot.send_message(user_id, "3. Дистанция (в километрах)?")
    bot.register_next_step_handler(message, ask_cargo_distance, bot)


def ask_cargo_distance(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_distance"] = message.text
    bot.send_message(user_id, "4. Вес груза (в кг)?")
    bot.register_next_step_handler(message, ask_cargo_weight, bot)


def ask_cargo_weight(message, bot):
    user_id = message.from_user.id
    user_dict.user_data[user_id]["cargo_weight"] = message.text
    bot.send_message(user_id, "5. Оплата (в рублях)?")
    bot.register_next_step_handler(message, save_cargo_info, bot)


def save_cargo_info(message, bot):
    user_id = message.from_user.id
    cargo_info = {
        "from_location": user_dict.user_data[user_id]["cargo_from"],
        "to_location": user_dict.user_data[user_id]["cargo_to"],
        "distance": user_dict.user_data[user_id]["cargo_distance"],
        "weight": user_dict.user_data[user_id]["cargo_weight"],
        "payment": message.text
    }

    add_data.add_cargo_to_google_sheets(**cargo_info)
    bot.send_message(user_id, "Спасибо! Данные о грузе сохранены.")
