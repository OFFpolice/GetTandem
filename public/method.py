import logging
from config import *
import emoji
from data.data import *


def to_peer_id(val):
    if val is None:
        return None
    s = str(val).strip()
    if s.lstrip('-').isdigit():
        return int(s)
    return s


def safe_int(val, default=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def format_tg_url(val):
    s = str(val or '').strip()
    if s.startswith('http://') or s.startswith('https://'):
        return s
    return f"https://t.me/{s.lstrip('@')}"


def esc(val):
    return html.escape(str(val if val is not None else ''))


def html_link(title, url):
    u = str(url or '').strip()
    t = esc(title)
    if u.startswith('http://') or u.startswith('https://'):
        return f'<a href="{html.escape(u, quote=True)}">{t}</a>'
    return t


FALLBACK_CUSTOM_ICONS = {
    "5258108352008823107": "📍",
    "5257969839313526622": "⏺",
    "5258503720928288433": "❔",
    "6021418126061605425": "📢",
    "5258084656674250503": "⬅️",
    "5257963315258204021": "🏚",
}


async def send_inline_message(
    client: Bot,
    msg: Message,
    is_query: bool,
    text: str,
    keyboard: list,
    parse_mode: ParseMode = ParseMode.HTML,
    tag: str = "sendMsg",
):
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def _send(reply_markup):
        if is_query:
            await client.edit_message_text(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                text=text,
                reply_markup=reply_markup,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                parse_mode=parse_mode,
            )
        else:
            await msg.answer(
                text=text,
                reply_markup=reply_markup,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                parse_mode=parse_mode,
            )

    try:
        await _send(markup)
    except TelegramBadRequest as e:
        err_msg = str(e).lower()
        if "message is not modified" in err_msg:
            return
        if "emoji" in err_msg or "icon" in err_msg or "custom_emoji" in err_msg:
            plain_rows = []
            for row in keyboard:
                plain_row = []
                for btn in row:
                    data = btn.model_dump(exclude_none=True)
                    icon_id = data.pop("icon_custom_emoji_id", None)
                    if icon_id and icon_id in FALLBACK_CUSTOM_ICONS:
                        data["text"] = f"{FALLBACK_CUSTOM_ICONS[icon_id]} {data['text']}"
                    plain_row.append(InlineKeyboardButton(**data))
                plain_rows.append(plain_row)
            try:
                await _send(InlineKeyboardMarkup(inline_keyboard=plain_rows))
                return
            except TelegramAPIError as retry_err:
                logging.warning(f"{tag} fallback error: {retry_err}")
        logging.warning(f"{tag} TelegramBadRequest: {e}")
    except TelegramAPIError as e:
        logging.warning(f"{tag} TelegramAPIError: {e}")


class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, path_pattern, handler_class, handler_method):
        param_pattern = re.compile(r'<(\w+)>')
        param_names = param_pattern.findall(path_pattern)
        path_pattern = param_pattern.sub(r'(?P<\1>[^/]+)', path_pattern)
        path_regex = re.compile(f"^{path_pattern}$")
        self.routes.append((path_regex, param_names, handler_class, handler_method))

    async def route(self, url, *args, **kwargs):
        parsed_url = urlparse(url)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        for path_regex, param_names, handler_class, handler_method in self.routes:
            match = path_regex.match(path)
            if not match:
                continue
            for param_name in param_names:
                query_params[param_name] = match.group(param_name)
            try:
                handler = handler_class(*args, **kwargs)
                return await getattr(handler, handler_method)(**query_params)
            except (TelegramAPIError, Exception) as e:
                raise ValueError(f"Ошибка выполнения метода маршрута {handler_method}: {e}")
        raise ValueError("В разработке — страница не найдена")


class RestrictAccess:
    # Контроль доступа
    def __init__(self, Msg: Message = None):
        self.msg = Msg

    async def limit_check(self):
        msg = self.msg
        if not msg or not msg.chat:
            return True
        try:
            count = redis_client.get(f"restrict{msg.chat.id}")
            if count is None or int(count) < int(bot_config['restrict_limit']):
                redis_client.incr(f"restrict{msg.chat.id}")
                if count is None:
                    redis_client.expire(f"restrict{msg.chat.id}", 60)
                return True
            else:
                if int(count) == int(bot_config['restrict_limit']):
                    redis_client.incr(f"restrict{msg.chat.id}")
                    redis_client.expire(f"restrict{msg.chat.id}", 60 * 10)
                    await msg.answer('Слишком частые запросы, доступ ограничен на 10 мин.')
                return False
        except Exception as e:
            logging.error(f"Ошибка ограничения доступа: {e}")
            return False


