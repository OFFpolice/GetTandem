from data.data import *
from public.method import *
from views.admin import *


def _collect_msg_ids(message: Message):
    ids = [message.message_id]
    if message.reply_to_message:
        ids.append(message.reply_to_message.message_id)
        if message.reply_to_message.reply_to_message:
            ids.append(message.reply_to_message.reply_to_message.message_id)
    return [x for x in ids if x]


async def _safe_delete(bot: Bot, chat_id: int, msg_ids: list):
    if not msg_ids:
        return
    try:
        await bot.delete_messages(chat_id=chat_id, message_ids=msg_ids)
    except TelegramAPIError as e:
        logging.debug(f"Ошибка удаления сообщений: {e}")


# Изменение конфигурации
async def admin_config_reply_input(message: Message, bot: Bot):
    user = await UserAuth(Msg=message).auth(FromUser=message.from_user)
    if user and user[5] in [1, 2]:
        reply_text = (message.reply_to_message.text or "").split(':')
        config = ConfigData()
        admin = Admin(Client=bot, Msg=message)
        msg_id = _collect_msg_ids(message)
        if not message.text:
            return await msgNotify(msg=message, text='Пожалуйста, отправьте текстовое сообщение')
        if "Введите ID админ-группы" in reply_text[0]:
            if await config.put_config(comm=message.text, name='adminGroup'):
                await get_config()
                await msgNotify(msg=message, text='Админ-группа успешно изменена')
                await _safe_delete(bot, message.chat.id, msg_id)
            else:
                await msgNotify(msg=message, text='Не удалось изменить админ-группу')
            await admin.config()
        elif "Введите ID группы уведомлений" in reply_text[0]:
            if await config.put_config(comm=message.text, name='msgGroup'):
                await get_config()
                await msgNotify(msg=message, text='Группа уведомлений успешно изменена')
                await _safe_delete(bot, message.chat.id, msg_id)
            else:
                await msgNotify(msg=message, text='Не удалось изменить группу уведомлений')
            await admin.config()
        elif "Введите лимит запросов" in reply_text[0]:
            if message.text and message.text.strip().isdigit() and await config.put_config(
                comm=message.text.strip(), name='restrict_limit'
            ):
                await get_config()
                await msgNotify(msg=message, text='Лимит запросов успешно изменён')
                await _safe_delete(bot, message.chat.id, msg_id)
            else:
                await msgNotify(msg=message, text='Не удалось изменить лимит запросов: введите число')
            await admin.config()
        elif "Введите причину отказа" in reply_text[0]:
            if await config.post_rejectText(text=message.text):
                await get_config()
                await msgNotify(msg=message, text='Причина отказа успешно добавлена')
                await _safe_delete(bot, message.chat.id, msg_id)
            else:
                await msgNotify(msg=message, text='Не удалось добавить причину отказа')
            await admin.reviewRejectionWords()
        elif "Введите новую причину отказа" in reply_text[0]:
            if await config.put_rejectText(id=reply_text[1], text=message.text):
                await get_config()
                await msgNotify(msg=message, text='Причина отказа успешно изменена')
                await _safe_delete(bot, message.chat.id, msg_id)
            else:
                await msgNotify(msg=message, text='Не удалось изменить причину отказа')
            await admin.reviewRejectionWords()
    else:
        await message.answer("⚠️ Недостаточно прав, требуются права администратора")


