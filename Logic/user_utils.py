import gspread
from oauth2client.service_account import ServiceAccountCredentials

JSON_PATH = 'Logic/credentials.json'
SPREADSHEET_ID_USER_DATA = '1Ru0mMLA8L6GyTPjvrFXIZ-dGN6u_CaHVsZiHVJo9R6w'
SPREADSHEET_ID_CARGO_DATA = '11bCdYF4Mt7ZJ9U9gkpKOUnMaBDIqYk3J2DoqQ4v6KFA'
SPREADSHEET_ID_APPROVED_CARGO_DATA = '1Eph_4O0fJzbAITj98-1aigGct9YPyizM7WZ7dCDC-Pw'
SPREADSHEET_ID_BROKER_DATA = '11kHyKE8x1xfMzojRvofHKZkUoK7NIHNhetwhWPlhrV8'
SPREADSHEET_ID_CARGO_HISTORY_DATA = '13ljzO69p1gdKyd7p9QbigiPT_L06R5Qf2GLgBsoGCKI'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, scope)
client = gspread.authorize(creds)


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
        user_data_disp = {
            "role": user_data_row[1] if len(user_data_row) > 1 and user_data_row[1] else "Отсутствует",
            "fullname": user_data_row[2] if len(user_data_row) > 2 and user_data_row[2] else "Отсутствует",
            "phone": user_data_row[3] if len(user_data_row) > 3 and user_data_row[3] else "Отсутствует",
            "sign": user_data_row[4] if len(user_data_row) > 4 and user_data_row[4] else "Отсутствует",
            "payload": user_data_row[5] if len(user_data_row) > 5 and user_data_row[5] else "Отсутствует",
            "dimensions": user_data_row[6] if len(user_data_row) > 6 and user_data_row[6] else "Отсутствует",
            "bodytype": user_data_row[7] if len(user_data_row) > 7 and user_data_row[7] else "Отсутствует",
            "city": user_data_row[8] if len(user_data_row) > 8 and user_data_row[8] else "Отсутствует",
            "distance": user_data_row[9] if len(user_data_row) > 9 and user_data_row[9] else "Отсутствует",
            "legalstatus": user_data_row[10] if len(user_data_row) > 10 and user_data_row[10] else "Отсутствует",
            "carownership": user_data_row[11] if len(user_data_row) > 11 and user_data_row[11] else "Отсутствует",
            "loadtype": user_data_row[12] if len(user_data_row) > 12 and user_data_row[12] else "Отсутствует",
            "broker_id": user_data_row[13] if len(user_data_row) > 13 and user_data_row[13] else "Отсутствует"
        }
        return user_data_disp
    else:
        return {}


def get_drivers_in_city_with_loadtype_weight_and_volume(city, loadtype, cargo_weight, cargo_volume):
    sheet = client.open_by_key(SPREADSHEET_ID_USER_DATA).get_worksheet(0)
    driver_ids = []

    for idx, row in enumerate(sheet.get_all_values(), start=1):  # Пропускаем заголовок
        if (
                row[8] == city  # Проверяем город проживания
                and row[1] == "Водитель"  # Проверяем роль
                and int(row[5]) >= int(cargo_weight)  # Проверяем, что вес груза меньше или равен грузоподъемности автомобиля
                and row[12] == loadtype  # Проверяем тип загрузки
        ):
            # Проверяем, подходит ли водитель по объему кузова
            dimensions = row[6]  # Получаем размеры кузова
            try:
                # Преобразуем cargo_volume в число (если оно строка)
                print(cargo_volume)
                if not isinstance(cargo_volume, (int, float)):
                    cargo_volume = float(cargo_volume)

                # Продолжаем сравнение как и ранее
                dimensions_list = [float(val) for val in dimensions.split("/")]
                product_dimensions = 1
                for dimension in dimensions_list:
                    product_dimensions *= dimension
                    print(product_dimensions)
                if product_dimensions >= cargo_volume:
                    driver_ids.append(int(row[0]))  # Добавляем идентификатор водителяr
                    print(driver_ids)
            except ValueError:
                # Если размеры кузова или cargo_volume не удалось корректно обработать, пропускаем этого водителя
                continue

    return driver_ids







