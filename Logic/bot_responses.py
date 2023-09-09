def new_cargo_response(from_location, to_location, distance, weight, volume, comments, payment):
    # Проверяем, содержит ли volume символ "/", если нет, то volume - это одно число
    if '/' in str(volume):
        volume_str = f"<b>Объём, м3:</b> {volume}"
        dimensions = volume.split("/")
        dimensions_str = f"<b>ДxШxВ,м:</b> {' x '.join(dimensions)}"
    else:
        volume_str = "<b>Объём, м3:</b> Отсутствует информация"
        dimensions_str = "<b>ДxШxВ,м:</b> Отсутствует информация"

    new_cargo_str = f"📦 <b>ДАННЫЕ О ГРУЗЕ:</b>\n" \
                    f"🅰️ <b>ЗАГРУЗКА:</b> {from_location}\n" \
                    "⬇️\n" \
                    f"⬇️ {distance} km\n" \
                    "⬇️\n" \
                    f"🅱️ <b>РАЗГРУЗКА:</b> {to_location}\n\n" \
                    f"<b>Вес, т:</b> {weight}\n" \
                    f"{volume_str}\n" \
                    f"{dimensions_str}\n\n" \
                    f"{comments}\n\n" \
                    f"💵 <b>СТАВКА ₽:</b> {payment}\n\n" \
                    f"📞 <b>ДИСПЕТЧЕР:</b> @Safron195"
    return new_cargo_str




def user_data_response(raw_user_data):
    if "role" in raw_user_data:
        user_data_str = "📁 <b>МОИ ДАННЫЕ:</b>\n\n" \
                        "👤 <b>ЛИЧНАЯ ИНФОРМАЦИЯ:</b>\n\n" \
                        f"<b>ФИО:</b> {raw_user_data['fullname']}\n" \
                        f"<b>Номер телефона:</b> {raw_user_data['phone']}\n" \
                        f"<b>Город проживания:</b> {raw_user_data['city']}\n" \
                        f"<b>Юридический статус:</b> {raw_user_data['legalstatus']}\n\n" \
                        f"🚗 <b>ИНФОРМАЦИЯ О ТС:</b>\n\n" \
                        f"<b>Гос.знак:</b> {raw_user_data['sign']}\n" \
                        f"<b>Грузоподьемность:</b> {raw_user_data['payload']} тонны\n" \
                        f"<b>Объем:</b> {raw_user_data['dimensions']}\n" \
                        f"<b>Тип кузова:</b> {raw_user_data['bodytype']}\n" \
                        f"<b>Тип загрузки:</b> {raw_user_data['loadtype']}\n" \
                        f"<b>Владение автомобилем:</b> {raw_user_data['carownership']}\n\n" \
                        f"⚙️ <b>НАСТРОЙКИ ПРОФИЛЯ:</b>\n\n" \
                        f"<b>Код диспетчера:</b> {raw_user_data['broker_id']}\n"\
                        f"<b>Роль:</b> {raw_user_data['role']}\n" \
                        f"<b>Дистанция:</b> {raw_user_data['distance']} км\n"
        return user_data_str
    else:
        return {}


def broker_data_response(broker_data):
    broker_data_str = "📞 <b>МОЙ ДИСПЕТЧЕР:</b>\n\n" \
                      "👤 ЛИЧНАЯ ИНФОРМАЦИЯ:\n\n" \
                      f"ФИО: {broker_data['fullname']}\n" \
                      f"Номер телефона: {broker_data['phone']}\n\n" \
                      f"Telegram:{broker_data['telegram']}\n\n" \
                      "❗️ПО ДРУГИМ ВОПРОСАМ\n" \
                      "только звонить: +79518400535 Павел"
    return broker_data_str
