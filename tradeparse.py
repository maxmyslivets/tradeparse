import os

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import conf
from bot.commands import command_start, command_parse, scheduled_parse
from logger import log


if __name__ == '__main__':

    log.info("Бот запущен!")

    token = os.getenv(conf.env.env_token)

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", command_start))
    application.add_handler(CommandHandler("parse", command_parse))

    # Планировщик для периодического запуска метода `scheduled_parse` экземпляра класса `application`
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_parse, 'interval', minutes=conf.general.interval, args=[application])
    scheduler.start()

    application.run_polling()
