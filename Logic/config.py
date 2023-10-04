import os

TOKEN = '6633230318:AAEPmoWn2SgZsenyflbzZEP2hJ_Fgg6-diM'

# Путь к файлу JSON с учетными данными для доступа к Google Таблицам
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

JSON_PATH = 'credentials.json'
SPREADSHEET_ID_USER_DATA = '1Ru0mMLA8L6GyTPjvrFXIZ-dGN6u_CaHVsZiHVJo9R6w'
SPREADSHEET_ID_CARGO_DATA = '11bCdYF4Mt7ZJ9U9gkpKOUnMaBDIqYk3J2DoqQ4v6KFA'
SPREADSHEET_ID_APPROVED_CARGO_DATA = '1Eph_4O0fJzbAITj98-1aigGct9YPyizM7WZ7dCDC-Pw'
SPREADSHEET_ID_BROKER_DATA = '11kHyKE8x1xfMzojRvofHKZkUoK7NIHNhetwhWPlhrV8'
SPREADSHEET_ID_CARGO_HISTORY_DATA = '13ljzO69p1gdKyd7p9QbigiPT_L06R5Qf2GLgBsoGCKI'

current_directory = os.path.dirname(os.path.abspath(__file__))
# Пути ко всем изображениям
CARGO_PHOTO = os.path.join(current_directory, '..', 'resources', 'Frame 32.png')
DRIVER_REG_PHOTO = os.path.join(current_directory, '..', 'resources', 'Frame 33.png')
START_PHOTO = os.path.join(current_directory, '..', 'resources', 'Frame 34.png')
REGISTRATION_PHOTO = os.path.join(current_directory, '..', 'resources', 'Frame 35.png')
USER_DATA_PHOTO = os.path.join(current_directory, '..', 'resources', 'Frame 36.png')
BROKER_PHOTO = os.path.join(current_directory, '..', 'resources', 'Frame 37.png')
NEW_CARGO_PHOTO = os.path.join(current_directory, '..', 'resources', 'Frame 39.png')
CARGO_HISTORY_PHOTO = os.path.join(current_directory, '..', 'resources', 'Frame 40.png')
DRIVER_MENU_PHOTO = os.path.join(current_directory, '..', 'resources', 'Frame 41.png')
CARGO_LIST_PHOTO = os.path.join(current_directory, '..', 'resources', 'Frame 42.png')