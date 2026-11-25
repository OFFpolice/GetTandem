import logging
from config import *
from data.data import db
from public.method import isPrivileges as HavePermission, truncate_string, format_tg_url, to_peer_id, html_link, esc

# ====== Модуль отправки сообщений и рассылки подборок (aiogram 3) ======


async def checkPrivileges(chatId):
    # Проверка прав
    try:
        groupType = await bot.get_chat(to_peer_id(chatId))
        member = await bot.get_chat_member(to_peer_id(chatId), bot.id)
        if isinstance(member, ChatMemberOwner):
            return 0, groupType
        if isinstance(member, ChatMemberAdministrator):
            if str(groupType.type).upper() == 'CHANNEL':
                if (
                    member.can_delete_messages
                    and member.can_post_messages
                    and member.can_edit_messages
                    and member.can_invite_users
                ):
                    return 0, groupType
            else:
                if member.can_delete_messages and member.can_invite_users:
                    return 0, groupType
        return 1, groupType
    except TelegramAPIError:
        return 2, {}


async def timeJob(arr):
    try:
        msg_ids = arr.get('message_ids')
        if isinstance(msg_ids, int):
            msg_ids = [msg_ids]
        await bot.delete_messages(arr.get('id'), message_ids=msg_ids)
    except TelegramAPIError as e:
        logging.debug(f"Ошибка удаления сообщения: {e}")


async def msgNotify(id=None, text='Нет', times=2):
    msgId = await bot.send_message(
        chat_id=to_peer_id(id),
        text=f"{esc(text)}\n(удаление через {times} сек.)",
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
    scheduler.add_job(
        timeJob,
        trigger='date',
        run_date=datetime.datetime.now() + datetime.timedelta(seconds=times),
        args=({'id': msgId.chat.id, 'message_ids': [msgId.message_id]},),
    )
