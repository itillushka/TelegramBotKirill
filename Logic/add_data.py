import user_utils

def add_chosen_cargo(user_id, cargo_id):
    sheet = user_utils.client.open_by_key(user_utils.SPREADSHEET_ID_USER_DATA).get_worksheet(0)

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

def add_cargo_to_google_sheets(from_location, to_location, distance, weight, payment):
    sheet = user_utils.client.open_by_key(user_utils.SPREADSHEET_ID_CARGO_DATA).get_worksheet(0)  # Открываем лист

    # Получаем текущее количество строк в таблице
    num_rows = len(sheet.get_all_values()) + 1

    # Генерируем идентификатор в формате "Xcrg", где X - порядковый номер груза
    cargo_id = f"{num_rows - 1}crg"

    cargo_info = [cargo_id, from_location, to_location, distance, weight, payment]
    sheet.append_row(cargo_info)