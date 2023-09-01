import user_utils
import user_dict
from telebot import types


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


def add_cargo_to_google_sheets(from_location, to_location, volume, weight, loadtype, description, payment, paymenttype, contacts, comments, bot):
    sheet = user_utils.client.open_by_key(user_utils.SPREADSHEET_ID_CARGO_DATA).get_worksheet(0)  # Открываем лист

    # Получаем текущее количество строк в таблице
    num_rows = len(sheet.get_all_values()) + 1

    # Генерируем идентификатор в формате "Xcrg", где X - порядковый номер груза
    cargo_id = f"{num_rows - 1}crg"

    cargo_info = [cargo_id, from_location, to_location, volume, weight, loadtype, description, payment, paymenttype, contacts, comments]
    sheet.append_row(cargo_info)

    # Оповещаем водителей о новом грузе из их города
    notify_drivers_about_new_cargo(from_location, loadtype,weight, bot)


def notify_drivers_about_new_cargo(from_location, loadtype,weight, bot):
    drivers_with_matching_city = user_utils.get_drivers_in_city(from_location)

    if drivers_with_matching_city:
        message = "Привет! Появился свежий груз в твоем городе!"
        for driver_id in drivers_with_matching_city:
            driver_data = user_utils.get_user_data(driver_id)
            if driver_data and driver_data["loadtype"] == loadtype and driver_data["payload"] <= weight:
                # Добавляем кнопку "Грузы" под уведомлением
                cargo_button = types.InlineKeyboardButton("Просмотреть грузы", callback_data="view_cargo")
                cargo_buttons_markup = types.InlineKeyboardMarkup(row_width=1)
                cargo_buttons_markup.add(cargo_button)

                with open(user_dict.NEW_CARGO_PHOTO, 'rb') as photo:
                    bot.send_photo(driver_id, photo, caption=message, reply_markup=cargo_buttons_markup)