class UserAuth:
    # Аутентификация пользователя
    def __init__(self, Msg: Message = None):
        self.msg = Msg

    async def auth(self, FromUser=None):
        msg = self.msg
        if not FromUser:
            return False
        try:
            name = f"user{FromUser.id}"
            redis_client.delete(name)
            user = redis_client.get(name)
            if user:
                user = json.loads(user)
            else:
                dbUser = ChatUser(Msg=msg)
                user = await dbUser.get_or_create(FromUser)
                redis_client.set(name, json.dumps(user, default=str), ex=600)
            if not user:
                if msg:
                    await msg.answer("Ошибка доступа к аккаунту")
                return False
            if user[4] == 1:
                if msg:
                    await msg.answer("Аккаунт заблокирован администратором")
                return False
            return user
        except Exception as e:
            logging.error(f"Ошибка доступа к аккаунту: {e}")
            if msg:
                await msg.answer("Ошибка доступа к аккаунту")
            return False


class Var:
    def __init__(self, Msg: Message = None):
        self.msg = Msg

    def write(self, value=None):
        msg = self.msg
        if value and msg:
            try:
                name = f"var{msg.chat.id}"
                redis_client.set(name, json.dumps(value, default=str), ex=60 * 2)
                return True
            except Exception as e:
                logging.error(f"Ошибка записи в Redis: {e}")
        return False


async def truncate_string(string, length):
    '''Обрезка заголовка'''
    pattern = r":[^:]+:"
    newStr = re.sub(pattern, "", emoji.demojize(string or ""))
    if len(newStr) > length:
        return newStr[:length] + ".."
    else:
        return newStr


async def isPrivileges(chatId, typeG):
    # Проверка прав бота в канале
    try:
        member = await bot.get_chat_member(to_peer_id(chatId), bot.id)
        if isinstance(member, ChatMemberOwner):
            return 0
        if isinstance(member, ChatMemberAdministrator):
            if str(typeG).upper() == 'CHANNEL':
                if (
                    member.can_delete_messages
                    and member.can_post_messages
                    and member.can_edit_messages
                    and member.can_invite_users
                ):
                    return 0
            else:
                if member.can_delete_messages and member.can_invite_users:
                    return 0
        return 1
    except TelegramAPIError:
        return 2


_bot_username_cache = ""


async def get_bot_username(client: Bot = None):
    global _bot_username_cache
    if _bot_username_cache:
        return _bot_username_cache
    c = client or bot
    try:
        me = await c.get_me()
        if me and me.username:
            _bot_username_cache = me.username.lstrip('@')
    except TelegramAPIError as e:
        logging.warning(f"Не удалось получить username бота: {e}")
    return _bot_username_cache


async def get_bot_url(client: Bot = None):
    uname = await get_bot_username(client)
    return f"https://t.me/{uname}" if uname else "https://t.me"


USER_COMMANDS = [
    BotCommand(command="start", description="Главная"),
    BotCommand(command="help", description="Помощь"),
]

ADMIN_COMMANDS = [
    BotCommand(command="start", description="Главная"),
    BotCommand(command="help", description="Помощь"),
    BotCommand(command="admin", description="Панель администратора"),
]


async def sync_user_commands(client: Bot, chat_id, is_admin: bool):
    peer = to_peer_id(chat_id)
    try:
        if is_admin:
            await client.set_my_commands(ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=peer))
        else:
            await client.delete_my_commands(scope=BotCommandScopeChat(chat_id=peer))
    except TelegramAPIError as e:
        logging.debug(f"Не удалось обновить команды меню для {peer}: {e}")


async def sync_bot_commands(client: Bot = None):
    c = client or bot
    ok = True
    try:
        await c.set_my_commands(USER_COMMANDS, scope=BotCommandScopeDefault())
        await c.set_my_commands(USER_COMMANDS, scope=BotCommandScopeAllPrivateChats())
    except TelegramAPIError as e:
        ok = False
        logging.warning(f"Не удалось установить команды бота: {e}")
    admin_list = await ChannelFleetList().get_admini_list()
    for adm in admin_list:
        await sync_user_commands(c, adm[1], is_admin=True)
    return ok


async def get_config():
    try:
        configData = ConfigData()
        configList = await configData.get_config_list()
        if configList:
            bot_config["rejectText"] = []
            for config in configList:
                if config[1] == "rejectText":
                    bot_config["rejectText"].append(config[2])
                elif config[1] in bot_config:
                    bot_config[config[1]] = config[2]
        return bot_config
    except Exception as e:
        logging.error(f'Ошибка чтения конфигурации: {e}')
        return bot_config


