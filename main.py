import logging

from pyrogram.handlers import *
from monitor.command import *
from monitor.input import *
from config import *


def command(client: Client):
    '''Команда запуска или главная страница'''
    client.add_handler(MessageHandler(start_handler, filters.command(["start", "index"]) & filters.private))
    # Команда вызова панели администратора
    client.add_handler(
        MessageHandler(admii_command, filters.private & (filters.command("admin") | filters.regex("⚙Админ-панель"))))
    # Маршруты обычных пользователей
    client.add_handler(CallbackQueryHandler(callback_query_router, filters.create(
        lambda _, __, query: (query.data and query.data.startswith("r/")))))
    # Маршруты администратора
    client.add_handler(CallbackQueryHandler(admin_callback_query_router, filters.create(
        lambda _, __, query: (query.data and query.data.startswith("a/")))))
    # Обновление статуса участника в чате/канале
    client.add_handler(ChatMemberUpdatedHandler(handle_chat_member_update))
    # # Мониторинг удалённых сообщений пользователя
    # client.add_handler(DeletedMessagesHandler(delete_message))
    # # Пользователь изменил сообщение
    # client.add_handler(EditedMessageHandler(edited_message))
    # Обработчик ввода ответа на настройку бота
    client.add_handler(MessageHandler(admin_config_reply_input, filters.private & filters.reply & filters.create(
        lambda _, __, query: (
                query.reply_to_message.text and query.reply_to_message.text.startswith("📲")
        )
    )))
    # Обработчик ввода управления рекламой
    client.add_handler(MessageHandler(admin_advertising_input, filters.private & filters.reply & filters.create(
        lambda _, __, query: (
                query.reply_to_message.text and query.reply_to_message.text.startswith("🗞️")
        )
    )))
    # Обработчик ввода управления подборками
    client.add_handler(MessageHandler(admin_car_input, filters.private & filters.reply & filters.create(
        lambda _, __, query: (
                query.reply_to_message.text and query.reply_to_message.text.startswith("🚒")
        )
    )))
    # Обработчик ввода управления подборками в админ-группе
    client.add_handler(MessageHandler(admin_car_group_input, filters.group & filters.reply & filters.create(
        lambda _, __, query: (
                query.reply_to_message.text and query.reply_to_message.text.startswith("💭")
        )
    )))
    # Обработчик ввода управления группами и каналами
    client.add_handler(MessageHandler(admin_group_input, filters.private & filters.reply & filters.create(
        lambda _, __, query: (
                query.reply_to_message.text and query.reply_to_message.text.startswith("🏵️")
        )
    )))
    # Обработчик ввода чёрного списка ботов
    client.add_handler(MessageHandler(admin_bot_blacklist_input, filters.private & filters.reply & filters.create(
        lambda _, __, query: (
                query.reply_to_message.text and query.reply_to_message.text.startswith("🤖")
        )
    )))
    # Обработчик ввода управления пользователями
    client.add_handler(MessageHandler(admin_user_input, filters.private & filters.reply & filters.create(
        lambda _, __, query: (
                query.reply_to_message.text and query.reply_to_message.text.startswith("👨‍💻")
        )
    )))


async def init_startup():
    await db.init_db()
    return await get_config()


if __name__ == '__main__':
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 47209))
    except socket.error:
        print('Бот уже запущен')
    else:
        try:
            logging.critical('Успешный запуск')
            bot_config = app.loop.run_until_complete(init_startup())
            logging.critical(f"Загружен файл конфигурации: {bot_config}")
            scheduler.start()
            schedulerObj = scheduler.add_job(convoyDriving, "interval", seconds=60 * 30, misfire_grace_time=60)
            logging.critical(f"Время выполнения планировщика: {schedulerObj}")
            command(app)
            app.run()
        except Exception as e:
            logging.error(e)