def get_broker_data(broker_id):
    sheet = client.open_by_key(SPREADSHEET_ID_BROKER_DATA).get_worksheet(0)
    broker_ids = sheet.col_values(1)[1:]

    if broker_id in broker_ids:
        broker_row = broker_ids.index(broker_id) + 2  # Индекс строки с broker_id, учитывая заголовок в первой строке
        broker_data_row = sheet.row_values(broker_row)
        broker_data = {
            "fullname": broker_data_row[1],
            "phone": broker_data_row[2],
            "telegram": broker_data_row[3]
        }
        return broker_data
    else:
        return None


def get_cargo_history(user_id):
    sheet = client.open_by_key(SPREADSHEET_ID_CARGO_HISTORY_DATA).get_worksheet(0)
    cargo_history_data = sheet.get_all_values()

    cargo_history = {}  # Словарь для хранения истории грузов {cargo_id: status}
    for row in cargo_history_data[1:]:  # Пропускаем заголовок
        driver_id = row[0]
        cargo_id = row[1]
        status = row[2]

        if driver_id == str(user_id):
            cargo_history[cargo_id] = status

    return cargo_history


def get_cargo_details(cargo_id):
    sheet = client.open_by_key(SPREADSHEET_ID_CARGO_DATA).get_worksheet(0)
    cargo_data = sheet.get_all_values()

    for row in cargo_data[1:]:  # Пропускаем заголовок
        if row[0] == cargo_id:
            cargo_history_sheet = client.open_by_key(SPREADSHEET_ID_CARGO_HISTORY_DATA).get_worksheet(0)
            cargo_history_data = cargo_history_sheet.get_all_values()

            comments = None
            for history_row in cargo_history_data[1:]:
                if history_row[1] == cargo_id:
                    comments = history_row[7]  # Измените на нужный индекс столбца с комментариями
                    break

            cargo_details = {
                "from_location": row[1],
                "to_location": row[2],
                "comments": comments
            }
            return cargo_details

    return None


def get_cargo_history_status(cargo_id):
    sheet = client.open_by_key(SPREADSHEET_ID_CARGO_HISTORY_DATA).get_worksheet(0)
    cargo_history_data = sheet.get_all_values()

    for row in cargo_history_data[1:]:  # Пропускаем заголовок
        if row[1] == cargo_id:
            return row[2]

    return None


def check_if_cargo_already_selected(user_id, cargo_id):
    sheet = client.open_by_key(SPREADSHEET_ID_USER_DATA).get_worksheet(0)
    user_cell = sheet.find(str(user_id))
    if user_cell:
        user_row = user_cell.row
        cargo_cell = sheet.cell(user_row, 15)  # Столбец "Груз и номер груза"
        existing_cargo = cargo_cell.value

        if existing_cargo:
            existing_cargo_ids = set(existing_cargo.split(','))
            return cargo_id in existing_cargo_ids

    return False


def get_recent_cargos(user_id, count):
    sheet = client.open_by_key(SPREADSHEET_ID_CARGO_HISTORY_DATA).get_worksheet(0)
    cargo_history_data = sheet.get_all_values()

    recent_cargos = {}  # Словарь для хранения последних грузов {cargo_id: status}
    user_cargos = [row for row in cargo_history_data[1:] if row[0] == str(user_id)]

    if user_cargos:
        sorted_cargos = sorted(user_cargos, key=lambda x: x[1], reverse=True)
        for row in sorted_cargos[:count]:
            cargo_id = row[1]
            status = row[2]
            recent_cargos[cargo_id] = status

    return recent_cargos


def get_unpaid_cargos(user_id):
    sheet = client.open_by_key(SPREADSHEET_ID_CARGO_HISTORY_DATA).get_worksheet(0)
    cargo_history_data = sheet.get_all_values()

    unpaid_cargos = {}  # Словарь для хранения неоплаченных грузов {cargo_id: status}
    user_cargos = [row for row in cargo_history_data[1:] if row[0] == str(user_id)]

    if user_cargos:
        for row in user_cargos:
            cargo_id = row[1]
            status = row[2]
            if status == "Неоплачен":
                unpaid_cargos[cargo_id] = status

    return unpaid_cargos