async def timeJob(arr):
    try:
        msg_ids = arr.get('message_ids')
        if isinstance(msg_ids, int):
            msg_ids = [msg_ids]
        await bot.delete_messages(chat_id=arr.get('id'), message_ids=msg_ids)
    except TelegramAPIError as e:
        logging.debug(f"Ошибка удаления временного сообщения: {e}")


async def msgNotify(msg: Message, text='Нет', times=2):
    msgId = await msg.answer(text=f"{esc(text)}\n(удаление через {times} сек.)")
    scheduler.add_job(
        timeJob,
        trigger='date',
        run_date=datetime.datetime.now(scheduler.timezone) + datetime.timedelta(seconds=times),
        args=({'id': msgId.chat.id, 'message_ids': [msgId.message_id]},),
    )


async def isBotBlacklist(Client: Bot, group):
    bl_rows = await BotBlacklistDate().get_bot_blacklist_list()
    if not bl_rows:
        return []
    bl_names = {
        str(row[1] or '').strip().lstrip('@').lower()
        for row in bl_rows
        if row[1]
    }
    if not bl_names:
        return []
    isBot = []
    peer_id = to_peer_id(group)
    try:
        admins = await Client.get_chat_administrators(peer_id)
        for admin in admins:
            uname = (admin.user.username or '').strip().lstrip('@').lower()
            if uname and uname in bl_names:
                isBot.append([admin.user.first_name or uname, admin.user.username])
                break
    except TelegramAPIError as e:
        logging.debug(f"Не удалось получить список администраторов канала {peer_id}: {e}")
    return isBot


async def send_msg(chat_id, text):
    try:
        await bot.send_message(
            chat_id=to_peer_id(chat_id),
            text=text,
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
    except TelegramAPIError as e:
        logging.error(f'Ошибка отправки сообщения: {chat_id} - Ошибка: {e}')


async def notify_admins(bot_client: Bot, text: str, reply_markup=None):
    notify_type = safe_int(bot_config.get("notifyType"), 1)
    admin_group = safe_int(bot_config.get("adminGroup"), 0)
    if notify_type == 0 and abs(admin_group) > 100:
        try:
            await bot_client.send_message(
                chat_id=admin_group,
                text=text,
                reply_markup=reply_markup,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
            return True
        except TelegramAPIError as e:
            logging.warning(f"Ошибка отправки уведомления в adminGroup ({admin_group}), отправка админам в ЛС: {e}")
    adminList = await ChannelFleetList().get_admini_list()
    sent = False
    for admin in adminList:
        try:
            await bot_client.send_message(
                chat_id=to_peer_id(admin[1]),
                text=text,
                reply_markup=reply_markup,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
            sent = True
        except TelegramAPIError as e:
            logging.warning(f"Ошибка отправки уведомления администратору {admin[1]}: {e}")
    return sent


async def convoyDriving():
    fleet_list = await db.select("SELECT * FROM fleet_list WHERE state = 1")
    logging.info('Запуск рассылки')
    if fleet_list:
        vp_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="JISOU",
                    url="https://t.me/jisou?start=a_1741564693",
                    icon_custom_emoji_id="5429571366384842791",
                ),
            ]
        ])
        for fleet in fleet_list:
            group_list = await db.select(
                "SELECT * FROM group_list WHERE fleet_list=? AND type='CHANNEL' AND state=2",
                (fleet[0],),
            )
            if group_list and len(group_list) >= 1:
                for group in group_list:
                    user = await db.select("SELECT * FROM chat_user WHERE id=?", (group[12],))
                    if not user:
                        continue
                    peer_id = to_peer_id(group[1])
                    isPrivi = await isPrivileges(chatId=peer_id, typeG=group[4])
                    if isPrivi == 1:
                        await db.update("UPDATE group_list SET state=0 WHERE id=?", (group[0],))
                        text = (
                            f"Проверка рассылки: в «{html_link(group[3], group[6])}» "
                            f"у бота недостаточно прав, канал будет снят с подборки, проверьте"
                        )
                        await send_msg(chat_id=user[0][1], text=text)
                        continue
                    elif isPrivi == 2:
                        await db.update("UPDATE group_list SET state=0 WHERE id=?", (group[0],))
                        text = (
                            f"Проверка рассылки: в «{html_link(group[3], group[6])}» "
                            f"бот не обнаружен, канал будет снят с подборки, проверьте"
                        )
                        await send_msg(chat_id=user[0][1], text=text)
                        continue
                    if group[7] and int(group[7]) != 0:
                        msg_exists = True
                        try:
                            await bot.edit_message_reply_markup(
                                chat_id=peer_id,
                                message_id=int(group[7]),
                                reply_markup=vp_keyboard,
                            )
                        except TelegramBadRequest as e:
                            err_text = str(e).lower()
                            if "not modified" in err_text:
                                msg_exists = True
                            elif "not found" in err_text or "message_id_invalid" in err_text:
                                msg_exists = False
                        except TelegramAPIError:
                            msg_exists = True
                        if not msg_exists:
                            await db.update("UPDATE group_list SET state=0 WHERE id=?", (group[0],))
                            text = (
                                f"Проверка рассылки: в «{html_link(group[3], group[6])}» "
                                f"не найдено предыдущее сообщение, канал снят с подборки"
                            )
                            await send_msg(chat_id=user[0][1], text=text)
                            continue
                    text_list = await marshalling(group_chat=group, fleet=fleet)
                    if len(text_list) > 2:
                        try:
                            msg = await bot.send_message(
                                chat_id=peer_id,
                                text=''.join(text_list),
                                reply_markup=vp_keyboard,
                                link_preview_options=LinkPreviewOptions(is_disabled=True),
                                disable_notification=True,
                            )
                        except TelegramAPIError as e:
                            logging.error(f"Ошибка отправки подборки в канал {group[1]}: {e}")
                            continue
                        if msg and msg.message_id:
                            await db.update(
                                "UPDATE group_list SET msg_id=? WHERE group_id=?",
                                (msg.message_id, str(group[1])),
                            )
                            try:
                                if group[7] and int(group[7]) != 0:
                                    await bot.delete_message(chat_id=peer_id, message_id=int(group[7]))
                            except TelegramAPIError as e:
                                logging.warning(f"Ошибка удаления предыдущего сообщения {group[2]}: {e}")


