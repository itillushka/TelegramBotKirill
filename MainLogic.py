import os
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

TOKEN = "6633230318:AAEPmoWn2SgZsenyflbzZEP2hJ_Fgg6-diM"
DATA_FILE = "Data/user_data.xlsx"
BROKER_PASSWORD = "1234"
AUTHORIZED_BROKERS = set()

SELECT_ROLE, DRIVER_DETAILS, BROKER_CARGO, ADD_CARGO, VERIFY_PASSWORD = range(5)

DRIVER_QUESTIONS = [
    "Ваше полное имя?",
    "Ваш возраст?",
    "Какая у вас машина?",
    "Из какого вы города?",
    "На какую дистанцию готовы ездить? (в километрах)"
]

def start(update: Update, context: CallbackContext) -> int:
    keyboard = [['Брокер', 'Водитель']]
    update.message.reply_text("Привет! Выберите вашу роль:", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return SELECT_ROLE

def select_role(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    role = update.message.text.lower()
    context.user_data["role"] = role

    if role == "брокер":
        update.message.reply_text("Введите пароль для доступа к роли 'брокер':")
        return ADD_CARGO
    elif role == "водитель":
        context.user_data["driver_question_index"] = 0
        update.message.reply_text(DRIVER_QUESTIONS[0])
        return DRIVER_DETAILS
    else:
        update.message.reply_text("Пожалуйста, выберите 'Брокер' или 'Водитель'.")


def driver_details(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    current_question_index = context.user_data["driver_question_index"]

    context.user_data[f"question_{current_question_index + 1}"] = update.message.text

    if current_question_index + 1 < len(DRIVER_QUESTIONS):
        next_question = DRIVER_QUESTIONS[current_question_index + 1]
        context.user_data["driver_question_index"] = current_question_index + 1
        update.message.reply_text(next_question)
    else:
        save_driver_info(user_id, context.user_data)
        update.message.reply_text("Информация сохранена. Спасибо!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


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

def save_driver_info(user_id, user_data) -> None:
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["User ID"] + [f"Question {i + 1}" for i in range(len(DRIVER_QUESTIONS))])
    else:
        df = pd.read_excel(DATA_FILE)

    new_row = {"User ID": user_id}
    for i, question in enumerate(DRIVER_QUESTIONS):
        new_row[f"Question {i + 1}"] = user_data.get(f"question_{i + 1}", "")

    new_row_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_row_df], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)

def add_cargo(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    cargo = update.message.text
    role = context.user_data.get("role")

    if role == "брокер":
        if context.user_data.get("authorized_broker"):
            save_broker_info(update, context)
            return ConversationHandler.END
        else:
            update.message.reply_text("Введите пароль для доступа к роли 'брокер':")
            return VERIFY_PASSWORD
    else:
        update.message.reply_text("Пожалуйста, выберите 'Брокер' или 'Водитель'.")

def verify_password(update: Update, context: CallbackContext) -> int:
    password = update.message.text.strip()
    if password == BROKER_PASSWORD:
        context.user_data["authorized_broker"] = True
        update.message.reply_text("Пароль верен. Теперь введите ваш груз:")
        return ADD_CARGO
    else:
        update.message.reply_text("Неверный пароль. Выберите 'Брокер' или 'Водитель'.")
        return SELECT_ROLE
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
            VERIFY_PASSWORD: [MessageHandler(Filters.text & ~Filters.command, verify_password)],
            BROKER_CARGO: [MessageHandler(Filters.text & ~Filters.command, add_cargo)],
            DRIVER_DETAILS: [MessageHandler(Filters.text & ~Filters.command, driver_details)],
            ADD_CARGO: [MessageHandler(Filters.text & ~Filters.command, add_cargo)],
        },
        fallbacks=[MessageHandler(Filters.command, cancel)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

