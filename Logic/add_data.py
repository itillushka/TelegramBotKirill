import user_utils
import user_dict
from telebot import types
import bot_responses


def add_chosen_cargo(user_id, chosen_cargo_ids):
    sheet = user_utils.client.open_by_key(user_utils.SPREADSHEET_ID_USER_DATA).get_worksheet(0)
    user_cell = sheet.find(str(user_id))
    if user_cell:
        user_row = user_cell.row
        cargo_cell = sheet.cell(user_row, 15)  # Столбец "Груз и номер груза"
        existing_cargo = cargo_cell.value

        if existing_cargo:
            existing_cargo_ids = set(existing_cargo.split(','))
            new_cargo_ids = set(chosen_cargo_ids)
            updated_cargo_ids = existing_cargo_ids.union(new_cargo_ids)
            updated_cargo = ','.join(updated_cargo_ids)
        else:
            updated_cargo = ','.join(chosen_cargo_ids)

        cargo_cell.value = updated_cargo
        sheet.update_cell(user_row, 15, updated_cargo)


def add_driver_to_google_sheets(user_id, **data):
    sheet = user_utils.client.open_by_key(user_utils.SPREADSHEET_ID_USER_DATA).get_worksheet(0)

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


def add_cargo_to_google_sheets(from_location, to_location, distance, volume, weight, loadtype, description, payment, paymenttype,
                               contacts, comments, bot):
    sheet = user_utils.client.open_by_key(user_utils.SPREADSHEET_ID_CARGO_DATA).get_worksheet(0)  # Открываем лист

    # Получаем текущее количество строк в таблице
    num_rows = len(sheet.get_all_values()) + 1

    # Генерируем идентификатор в формате "Xcrg", где X - порядковый номер груза
    cargo_id = f"{num_rows - 1}crg"

    cargo_info = [cargo_id, from_location, to_location, distance, volume, weight, loadtype, description, payment, paymenttype,
                  contacts, comments]
    sheet.append_row(cargo_info)


def update_cargo_notifications(call, bot):
    user_id = call.from_user.id
    sheet = user_utils.client.open_by_key(user_utils.SPREADSHEET_ID_APPROVED_CARGO_DATA).get_worksheet(0)
    cargo_data = sheet.get_all_values()

    for row in cargo_data[1:]:  # Пропускаем заголовок
        cargo_id = row[0]
        approved = row[12]

        if not approved:
            from_location = row[1]
            to_location = row[2]
            distance = row[3]
            volume = row[4]
            weight = row[5]
            loadtype = row[6]
            payment = row[8]
            comments = row[10]

            # Проверяем, есть ли идентификатор груза в ячейке столбца номер 11
            if cargo_id not in row[12:]:
                notify_drivers_about_new_cargo(from_location, to_location, distance, volume, weight, loadtype, payment, comments, bot)
                # Добавляем "да" в 11-ю ячейку после отправки уведомления
                cargo_row_index = cargo_data.index(row) + 1
                sheet.update_cell(cargo_row_index, 13, "да")
                # Сообщаем о том, какой груз был обновлен
                bot.send_message(user_id, f"Груз с идентификатором {cargo_id} обновил рассылку.")


def notify_drivers_about_new_cargo(from_location, to_location, distance, volume, weight, loadtype, payment, comments, bot):
    drivers_with_matching_city = user_utils.get_drivers_in_city_with_loadtype_weight_and_volume(from_location, loadtype, weight, volume)

    if drivers_with_matching_city:
        #message = "Привет! Появился свежий груз в твоем городе!"
        for driver_id in drivers_with_matching_city:
            driver_data = user_utils.get_user_data(driver_id)
            if driver_data:
                # Добавляем кнопку "Грузы" под уведомлением
                cargo_button = types.InlineKeyboardButton("Просмотреть грузы", callback_data="view_cargo")
                cargo_buttons_markup = types.InlineKeyboardMarkup(row_width=1)
                cargo_buttons_markup.add(cargo_button)
                message_str = bot_responses.new_cargo_response(from_location, to_location, distance, weight, volume, comments, payment)

                with open(user_dict.NEW_CARGO_PHOTO, 'rb') as photo:
                    bot.send_photo(driver_id, photo, caption=message_str, reply_markup=cargo_buttons_markup, parse_mode="HTML")
