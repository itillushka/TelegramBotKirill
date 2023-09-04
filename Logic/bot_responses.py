def new_cargo_response(from_location, to_location, distance, date_from, date_to, weight, volume, comments, payment):
    new_cargo_str = f"📦 ДАННЫЕ О ГРУЗЕ:\n" \
                    f"🅰️ ЗАГРУЗКА: {from_location}\n" \
                    "⬇️\n" \
                    f"⬇️ {distance} km\n" \
                    "⬇️\n" \
                    f"🅱️ РАЗГРУЗКА: {to_location}\n\n" \
                    f"Загрузка: {date_from} \n" \
                    f"Разгрузка: {date_to}\n" \
                    f"Вес, т: {weight}\n" \
                    f"Объём, м3: {volume}\n" \
                    f"ДxШxВ,м: {volume}\n\n" \
                    f"{comments}\n\n" \
                    f"💵 СТАВКА ₽: {payment}\n\n" \
                    f"📞 ДИСПЕТЧЕР: @Safron195"
    return new_cargo_str


print(new_cargo_response("Ростов", "Москва", 500, "1.09", "1.09",2,200,"пппп",5000))


def user_data_response(raw_user_data):
    if "role" in raw_user_data:
        user_data_str = "📁 МОИ ДАННЫЕ:\n\n" \
                        "👤 ЛИЧНАЯ ИНФОРМАЦИЯ:\n\n" \
                        f"ФИО: {raw_user_data['fullname']}\n" \
                        f"Номер телефона: {raw_user_data['phone']}\n" \
                        f"Город проживания: {raw_user_data['city']}\n" \
                        f"Юридический статус: {raw_user_data['legalstatus']}\n\n" \
                        f"🚗 ИНФОРМАЦИЯ О ТС:\n\n" \
                        f"Гос.знак: {raw_user_data['sign']}\n" \
                        f"Грузоподьемность: {raw_user_data['payload']} тонны\n" \
                        f"Объем: {raw_user_data['dimensions']}\n" \
                        f"Тип кузова: {raw_user_data['bodytype']}\n" \
                        f"Тип загрузки: {raw_user_data['loadtype']}\n" \
                        f"Владение автомобилем: {raw_user_data['carownership']}\n\n" \
                        f"⚙️ НАСТРОЙКИ ПРОФИЛЯ:\n\n" \
                        f"Роль: {raw_user_data['role']}\n" \
                        f"Дистанция : {raw_user_data['distance']} км\n"
        return user_data_str
    else:
        return {}

