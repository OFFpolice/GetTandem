import logging

from router import router
from views.client import *
from views.admin import *


async def start_handler(message: Message, bot: Bot):
    '''Обработчик команды запуска пользователя'''
    if await RestrictAccess(Msg=message).limit_check():
        user = await UserAuth(Msg=message).auth(FromUser=message.from_user)
        if user:
            if user[5] in [1, 2]:
                await sync_user_commands(bot, message.from_user.id, is_admin=True)
            try:
                index = Index(Client=bot, Msg=message, Data={'user': user})
                await index.index()
            except (TelegramAPIError, Exception) as e:
                logging.error(f"Ошибка команды пользователя: {e}")


async def help_handler(message: Message, bot: Bot):
    '''Обработчик команды /help'''
    if await RestrictAccess(Msg=message).limit_check():
        user = await UserAuth(Msg=message).auth(FromUser=message.from_user)
        if user:
            if user[5] in [1, 2]:
                await sync_user_commands(bot, message.from_user.id, is_admin=True)
            try:
                index = Index(Client=bot, Msg=message, Data={'user': user})
                await index.instruction()
            except (TelegramAPIError, Exception) as e:
                logging.error(f"Ошибка команды /help: {e}")


async def noop_callback_handler(query: CallbackQuery):
    await query.answer()


async def callback_query_router(query: CallbackQuery, bot: Bot):
    # Маршрутизация при нажатии на кнопку
    if await RestrictAccess(Msg=query.message).limit_check():
        user = await UserAuth(Msg=query.message).auth(FromUser=query.from_user)
        if user:
            try:
                logging.info(query.data)
                await router.route(query.data, bot, query, Data={'user': user})
            except ValueError as E:
                logging.error(f'Ошибка обычного маршрута: {E}')
                await query.answer(text=f'Ошибка: {E}', show_alert=True)


async def admin_callback_query_router(query: CallbackQuery, bot: Bot):
    # Маршрутизация при нажатии на кнопку администратора
    user = await UserAuth(Msg=query.message).auth(FromUser=query.from_user)
    if (user and user[5] in [1, 2]) or (
        query.message and query.message.chat.id == safe_int(bot_config.get("adminGroup"), None)
    ):
        try:
            logging.info(query.data)
            await router.route(query.data, bot, query, Data={'user': user})
        except ValueError as E:
            logging.error(f'Ошибка админ-маршрута: {E}')
            await query.answer(text=f'Ошибка: {E}', show_alert=True)
    else:
        if query.message:
            await query.message.answer("⚠️ Недостаточно прав, требуются права администратора")
        else:
            await query.answer("⚠️ Недостаточно прав, требуются права администратора", show_alert=True)


async def admii_command(message: Message, bot: Bot):
    # Вход в панель администратора
    user = await UserAuth(Msg=message).auth(FromUser=message.from_user)
    if user and user[5] in [1, 2]:
        try:
            admin = Admin(Client=bot, Msg=message, Data={'user': user})
            await admin.index()
        except (TelegramAPIError, Exception) as e:
            logging.error(f"Ошибка панели администратора: {e}")
    else:
        await message.answer("⚠️ Недостаточно прав, требуются права администратора")


