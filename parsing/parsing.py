import aiohttp
import ssl
from bs4 import BeautifulSoup


async def parse(url: str) -> dict:
    """
    Асинхронный парсинг сайта и извлечение данных из таблицы
    :param url:
    :return:
    """

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
                        row_data['Источник'] = row.a['href']
                        data[row_data[headers[3]]] = row_data  # Используем номер закупки как ключ

            return data
