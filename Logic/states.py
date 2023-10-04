from aiogram.dispatcher.filters.state import State, StatesGroup

class CargoData(StatesGroup):
    cargo_from = State()  # Шаг 1: Запрос откуда
    cargo_to = State()  # Шаг 2: Запрос куда
    cargo_distance = State()  # Шаг 3: Запрос дистанции
    cargo_volume = State()  # Шаг 4: Запрос объема
    cargo_loadtype = State()  # Шаг 5: Запрос типа загрузки
    cargo_weight = State()  # Шаг 6: Запрос веса
    cargo_description = State()  # Шаг 7: Запрос описания
    cargo_payment = State()  # Шаг 8: Запрос оплаты
    cargo_paymenttype = State()  # Шаг 9: Запрос типа оплаты
    cargo_contacts = State()  # Шаг 10: Запрос контактов
    cargo_comments = State()  # Шаг 11: Завершение диалога
