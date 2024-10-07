from telegram import Update
from telegram.ext import Application, ContextTypes

from config import conf
from parsing.parsing import parse
from db.json_db import load_data, save_data


subscribed_users = set()    # TODO: список подписчиков перенести в БД
latest_new_data = {}


# Функция для обработки команды /start
async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    subscribed_users.add(user_id)
    await update.message.reply_text(
        'Привет! Я бот для парсинга сайта https://icetrade.by. Я буду уведомлять вас о новых данных.')


# Функция для обработки команды /parse
async def command_parse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    old_data = load_data()
    new_data = await parse(conf.general.url)
    new_entries = _compare_data(new_data, old_data)

    if new_entries:
        global latest_new_data
        latest_new_data = new_entries
        save_data(new_data)
        await update.message.reply_text('Найдены новые данные. Вот некоторые из них:')
        for key, value in list(new_entries.items())[:5]:  # Выводим первые 5 новых записей
            formatted_message = f"Ключ: {key}\n"
            for k, v in value.items():
                formatted_message += f"{k}: {v}\n"
            await update.message.reply_text(formatted_message)
    else:
        await update.message.reply_text('Новых данных не найдено.')


# Функция для сравнения новых данных с прошлыми
def _compare_data(new_data, old_data):
    # FIXME Сравнивать не ключ, а все данные, в частности Номер
    new_entries = {}
    for key, value in new_data.items():
        if key not in old_data:
            new_entries[key] = value
    return new_entries


async def scheduled_parse(application: Application) -> None:
    try:
        old_data = load_data()
        new_data = await parse(conf.general.url)
        new_entries = _compare_data(new_data, old_data)

        if new_entries:
            global latest_new_data
            latest_new_data = new_entries
            save_data(new_data)
            for key, value in list(new_entries.items())[:5]:  # Выводим первые 5 новых записей
                formatted_message = f"Ключ: {key}\n"
                for k, v in value.items():
                    formatted_message += f"{k}: {v}\n"
                for user_id in subscribed_users:
                    await application.bot.send_message(chat_id=user_id, text=formatted_message)
    except Exception as e:
        # Отправляем сообщение об ошибке в чат (можете изменить chat_id на ваш собственный)
        for user_id in subscribed_users:
            try:
                await application.bot.send_message(chat_id=user_id, text=f"Ошибка в парсинге данных: {e}")
            except Exception as send_error:
                print(f"Не удалось отправить сообщение об ошибке: {send_error}")
        # Логирование ошибки
        print(f"Ошибка в scheduled_parse: {e}")


# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    error_message = f"Произошла ошибка: {context.error}"

    # Отправка сообщения в чат (если доступен user_id)
    if update.effective_chat:
        await update.effective_chat.send_message(error_message)

    # Логирование ошибки (можно настроить логирование в файл)
    print(f"Ошибка: {context.error}")
