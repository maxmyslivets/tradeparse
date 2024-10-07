from telegram import Update
from telegram.ext import Application, ContextTypes

from config import conf
from parsing.parsing import parse
from db.json_db import load_data, save_data, set_user, get_users
from logger import log


# Функция для обработки команды /start
@log.catch
async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.info(f'Пользователь `{update.effective_user.full_name}` /start')
    user_id = update.effective_user.id
    if user_id not in get_users():
        set_user(user_id)
    await update.message.reply_text(
        f'Привет, {update.effective_user.full_name}! Я бот для парсинга сайта https://icetrade.by. '
        f'Я буду уведомлять вас о новых закупках.')


# Функция для обработки команды /parse
@log.catch
async def command_parse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id in get_users():
        log.info(f'Пользователь `{update.effective_user.first_name}` /parse')
        old_data = load_data()
        new_data = await parse(conf.general.url)
        new_entries = _compare_data(new_data, old_data)

        if new_entries:
            save_data(new_data)
            await update.message.reply_text('Найдены новые данные.')
            for key, value in list(new_entries.items()):
                formatted_message = ""
                for k, v in value.items():
                    formatted_message += f"{k}: {v}\n"
                await update.message.reply_text(formatted_message)
        else:
            await update.message.reply_text('Новых данных не найдено.')
    else:
        log.warning(f'Неизвестный пользователь `{update.effective_user.first_name}` пытается выполнить команду /parse')
        await update.message.reply_text('Вы не подписаны на рассылку.')


# Функция для сравнения новых данных с прошлыми
def _compare_data(new_data, old_data):
    new_entries = {}
    for key, value in new_data.items():
        if key not in old_data:
            new_entries[key] = value
    return new_entries


@log.catch
async def scheduled_parse(application: Application) -> None:
    log.info("Автоматическая проверка на наличие новых данных ...")
    old_data = load_data()
    new_data = await parse(conf.general.url)
    new_entries = _compare_data(new_data, old_data)

    if new_entries:
        save_data(new_data)
        for key, value in list(new_entries.items()):
            formatted_message = ""
            print(formatted_message)
            for k, v in value.items():
                formatted_message += f"{k}: {v}\n"
            for user_id in get_users():
                await application.bot.send_message(chat_id=user_id, text=formatted_message)
