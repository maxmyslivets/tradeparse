from aiogram import types
from aiogram import Dispatcher
from aiogram.filters import Command

from config import conf
from parsing.parsing import parse as parse_url
from db.json_db import load_data, save_data, set_user, get_users
from logger import log


# Создаем экземпляр dispatcher для регистрации хендлеров
dp = Dispatcher()


# Функция для обработки команды /start
async def start(message: types.Message) -> None:
    log.info(f'Пользователь `{message.from_user.full_name}` /start')
    user_id = message.from_user.id
    if user_id not in get_users():
        set_user(user_id)
    await message.answer(
        f'Привет, {message.from_user.full_name}! Я бот для парсинга сайта https://icetrade.by. '
        f'Я буду уведомлять вас о новых закупках.')


# Функция для обработки команды /parse
async def parse(message: types.Message) -> None:
    if message.from_user.id in get_users():
        log.info(f'Пользователь `{message.from_user.first_name}` /parse')
        old_data = load_data()
        new_data = await parse_url(conf.general.url)
        new_entries = _compare_data(new_data, old_data)

        if new_entries:
            save_data(new_data)
            await message.answer('Найдены новые данные.')
            for key, value in list(new_entries.items()):
                formatted_message = ""
                for k, v in value.items():
                    formatted_message += f"{k}: {v}\n"
                await message.answer(formatted_message)
        else:
            await message.answer('Новых данных не найдено.')
    else:
        log.warning(f'Неизвестный пользователь `{message.from_user.first_name}` пытается выполнить команду /parse')
        await message.answer('Вы не подписаны на рассылку.')


# Функция для сравнения новых данных с прошлыми
def _compare_data(new_data, old_data):
    new_entries = {}
    for key, value in new_data.items():
        if key not in old_data:
            new_entries[key] = value
    return new_entries


async def scheduled_parse(bot) -> None:
    try:
        log.info("Автоматическая проверка на наличие новых данных ...")
        old_data = load_data()
        new_data = await parse_url(conf.general.url)
        new_entries = _compare_data(new_data, old_data)

        if new_entries:
            save_data(new_data)
            log.info(f"Найдено {len(new_entries)} новых записей")
            for key, value in list(new_entries.items()):
                formatted_message = ""
                for k, v in value.items():
                    formatted_message += f"{k}: {v}\n"
                users = get_users()
                log.info(f"Отправка {len(users)} пользователям")
                for user_id in users:
                    await bot.send_message(chat_id=user_id, text=formatted_message)
        else:
            log.info("Новых записей не найдено")
    except Exception as e:
        log.error(f"Ошибка в scheduled_parse: {e}", exc_info=True)


# Регистрируем хендлеры с использованием фильтров
dp.message.register(start, Command("start"))
dp.message.register(parse, Command("parse"))