# Мониторинг статуса бота в каналах (my_chat_member)
async def handle_chat_member_update(update: ChatMemberUpdated, bot: Bot):
    if update.chat.type != ChatType.CHANNEL:
        return
    new_m = update.new_chat_member
    old_m = update.old_chat_member
    chat_title = update.chat.title or 'Канал'
    chat_fallback_url = f"https://t.me/{update.chat.username}" if update.chat.username else ""

    if new_m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER):
        if not update.from_user:
            return
        user = await ChatUser().get_or_create(update.from_user)
        if user:
            user_peer = to_peer_id(user[1])
            if user[4] == 0:
                try:
                    if new_m.status == ChatMemberStatus.ADMINISTRATOR:
                        group = await bot.get_chat(update.chat.id)
                        try:
                            members_count = await bot.get_chat_member_count(update.chat.id)
                        except TelegramAPIError:
                            members_count = 0
                        isPrivi = await isPrivileges(chatId=update.chat.id, typeG='CHANNEL')
                        ch_url = group.invite_link or chat_fallback_url
                        if not ch_url and isPrivi == 0:
                            try:
                                ch_url = await bot.export_chat_invite_link(update.chat.id)
                            except TelegramAPIError:
                                ch_url = ""
                        ch_link = html_link(chat_title, ch_url)
                        if isPrivi == 1:
                            text = (
                                f"В «{ch_link}» "
                                "у бота недостаточно прав, канал будет снят с подборки, проверьте настройки"
                            )
                            await db.update("UPDATE group_list SET state=0 WHERE group_id=?", (str(update.chat.id),))
                            return await bot.send_message(
                                chat_id=user_peer,
                                text=text,
                                link_preview_options=LinkPreviewOptions(is_disabled=True),
                            )
                        groupIs = await db.select("SELECT * FROM group_list WHERE group_id=?", (str(update.chat.id),))
                        is_new_channel = False
                        if not groupIs:
                            is_new_channel = True
                            text = f"«{ch_link}» успешно добавлен, проверка прав пройдена"
                            await db.insert(
                                "INSERT INTO group_list (group_id,username,title,type,total_people,url,chat_id) VALUES(?,?,?,?,?,?,?)",
                                (
                                    str(group.id),
                                    group.username or "",
                                    group.title or chat_title,
                                    "CHANNEL",
                                    members_count or 0,
                                    ch_url,
                                    user[0],
                                ),
                            )
                            groupIs = await db.select("SELECT * FROM group_list WHERE group_id=?", (str(update.chat.id),))
                        else:
                            if groupIs[0][10] == 10:
                                ch_link_u = html_link(chat_title, chat_fallback_url)
                                text = (
                                    f"«{ch_link_u}» — "
                                    "ваш канал заблокирован, обратитесь к администратору"
                                )
                                return await bot.send_message(
                                    chat_id=user_peer,
                                    text=text,
                                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                                )
                            await db.update(
                                "UPDATE group_list SET title=?,total_people=?,url=?,chat_id=? WHERE group_id=?",
                                (
                                    group.title or chat_title,
                                    members_count or 0,
                                    ch_url,
                                    user[0],
                                    str(update.chat.id),
                                ),
                            )
                            ch_link_g = html_link(group.title or chat_title, ch_url)
                            text = f"«{ch_link_g}» уже существует, данные обновлены!"
                            groupIs = await db.select("SELECT * FROM group_list WHERE group_id=?", (str(update.chat.id),))

                        await bot.send_message(
                            chat_id=user_peer,
                            text=text,
                            link_preview_options=LinkPreviewOptions(is_disabled=True),
                        )

                        if groupIs:
                            g_row = groupIs[0]
                            await CarData().post_notify_msg(
                                group=g_row,
                                label="Новый канал добавлен в бот" if is_new_channel else "Канал обновлён",
                            )
                            applicant = (
                                html_link(user[3], f"https://t.me/{user[2]}")
                                if user[2] and user[2] != 'Нет'
                                else esc(user[3])
                            )
                            admin_header = (
                                "<b>📣 Добавлен новый канал</b>"
                                if is_new_channel
                                else "<b>📣 Канал обновлён в боте</b>"
                            )
                            admin_text = (
                                f"{admin_header}\n\n"
                                f"<b>ID канала:</b> <code>{esc(g_row[1])}</code>\n"
                                f"<b>Канал:</b> {html_link(g_row[3], g_row[6])}\n"
                                f"<b>Подписчиков:</b> {g_row[5]}\n"
                                f"<b>ID владельца:</b> <code>{esc(user[1])}</code>\n"
                                f"<b>Владелец:</b> {applicant}\n"
                                f"<b>Статус:</b> ⚪ Ожидает решения администратора"
                            )
                            admin_kb = InlineKeyboardMarkup(inline_keyboard=[
                                [
                                    InlineKeyboardButton(
                                        text="➕ Добавить",
                                        callback_data=f"a/pick_fleet?group={g_row[0]}",
                                    ),
                                    InlineKeyboardButton(
                                        text="❌ Отклонить",
                                        callback_data=f"a/review_reject?group={g_row[0]}",
                                    ),
                                ],
                                [
                                    InlineKeyboardButton(
                                        text="🚫 Заблокировать",
                                        callback_data=f"a/review_ban?group={g_row[0]}",
                                    )
                                ],
                            ])
                            await notify_admins(bot, text=admin_text, reply_markup=admin_kb)
                    elif new_m.status == ChatMemberStatus.MEMBER:
                        ch_link_u = html_link(chat_title, chat_fallback_url)
                        text = (
                            f"В «{ch_link_u}» "
                            "не обнаружены права администратора, канал будет снят с подборки, проверьте!"
                        )
                        await db.update(
                            "UPDATE group_list SET state=0,label='Права администратора не обнаружены' WHERE group_id=?",
                            (str(update.chat.id),),
                        )
                        return await bot.send_message(
                            chat_id=user_peer,
                            text=text,
                            link_preview_options=LinkPreviewOptions(is_disabled=True),
                        )
                except TelegramAPIError as e:
                    logging.error(f"Ошибка обработки обновления канала {update.chat.id}: {e}")
            else:
                try:
                    return await bot.send_message(
                        chat_id=update.from_user.id,
                        text="Ваш аккаунт заблокирован, обратитесь к администратору",
                    )
                except TelegramAPIError as e:
                    logging.error(f"Ошибка отправки уведомления о блокировке: {e}")
    elif new_m.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED) and old_m.status in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.RESTRICTED,
    ):
        group = await db.select("SELECT * FROM group_list WHERE group_id=?", (str(update.chat.id),))
        if group:
            target_id = None
            if update.from_user:
                target_id = update.from_user.id
            else:
                owner = await db.select("SELECT chat_id FROM chat_user WHERE id=?", (group[0][12],))
                if owner:
                    target_id = to_peer_id(owner[0][0])
            ch_link_u = html_link(chat_title, chat_fallback_url)
            if group[0][10] == 10:
                text = (
                    f"«{ch_link_u}» — "
                    "ваш канал заблокирован, обратитесь к администратору"
                )
            else:
                await db.update("UPDATE group_list SET state=0 WHERE group_id=?", (str(update.chat.id),))
                text = (
                    f"«{ch_link_u}» — "
                    "бот вышел из канала, канал будет снят с подборки, проверьте!"
                )
            if target_id:
                try:
                    return await bot.send_message(
                        chat_id=target_id,
                        text=text,
                        link_preview_options=LinkPreviewOptions(is_disabled=True),
                    )
                except TelegramAPIError as e:
                    logging.error(f"Ошибка отправки уведомления о выходе из канала: {e}")