async def marshalling(group_chat=None, fleet=None):
    new_car_list, index = [], 1
    bot_url = await get_bot_url(bot)
    header_link = html_link(fleet[1], bot_url)
    new_car_list.append(f"<b>⛩️ {header_link} ⛩️</b>\n")
    advertising_list = await AdvertisingData().get_advertising_list()
    if len(advertising_list) >= 1:
        new_car_list.append(f"<b>AD:{html_link(advertising_list[0][1], advertising_list[0][2])}</b>\n\n")
    group_list = await db.select(
        "SELECT * FROM group_list WHERE fleet_list=? AND type='CHANNEL' AND state=2",
        (fleet[0],),
    )
    for group in group_list:
        if group[0] != group_chat[0]:
            invite_url = str(group[6] or '').strip()
            try:
                if "/+" in invite_url or "joinchat/" in invite_url:
                    link_group = await bot.edit_chat_invite_link(to_peer_id(group[1]), invite_url)
                    if link_group and not link_group.is_revoked:
                        short_name = await truncate_string(group[3], 20)
                        new_car_list.append(f"{index}: {html_link(short_name, link_group.invite_link)} \n")
                        index += 1
                    else:
                        await db.update("UPDATE group_list SET state=0 WHERE id=?", (group[0],))
                        continue
                else:
                    link_group = await bot.create_chat_invite_link(to_peer_id(group[1]))
                    await db.update("UPDATE group_list SET url=? WHERE id=?", (link_group.invite_link, group[0]))
                    short_name = await truncate_string(group[3], 20)
                    new_car_list.append(f"{index}: {html_link(short_name, link_group.invite_link)} \n")
                    index += 1
            except TelegramAPIError as e:
                logging.warning(f"Ошибка проверки ссылки {group[1]}: {e}")
                await db.update("UPDATE group_list SET state=0 WHERE id=?", (group[0],))
                continue
    try:
        self_url = str(group_chat[6] or '').strip()
        if "/+" in self_url or "joinchat/" in self_url:
            link_group = await bot.edit_chat_invite_link(to_peer_id(group_chat[1]), self_url)
            if link_group and not link_group.is_revoked:
                try:
                    member_count = await bot.get_chat_member_count(to_peer_id(group_chat[1]))
                    await db.update(
                        "UPDATE group_list SET input_fan=? WHERE id=?",
                        (member_count, group_chat[0]),
                    )
                except TelegramAPIError as e:
                    logging.debug(f"Ошибка обновления числа участников канала: {e}")
    except TelegramAPIError as e:
        logging.debug(f"Ошибка обновления числа вступивших по ссылке: {e}")
    if index <= 1:
        return []
    if len(advertising_list) >= 2:
        new_car_list.append(f"\n<b>AD:{html_link(advertising_list[1][1], advertising_list[1][2])}</b>")
    if len(advertising_list) >= 3:
        new_car_list.append(f"\n<b>AD:{html_link(advertising_list[2][1], advertising_list[2][2])}</b>")
    return new_car_list
