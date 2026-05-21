import asyncio
import logging
import ssl

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def parse(url: str) -> dict:
    """
    Асинхронный парсинг сайта и извлечение данных из таблицы
    :param url:
    :return:
    """
    logger.info(f"Начало парсинга URL: {url}")

    # Создание SSL-контекста без проверки сертификатов
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    timeout = aiohttp.ClientTimeout(total=30)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, ssl=ssl_context) as response:
                response_text = await response.text()
                logger.info(f"Получен ответ, размер: {len(response_text)} байт")
    except aiohttp.ClientTimeout:
        logger.error(f"Таймаут при запросе к {url}")
        raise
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка клиента при запросе к {url}: {e}")
        raise

    # Выносим парсинг из event loop, чтобы не блокировать его
    soup = await asyncio.to_thread(BeautifulSoup, response_text, 'html.parser')
    logger.info("HTML распарсен")

    auctions_list = soup.find('table', id='auctions-list')
    data = {}

    if auctions_list:
        headers = [th.text.strip() for th in auctions_list.find_all('th')]
        rows = auctions_list.find_all('tr')[1:]  # Пропускаем заголовок таблицы

        for row in rows:
            columns = row.find_all('td')
            if columns:
                row_data = {headers[i]: columns[i].text.strip() for i in range(len(columns))}
                row_data['Источник'] = row.a['href']
                data[row_data[headers[3]]] = row_data  # Используем номер закупки как ключ

    logger.info(f"Парсинг завершён, найдено записей: {len(data)}")
    return data
