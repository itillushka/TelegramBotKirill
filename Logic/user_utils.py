import gspread
from oauth2client.service_account import ServiceAccountCredentials

JSON_PATH = '../credentials.json'
SPREADSHEET_ID_USER_DATA = '1Ru0mMLA8L6GyTPjvrFXIZ-dGN6u_CaHVsZiHVJo9R6w'
SPREADSHEET_ID_CARGO_DATA = '1Eph_4O0fJzbAITj98-1aigGct9YPyizM7WZ7dCDC-Pw'
SPREADSHEET_ID_BROKER_DATA = '11kHyKE8x1xfMzojRvofHKZkUoK7NIHNhetwhWPlhrV8'

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
            "role": user_data_row[1],
            "fullname": user_data_row[2],
            "phone": user_data_row[3],
            "sign": user_data_row[4],
            "payload": user_data_row[5],
            "dimensions": user_data_row[6],
            "bodytype": user_data_row[7],
            "city": user_data_row[8],
            "distance": user_data_row[9],
            "legalstatus": user_data_row[10],
            "carownership": user_data_row[11],
            "loadtype": user_data_row[12],
            "broker_id": user_data_row[13]
        }
        return user_data_disp
    else:
        return {}


def get_displayed_user_data(raw_user_data):
    if "role" in raw_user_data:
        user_data_disp = {
            "Профессия": raw_user_data["role"],
            "ФИО": raw_user_data["fullname"],
            "Номер телефона": raw_user_data["phone"],
            "Гос.знак": raw_user_data["sign"],
            "Грузоподьемность": raw_user_data["payload"],
            "Измерения": raw_user_data["dimensions"],
            "Тип кузова": raw_user_data["bodytype"],
            "Город проживания": raw_user_data["city"],
            "Дистанция": raw_user_data["distance"],
            "Юридический статус": raw_user_data["legalstatus"],
            "Владение автомобилем": raw_user_data["carownership"],
            "Тип загрузки": raw_user_data["loadtype"]
        }
        return user_data_disp
    else:
        return {}


def get_drivers_in_city(city):
    sheet = client.open_by_key(SPREADSHEET_ID_USER_DATA).get_worksheet(0)
    driver_ids = []
    for idx, row in enumerate(sheet.get_all_values(), start=1):  # Пропускаем заголовок
        if row[8] == city and row[1] == "Водитель":  # Проверяем город проживания и роль
            driver_ids.append(int(row[0]))  # Добавляем идентификатор водителя

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