async def admin_advertising_input(message: Message, bot: Bot):
    user = await UserAuth(Msg=message).auth(FromUser=message.from_user)
    if user and user[5] in [1, 2]:
        if not message.text:
            return await msgNotify(msg=message, text='Пожалуйста, отправьте текстовое сообщение')
        reply_text = (message.reply_to_message.text or "").split(':')
        adData = AdvertisingData()
        advertising = Advertising(Client=bot, Msg=message)
        msg_id = _collect_msg_ids(message)
        if "Введите рекламу" in reply_text[0]:
            text = message.text.split('&')
            if len(text) > 1:
                if await adData.post_advertising(titel=text[0], url=text[1]):
                    await msgNotify(msg=message, text='Реклама успешно добавлена')
                    await _safe_delete(bot, message.chat.id, msg_id)
                else:
                    await msgNotify(msg=message, text='Не удалось добавить рекламу')
                await advertising.index()
            else:
                await msgNotify(msg=message, text='Неверный формат: используйте Заголовок&Ссылка')
        elif "Введите новую рекламу" in reply_text[0]:
            text = message.text.split('&')
            if len(text) > 1:
                if await adData.put_advertising(id=reply_text[1], titel=text[0], url=text[1]):
                    await msgNotify(msg=message, text='Реклама успешно изменена')
                    await _safe_delete(bot, message.chat.id, msg_id)
                else:
                    await msgNotify(msg=message, text='Не удалось изменить рекламу')
                await advertising.index()
            else:
                await msgNotify(msg=message, text='Неверный формат: используйте Заголовок&Ссылка')
    else:
        await message.answer("⚠️ Недостаточно прав, требуются права администратора")


async def admin_car_input(message: Message, bot: Bot):
    user = await UserAuth(Msg=message).auth(FromUser=message.from_user)
    if user and user[5] in [1, 2]:
        if not message.text:
            return await msgNotify(msg=message, text='Пожалуйста, отправьте текстовое сообщение')
        reply_text = (message.reply_to_message.text or "").split(':')
        carData = CarData()
        car = Car(Client=bot, Msg=message)
        msg_id = _collect_msg_ids(message)
        if "Введите название подборки каналов" in reply_text[0]:
            if await carData.post_car(car_title=message.text, car_type=0):
                await msgNotify(msg=message, text='Подборка каналов успешно добавлена')
                await _safe_delete(bot, message.chat.id, msg_id)
            else:
                await msgNotify(msg=message, text='Не удалось добавить подборку каналов')
            await car.channel_car()
        elif "Введите новое название подборки" in reply_text[0]:
            if await carData.put_car_titel(text=message.text, id=reply_text[1]):
                await msgNotify(msg=message, text='Название подборки успешно изменено')
                await _safe_delete(bot, message.chat.id, msg_id)
            else:
                await msgNotify(msg=message, text='Не удалось изменить название подборки')
            await car.channel_fleet_info(fleet=[reply_text[1]])
        elif "Введите новое описание подборки" in reply_text[0]:
            if await carData.put_car_introduce(text=message.text, id=reply_text[1]):
                await msgNotify(msg=message, text='Описание подборки успешно изменено')
                await _safe_delete(bot, message.chat.id, msg_id)
            else:
                await msgNotify(msg=message, text='Не удалось изменить описание подборки')
            await car.channel_fleet_info(fleet=[reply_text[1]])
        elif "Введите макс. число участников" in reply_text[0]:
            if message.text and message.text.strip().isdigit() and await carData.put_car_total(
                text=int(message.text.strip()), id=reply_text[1]
            ):
                await msgNotify(msg=message, text='Макс. число участников успешно изменено')
                await _safe_delete(bot, message.chat.id, msg_id)
            else:
                await msgNotify(msg=message, text='Не удалось изменить макс. число участников: введите целое число')
            await car.channel_fleet_info(fleet=[reply_text[1]])
        elif "Введите мин. число подписчиков" in reply_text[0]:
            if message.text and message.text.strip().isdigit() and await carData.put_car_mi_memberl(
                text=int(message.text.strip()), id=reply_text[1]
            ):
                await msgNotify(msg=message, text='Мин. число подписчиков успешно изменено')
                await _safe_delete(bot, message.chat.id, msg_id)
            else:
                await msgNotify(msg=message, text='Не удалось изменить мин. число подписчиков: введите целое число')
            await car.channel_fleet_info(fleet=[reply_text[1]])
        elif "Введите мин. число просмотров" in reply_text[0]:
            if message.text and message.text.strip().isdigit() and await carData.put_car_mi_mi_read(
                text=int(message.text.strip()), id=reply_text[1]
            ):
                await msgNotify(msg=message, text='Мин. число просмотров успешно изменено')
                await _safe_delete(bot, message.chat.id, msg_id)
            else:
                await msgNotify(msg=message, text='Не удалось изменить мин. число просмотров: введите целое число')
            await car.channel_fleet_info(fleet=[reply_text[1]])
    else:
        await message.answer("⚠️ Недостаточно прав, требуются права администратора")


