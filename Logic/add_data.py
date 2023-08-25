import user_utils
from telebot import types

def add_chosen_cargo(user_id, cargo_id):
    sheet = user_utils.client.open_by_key(user_utils.SPREADSHEET_ID_USER_DATA).get_worksheet(0)

    # Найдем строку, где user_id совпадает
    for idx, row in enumerate(sheet.get_all_values(), start=1):
        if row[0] == str(user_id):
            user_row = idx  # Индекс строки, где нашли совпадение

            # Получаем текущее значение ячейки с выбранными грузами
            current_cargo_ids = row[len(row) - 1]  # Последний столбец

            # Объединяем текущие идентификаторы и новый идентификатор через запятую
            updated_cargo_ids = f"{current_cargo_ids},{cargo_id}" if current_cargo_ids else cargo_id

            # Обновляем значение ячейки
            sheet.update_cell(user_row, len(row), updated_cargo_ids)
            break  # Прерываем цикл, так как нашли нужную строку



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


def add_cargo_to_google_sheets(from_location, to_location, volume, weight, description, payment, contacts, bot):
    sheet = user_utils.client.open_by_key(user_utils.SPREADSHEET_ID_CARGO_DATA).get_worksheet(0)  # Открываем лист

    # Получаем текущее количество строк в таблице
    num_rows = len(sheet.get_all_values()) + 1

    # Генерируем идентификатор в формате "Xcrg", где X - порядковый номер груза
    cargo_id = f"{num_rows - 1}crg"

    cargo_info = [cargo_id, from_location, to_location, volume, weight, description, payment, contacts]
    sheet.append_row(cargo_info)

    # Оповещаем водителей о новом грузе из их города
    notify_drivers_about_new_cargo(from_location, bot)


def notify_drivers_about_new_cargo(from_location, bot):
    drivers_with_matching_city = user_utils.get_drivers_in_city(from_location)

    if drivers_with_matching_city:
        message = "Привет! Появился свежий груз в твоем городе!"
        for driver_id in drivers_with_matching_city:
            # Добавляем кнопку "Грузы" под уведомлением
            cargo_button = types.InlineKeyboardButton("Просмотреть грузы", callback_data="view_cargo")
            cargo_buttons_markup = types.InlineKeyboardMarkup(row_width=1)
            cargo_buttons_markup.add(cargo_button)

            bot.send_message(driver_id, message, reply_markup=cargo_buttons_markup)
