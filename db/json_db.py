import json

from config import conf


# Функция для сохранения данных в файл
def save_data(data, filepath=conf.db.json_db_path):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Функция для загрузки данных из файла
def load_data(filepath=conf.db.json_db_path):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
