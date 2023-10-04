import gspread
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from oauth2client.service_account import ServiceAccountCredentials

import handlers
import user_dict
import config

bot = Bot(token=config.TOKEN)

creds = ServiceAccountCredentials.from_json_keyfile_name(config.JSON_PATH, config.scope)
client = gspread.authorize(creds)

# Создаем объект диспетчера (Dispatcher) и подключаем к нему логирование
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


# Обработчик команды /start
@dp.message_handler(commands=['start', 'menu'])
async def start(message: types.Message):
    await handlers.start(message, bot)


@dp.callback_query_handler(lambda call: call.data in ["back"])
async def back(call: types.CallbackQuery):
    chat_id_to_delete = call.message.chat.id
    message_id_to_delete = call.message.message_id

    await bot.delete_message(chat_id_to_delete, message_id_to_delete)

    chat_id = call.message.chat.id
    message_id = 0
    await handlers.handle_driver_role(call, chat_id, message_id, bot)


@dp.callback_query_handler(lambda call: call.data in ["back_cargo"])
async def back_cargo(call: types.CallbackQuery):
    user_id = call.from_user.id
    chat_id_to_delete = call.message.chat.id
    message_id_to_delete = call.message.message_id

    if "started_dialog" in user_dict.user_data[user_id] and user_dict.user_data[user_id]["started_dialog"]:
        await bot.delete_message(chat_id_to_delete, message_id_to_delete)
        user_dict.user_data[user_id] = {}
        await bot.delete_message(chat_id_to_delete, message_id_to_delete + 1)
        await bot.send_message(chat_id_to_delete, "Диалог прерван. Вы вернулись в начальное состояние.")
        # bot.clear_step_handler_by_chat_id(chat_id_to_delete)
    else:
        await bot.delete_message(chat_id_to_delete, message_id_to_delete)


@dp.message_handler(commands=['broker1111'])
async def broker(message: types.Message):
    await handlers.broker(message, bot)


@dp.message_handler(lambda message: message.text == "Диспетчерам")
async def handle_broker_role(message: types.Message):
    await handlers.handle_broker_role(message, bot)


@dp.message_handler(lambda message: message.text == "Перевозчикам")
async def handle_driver_role(call: types.Message):
    chat_id = call.chat.id
    message_id = call.message_id
    await handlers.handle_driver_role(call, chat_id, message_id, bot)


@dp.message_handler(lambda message: message.text == "Сообщество")
async def handle_community_button(message: types.Message):
    await handlers.handle_community(message, bot)


@dp.callback_query_handler(lambda call: call.data in ["start_driver"])
async def start_driver(call: types.CallbackQuery):
    await handlers.start_driver(call, bot)


@dp.callback_query_handler(lambda call: call.data in ["my_data", "view_cargo", "view_broker"])
async def handle_driver_choice(call: types.CallbackQuery):
    await handlers.handle_driver_choice(call, bot)


@dp.callback_query_handler(lambda call: call.data in ["view_history"])
async def handle_history(call: types.CallbackQuery):
    await handlers.handle_history(call, bot)


@dp.callback_query_handler(lambda call: call.data.startswith("cargo_"))
async def handle_cargo_choice(call: types.CallbackQuery):
    await handlers.handle_cargo_choice(call, bot)


@dp.callback_query_handler(lambda call: call.data == "finish")
async def handle_finish(call: types.CallbackQuery):
    await handlers.handle_finish(call, bot)


@dp.message_handler(lambda message: message.text == "Отправить груз")
async def handle_cargo(message: types.Message):
    await handlers.handle_cargo(message, bot)


@dp.callback_query_handler(lambda call: call.data == "next_cargo")
async def handle_cargo_questions(call: types.CallbackQuery):
    await handlers.handle_cargo_questions(call, bot)


@dp.callback_query_handler(lambda call: call.data.startswith("history_"))
async def handle_history_details(call: types.CallbackQuery):
    await handlers.handle_history_details(call, bot)


@dp.callback_query_handler(lambda call: call.data.startswith("recent_history"))
async def handle_recent_cargos(call: types.CallbackQuery):
    await handlers.handle_recent_cargos(call, bot)


@dp.callback_query_handler(lambda call: call.data.startswith("unpaid_history"))
async def handle_unpaid_cargos(call: types.CallbackQuery):
    await handlers.handle_unpaid_cargos(call, bot)


@dp.callback_query_handler(lambda call: call.data == "update_notifications")
async def update_notifications(call: types.CallbackQuery):
    await handlers.handle_update_notifications(call, bot)


@dp.callback_query_handler(lambda call: call.data == "edit_data")
async def update_notifications(call: types.CallbackQuery):
    await handlers.handle_edit_data(call, bot)


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp)
