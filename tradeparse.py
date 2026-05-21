import asyncio
import sys

from aiogram import Bot

from config import conf
from bot.commands import dp, scheduled_parse
from logger import log


async def scheduler_loop(bot):
    """Асинхронный циклический планировщик на основе asyncio."""
    interval = conf.general.interval * 60  # конвертируем минуты в секунды
    while True:
        await asyncio.sleep(interval)
        await scheduled_parse(bot)


async def main():
    log.info("Бот запущен!")
    token = conf.env.env_token

    bot = Bot(token=token)

    # Запускаем планировщик как фоновую задачу
    log.info(f"Планировщик настроен, интервал: {conf.general.interval} мин")
    asyncio.create_task(scheduler_loop(bot))
    log.info("Планировщик запущен")

    log.info("Запуск polling...")
    await dp.start_polling(bot)
    log.info("Polling запущен")

    log.info("Бот остановлен")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Бот остановлен пользователем (KeyboardInterrupt)")
    except Exception as e:
        log.error(f"Критическая ошибка: {e}", exc_info=True)
