import gspread
from oauth2client.service_account import ServiceAccountCredentials

JSON_PATH = '../credentials.json'
SPREADSHEET_ID_USER_DATA = '1Ru0mMLA8L6GyTPjvrFXIZ-dGN6u_CaHVsZiHVJo9R6w'
SPREADSHEET_ID_CARGO_DATA = '1Eph_4O0fJzbAITj98-1aigGct9YPyizM7WZ7dCDC-Pw'

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
            "Профессия": user_data_row[1],
            "ФИО": user_data_row[2],
            "Номер телефона": user_data_row[3],
            "Гос.знак": user_data_row[4],
            "Грузоподьемность": user_data_row[5],
            "Измерения": user_data_row[6],
            "Тип кузова": user_data_row[7],
            "Город проживания": user_data_row[8],
            "Дистанция": user_data_row[9],
            "Юридический статус": user_data_row[10],
            "Владение автомобилем": user_data_row[11],
            "Тип загрузки": user_data_row[12]
        }
        return user_data_disp
    else:
        return {}
