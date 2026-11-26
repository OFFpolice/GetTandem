import importlib.util
import logging
import subprocess
import sys


def _ensure_dependencies():
    required = ("aiogram", "dotenv", "aiosqlite", "apscheduler", "emoji", "redis", "uvloop", "asyncpg")
    if all(importlib.util.find_spec(pkg) is not None for pkg in required):
        return
    if importlib.util.find_spec("pip") is None:
        import os
        import urllib.request

        tmp_pip = "/tmp/get-pip.py"
        urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", tmp_pip)
        try:
            subprocess.run([sys.executable, tmp_pip, "--break-system-packages"], check=True)
        finally:
            if os.path.exists(tmp_pip):
                os.remove(tmp_pip)
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--break-system-packages", "-q", "-r", "requirements.txt"],
        check=True,
    )


_ensure_dependencies()

from config import *
from monitor.command import *
from monitor.input import *


def register_handlers(dispatcher: Dispatcher):
    '''Регистрация обработчиков aiogram 3'''
    # Команда запуска или главная страница
    dispatcher.message.register(
        start_handler,
        Command("start"),
        F.chat.type == ChatType.PRIVATE,
    )
    # Команда инструкции /help
    dispatcher.message.register(
        help_handler,
        Command("help"),
        F.chat.type == ChatType.PRIVATE,
    )
    # Команда вызова панели администратора
    dispatcher.message.register(
        admii_command,
        F.chat.type == ChatType.PRIVATE,
        Command("admin"),
    )
    # Заглушка для неактивных кнопок
    dispatcher.callback_query.register(noop_callback_handler, F.data == "-")
    # Маршруты обычных пользователей
    dispatcher.callback_query.register(callback_query_router, F.data.startswith("r/"))
    # Маршруты администратора
    dispatcher.callback_query.register(admin_callback_query_router, F.data.startswith("a/"))
    # Обновление статуса бота в каналах
    dispatcher.my_chat_member.register(handle_chat_member_update)

    # Обработчик ввода ответа на настройку бота
    dispatcher.message.register(
        admin_config_reply_input,
        F.chat.type == ChatType.PRIVATE,
        F.reply_to_message.text.startswith("📲"),
    )
    # Обработчик ввода управления рекламой
    dispatcher.message.register(
        admin_advertising_input,
        F.chat.type == ChatType.PRIVATE,
        F.reply_to_message.text.startswith("🗞️"),
    )
    # Обработчик ввода управления подборками
    dispatcher.message.register(
        admin_car_input,
        F.chat.type == ChatType.PRIVATE,
        F.reply_to_message.text.startswith("🚒"),
    )
    # Обработчик ввода своей причины отказа (админ-группа или ЛС админа)
    dispatcher.message.register(
        admin_car_group_input,
        F.reply_to_message.text.startswith("💭"),
    )
    # Обработчик ввода управления каналами
    dispatcher.message.register(
        admin_group_input,
        F.chat.type == ChatType.PRIVATE,
        F.reply_to_message.text.startswith("🏵️"),
    )
    # Обработчик ввода чёрного списка ботов
    dispatcher.message.register(
        admin_bot_blacklist_input,
        F.chat.type == ChatType.PRIVATE,
        F.reply_to_message.text.startswith("🤖"),
    )
    # Обработчик ввода управления пользователями
    dispatcher.message.register(
        admin_user_input,
        F.chat.type == ChatType.PRIVATE,
        F.reply_to_message.text.startswith("👨‍💻"),
    )


async def init_startup():
    await db.init_db()
    return await get_config()


async def main():
    global bot_config
    logging.critical('Успешный запуск (aiogram 3)')
    bot_config = await init_startup()
    logging.critical(f"Загружен файл конфигурации: {bot_config}")
    scheduler.start()
    schedulerObj = scheduler.add_job(convoyDriving, "interval", seconds=60 * 30, misfire_grace_time=60)
    logging.critical(f"Время выполнения планировщика: {schedulerObj}")
    register_handlers(dp)
    await bot.delete_webhook(drop_pending_updates=False)
    await sync_bot_commands(bot)
    try:
        await dp.start_polling(bot)
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)
        await db.close()
        await bot.session.close()


if __name__ == '__main__':
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", 47209))
    except socket.error:
        print('Бот уже запущен')
    else:
        try:
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            logging.info("Бот остановлен")
        except Exception as e:
            logging.error(f"Критическая ошибка запуска: {e}")
