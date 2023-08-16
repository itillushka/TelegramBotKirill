import os
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

TOKEN = "6633230318:AAEPmoWn2SgZsenyflbzZEP2hJ_Fgg6-diM"
DATA_FILE = "Data/user_data.xlsx"

SELECT_ROLE, DRIVER_CAR, BROKER_CARGO, ADD_CARGO = range(4)

def start(update: Update, context: CallbackContext) -> int:
    keyboard = [['Брокер', 'Водитель']]
    update.message.reply_text("Привет! Выберите вашу роль:", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return SELECT_ROLE

def select_role(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    role = update.message.text.lower()
    context.user_data["role"] = role

    if role == "брокер":
        update.message.reply_text("Отлично! Какой у вас груз?")
        return BROKER_CARGO
    elif role == "водитель":
        update.message.reply_text("Какая у вас машина?")
        return DRIVER_CAR
    else:
        update.message.reply_text("Пожалуйста, выберите 'Брокер' или 'Водитель'.")

def save_broker_info(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    cargo = update.message.text

    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["User ID", "Role", "Cargo", "Car"])
    else:
        df = pd.read_excel(DATA_FILE)

    new_row = pd.DataFrame({"User ID": [user_id], "Role": ["Брокер"], "Cargo": [cargo], "Car": [""]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)

    update.message.reply_text("Информация сохранена. Спасибо!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def save_driver_info(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    car = update.message.text

    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["User ID", "Role", "Cargo", "Car"])
    else:
        df = pd.read_excel(DATA_FILE)

    new_row = pd.DataFrame({"User ID": [user_id], "Role": ["Водитель"], "Cargo": [""], "Car": [car]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)

    update.message.reply_text("Информация сохранена. Спасибо!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def add_cargo(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    cargo = update.message.text

    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["User ID", "Role", "Cargo", "Car"])
    else:
        df = pd.read_excel(DATA_FILE)

    new_row = pd.DataFrame({"User ID": [user_id], "Role": ["Брокер"], "Cargo": [cargo], "Car": [""]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)

    update.message.reply_text("Груз добавлен. Спасибо!")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Операция отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_ROLE: [MessageHandler(Filters.text & ~Filters.command, select_role)],
            BROKER_CARGO: [MessageHandler(Filters.text & ~Filters.command, save_broker_info)],
            DRIVER_CAR: [MessageHandler(Filters.text & ~Filters.command, save_driver_info)],
            ADD_CARGO: [MessageHandler(Filters.text & ~Filters.command, add_cargo)],
        },
        fallbacks=[MessageHandler(Filters.command, cancel)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
