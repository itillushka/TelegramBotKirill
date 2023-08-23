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
            "role": user_data_row[1],
            "name": user_data_row[2],
            "phone": user_data_row[3],
            "car_plate": user_data_row[4],
            "cargo_capacity": user_data_row[5],
            "dimensions": user_data_row[6],
            "body_type": user_data_row[7],
            "city": user_data_row[8],
            "distance": user_data_row[9],
            "ip_or_self_employed": user_data_row[10],
            "rent_or_own_car": user_data_row[11],
            "cargo_loading_type": user_data_row[12]
        }
        return user_data_disp
    else:
        return {}
