#!/bin/bash
# entrypoint.sh - Инициализация файлов данных при первом запуске контейнера

DATA_DIR="/app/data"

# Создаём директории если не существуют
mkdir -p "$DATA_DIR"

# Создаём пустые файлы если не существуют
touch "$DATA_DIR/users.txt"
touch "$DATA_DIR/previous_data.json"
touch "$DATA_DIR/errors.log"

# Запускаем основную команду
exec "$@"