async def admin_car_group_input(message: Message, bot: Bot):
    user = await UserAuth(Msg=message).auth(FromUser=message.from_user) if message.from_user else None
    if (user and user[5] in [1, 2]) or message.chat.id == safe_int(bot_config.get("adminGroup"), None):
        if not message.text:
            return await msgNotify(msg=message, text='Пожалуйста, отправьте текстовую причину отказа')
        reply_text = (message.reply_to_message.text or "").split(':')
        review = Review(Client=bot, Msg=message)
        if "Введите свою причину отказа" in reply_text[0]:
            await _safe_delete(bot, message.chat.id, [message.message_id, message.reply_to_message.message_id])
            await review.rejectReason(group=[reply_text[1]], reason=[message.text])
    else:
        await message.answer("⚠️ Недостаточно прав, требуется админ-группа")


async def admin_group_input(message: Message, bot: Bot):
    user = await UserAuth(Msg=message).auth(FromUser=message.from_user)
    if user and user[5] in [1, 2]:
        if not message.text:
            return await msgNotify(msg=message, text='Пожалуйста, отправьте текстовое сообщение')
        reply_text = (message.reply_to_message.text or "").split(':')
        group = Group(Client=bot, Msg=message)
        msg_id = _collect_msg_ids(message)
        if "Введите название канала" in reply_text[0]:
            await _safe_delete(bot, message.chat.id, msg_id)
            await group.index(search=message.text)
    else:
        await message.answer("⚠️ Недостаточно прав, требуются права администратора")


async def admin_user_input(message: Message, bot: Bot):
    user = await UserAuth(Msg=message).auth(FromUser=message.from_user)
    if user and user[5] in [1, 2]:
        if not message.text:
            return await msgNotify(msg=message, text='Пожалуйста, отправьте текстовое сообщение')
        reply_text = (message.reply_to_message.text or "").split(':')
        user_view = User(Client=bot, Msg=message)
        msg_id = _collect_msg_ids(message)
        if "Введите юзернейм или имя" in reply_text[0]:
            await _safe_delete(bot, message.chat.id, msg_id)
            await user_view.getUser(search=message.text)
    else:
        await message.answer("⚠️ Недостаточно прав, требуются права администратора")


async def admin_bot_blacklist_input(message: Message, bot: Bot):
    user = await UserAuth(Msg=message).auth(FromUser=message.from_user)
    if user and user[5] in [1, 2]:
        if not message.text:
            return await msgNotify(msg=message, text='Пожалуйста, отправьте текстовое сообщение')
        reply_text = (message.reply_to_message.text or "").split(':')
        blacklist_date = BotBlacklistDate()
        blacklist = BotBlacklist(Client=bot, Msg=message)
        msg_id = _collect_msg_ids(message)
        if "Введите юзернейм бота" in reply_text[0]:
            if "@" in message.text:
                if await blacklist_date.post_bot_blacklist(titel=message.text):
                    await msgNotify(msg=message, text='Бот добавлен в чёрный список')
                else:
                    await msgNotify(msg=message, text='Не удалось добавить бота в чёрный список')
                await _safe_delete(bot, message.chat.id, msg_id)
                await blacklist.index()
            else:
                await msgNotify(msg=message, text='Неверный формат: используйте @username_bot')
        elif "Введите новый юзернейм бота" in reply_text[0]:
            if "@" in message.text:
                if await blacklist_date.put_bot_blacklist(id=reply_text[1], titel=message.text):
                    await msgNotify(msg=message, text='Запись чёрного списка успешно изменена')
                    await _safe_delete(bot, message.chat.id, msg_id)
                else:
                    await msgNotify(msg=message, text='Не удалось изменить запись чёрного списка')
                await blacklist.index()
            else:
                await msgNotify(msg=message, text='Неверный формат: используйте @username_bot')
    else:
        await message.answer("⚠️ Недостаточно прав, требуются права администратора")