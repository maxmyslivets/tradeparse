import aiohttp
import asyncio
import ssl
import json
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Глобальная переменная для хранения новых данных и списка пользователей
latest_new_data = {}
subscribed_users = set()


# Функция для асинхронного парсинга сайта и извлечения данных из таблицы
async def parse_site():
    url = "https://icetrade.by/search/auctions?search_text=%D0%B3%D0%B5%D0%BE%D0%B4&zakup_type%5B1%5D=1&zakup_type%5B2%5D=1&auc_num=&okrb=&company_title=&establishment=0&industries=&period=&created_from=&created_to=&request_end_from=&request_end_to=&t%5BTrade%5D=1&t%5BeTrade%5D=1&t%5BsocialOrder%5D=1&t%5BsingleSource%5D=1&t%5BAuction%5D=1&t%5BRequest%5D=1&t%5BcontractingTrades%5D=1&t%5Bnegotiations%5D=1&t%5BOther%5D=1&r%5B1%5D=1&r%5B2%5D=2&r%5B7%5D=7&r%5B3%5D=3&r%5B4%5D=4&r%5B6%5D=6&r%5B5%5D=5&sort=num%3Adesc&sbm=1&onPage=100"

    # Создание SSL-контекста без проверки сертификатов
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=ssl_context) as response:
            response_text = await response.text()
            soup = BeautifulSoup(response_text, 'html.parser')

            auctions_list = soup.find('table', id='auctions-list')
            data = {}

            if auctions_list:
                headers = [th.text.strip() for th in auctions_list.find_all('th')]
                rows = auctions_list.find_all('tr')[1:]  # Пропускаем заголовок таблицы

                for row in rows:
                    columns = row.find_all('td')
                    if columns:
                        row_data = {headers[i]: columns[i].text.strip() for i in range(len(columns))}
                        data[row_data[headers[0]]] = row_data  # Используем первое поле как ключ

            return data


# Функция для сохранения данных в файл
def save_data(data, filename='previous_data.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Функция для загрузки данных из файла
def load_data(filename='previous_data.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# Функция для сравнения новых данных с прошлыми
def compare_data(new_data, old_data):
    # FIXME Сравнивать не ключ, а все данные, в частности Номер
    new_entries = {}
    for key, value in new_data.items():
        if key not in old_data:
            new_entries[key] = value
    return new_entries


# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    subscribed_users.add(user_id)
    await update.message.reply_text(
        'Привет! Я бот для парсинга сайта https://icetrade.by. Я буду уведомлять вас о новых данных.')


# Функция для обработки команды /parse
async def parse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    old_data = load_data()
    new_data = await parse_site()
    new_entries = compare_data(new_data, old_data)

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


async def scheduled_parse(application: Application) -> None:
    try:
        old_data = load_data()
        new_data = await parse_site()
        new_entries = compare_data(new_data, old_data)

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


def main():
    # Загрузка токена из файла конфигурации
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    token = config['token']

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("parse", parse))

    # Добавляем обработчик ошибок
    application.add_handler(MessageHandler(filters.ALL, error_handler))

    # Планировщик для периодического парсинга сайта
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_parse, 'interval', minutes=5, args=[application])  # Установите нужный интервал
    scheduler.start()

    application.run_polling()


if __name__ == '__main__':
    main()
