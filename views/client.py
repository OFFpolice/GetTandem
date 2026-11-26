from config import *
from public.method import *
from data.data import *


class Index:
    def __init__(self, Client: Bot, Query: CallbackQuery = None, Msg: Message = None, Data=None):
        self.client = Client
        self.query = Query
        self.msg = Msg
        self.data = Data

    async def retChat(self):
        if self.query:
            return self.query.message
        return self.msg

    async def sendMsg(self, **kwargs):
        msg = await self.retChat()
        await send_inline_message(
            client=self.client,
            msg=msg,
            is_query=bool(self.query),
            text=kwargs['text'],
            keyboard=kwargs['keyboard'],
            parse_mode=kwargs.get('parse_mode', ParseMode.HTML),
            tag="Index.sendMsg",
        )

    async def index(self, **kwargs):
        msg = await self.retChat()
        user = self.data.get('user')
        try:
            if user:
                botClean = await get_bot_username(self.client)
                adminInviteUrl = (
                    f"https://t.me/{botClean}?startchannel"
                    f"&admin=post_messages+edit_messages+delete_messages+invite_users"
                )
                text = (
                    f"<b>👋 Здравствуйте, я бот для взаимного продвижения каналов!</b>\n\n"
                    f"<b>P.S. Ваш ID:</b> <code>{esc(user[1])}</code>\n\n"
                    f"<b>Инструкция:</b>\n"
                    f'<blockquote>Добавьте бота в ваш <a href="{html.escape(adminInviteUrl, quote=True)}">канал</a> и выдайте права администратора</blockquote>\n'
                    f"<b>Права администратора:</b>\n"
                    f"<blockquote>Публикация сообщений\n"
                    f"Редактирование сообщений\n"
                    f"Удаление сообщений\n"
                    f"Приглашение пользователей</blockquote>\n"
                    f"<b>(Без этих прав бот не сможет работать)</b>\n\n"
                    f"<b>⚠️ Запрещено участие каналов которые нарушают правила платформа держателей, телеграм и здравый смысл!</b>"
                )
                keyboard = [
                    [InlineKeyboardButton(text="Добавить бота в канал", url=adminInviteUrl, icon_custom_emoji_id="5258108352008823107")],
                    [InlineKeyboardButton(text="Подборки каналов", callback_data="r/channel", icon_custom_emoji_id="5257969839313526622")],
                    [
                        InlineKeyboardButton(text="Инструкция", callback_data="r/instruction", icon_custom_emoji_id="5258503720928288433"),
                        InlineKeyboardButton(text="Новости", url="https://t.me/BroadcastOFF", icon_custom_emoji_id="6021418126061605425"),
                    ],
                ]
                await self.sendMsg(text=text, keyboard=keyboard, parse_mode=ParseMode.HTML)
        except (TelegramAPIError, Exception) as E:
            logging.error(f"Index.index error: {E}")
            await msg.answer(text=f'Ошибка: сделайте скриншот и обратитесь в поддержку {esc(E)}')

    async def instruction(self, **kwargs):
        msg = await self.retChat()
        botClean = await get_bot_username(self.client)
        adminInviteUrl = (
            f"https://t.me/{botClean}?startchannel"
            f"&admin=post_messages+edit_messages+delete_messages+invite_users"
        )
        text = (
            '<b><tg-emoji emoji-id="5258503720928288433">❔</tg-emoji> Подробная инструкция по работе с ботом</b>\n\n'
            "<b>1. Добавление канала</b>\n"
            '<blockquote>Нажмите кнопку «<tg-emoji emoji-id="5258108352008823107">📍</tg-emoji> Добавить бота в канал» и выберите нужный канал. '
            "Выдайте боту все 4 права администратора: публикация, редактирование, удаление сообщений и приглашение пользователей. "
            "После добавления бот автоматически проверит права и сохранит канал.</blockquote>\n\n"
            "<b>2. Выбор подборки и подача заявки</b>\n"
            '<blockquote>Откройте раздел «<tg-emoji emoji-id="5257969839313526622">⏺</tg-emoji> Подборки каналов», выберите подборку, подходящую по минимальному числу подписчиков, '
            "и отправьте заявку для своего канала. Заявка поступит администратору на проверку.</blockquote>\n\n"
            "<b>3. Автоматический взаимопиар</b>\n"
            "<blockquote>После одобрения канал попадает в подборку. Бот автоматически публикует общий список каналов по расписанию, "
            "обновляет пост и удаляет предыдущее сообщение подборки, чтобы канал не засорялся.</blockquote>\n\n"
            "<b>4. Важные требования</b>\n"
            "<blockquote>• Не снимайте с бота права администратора и не удаляйте его из канала.\n"
            "• Не удаляйте опубликованный пост подборки вручную — иначе канал будет автоматически снят с подборки.\n"
            "• Запрещены каналы, нарушающие правила Telegram и платформ, а также каналы со сторонними ботами из ЧС.</blockquote>"
        )
        keyboard = [
            [InlineKeyboardButton(text="Добавить бота в канал", url=adminInviteUrl, icon_custom_emoji_id="5258108352008823107")],
            [InlineKeyboardButton(text="Подборки каналов", callback_data="r/channel", icon_custom_emoji_id="5257969839313526622")],
            [
                InlineKeyboardButton(text="Новости", url="https://t.me/BroadcastOFF", icon_custom_emoji_id="6021418126061605425"),
                InlineKeyboardButton(text="Назад", callback_data="r/index", icon_custom_emoji_id="5258084656674250503"),
            ],
        ]
        try:
            await self.sendMsg(text=text, keyboard=keyboard, parse_mode=ParseMode.HTML)
        except (TelegramAPIError, Exception) as E:
            logging.error(f"Index.instruction error: {E}")
            await msg.answer(text=f'Ошибка: сделайте скриншот и обратитесь в поддержку {esc(E)}')


class Channel:
    def __init__(self, Client: Bot, Query: CallbackQuery = None, Msg: Message = None, Data=None):
        self.client = Client
        self.query = Query
        self.msg = Msg
        self.data = Data

    async def retChat(self):
        if self.query:
            return self.query.message
        return self.msg

    async def sendMsg(self, **kwargs):
        msg = await self.retChat()
        await send_inline_message(
            client=self.client,
            msg=msg,
            is_query=bool(self.query),
            text=kwargs['text'],
            keyboard=kwargs['keyboard'],
            parse_mode=kwargs.get('parse_mode', ParseMode.HTML),
            tag="Channel.sendMsg",
        )

    async def index(self, **kwargs):
        OFFSET, LIMIT = int(kwargs.get('page')[0]) if kwargs.get('page') else 0, 30
        fleet = ChannelFleetList()
        fleetList, count = await fleet.get_fleet(OFFSET=OFFSET, LIMIT=LIMIT)
        group_count = await fleet.get_group_count()
        keyboard = []
        text = (
            '<b><tg-emoji emoji-id="5257969839313526622">⏺</tg-emoji> Подборки каналов</b>\n\n'
            f"<b>Активных подборок:</b> {count}\n"
            f"<b>Участвует каналов:</b> {group_count}\n\n"
            "<b>Обозначения кнопок:</b>\n"
            "<blockquote>"
            "🚒 — идёт рассылка\n"
            "🕛 — ожидание запуска\n"
            "<code>Название | места | мин. подписчиков</code>"
            "</blockquote>\n\n"
            "Выберите подходящую подборку ниже, а затем укажите ваш канал для подачи заявки."
        )
        if fleetList:
            totalPages, currentPage = math.ceil(count / LIMIT) or 1, math.ceil(OFFSET / LIMIT) + 1
            upPage, dowPage = OFFSET - LIMIT, OFFSET + LIMIT
            row, step = [], 2
            for i in range(0, len(fleetList), step):
                batch = fleetList[i:i + step]
                for Cont in batch:
                    row.append(
                        InlineKeyboardButton(
                            text=f"{'🚒' if Cont[4] == 1 else '🕛'} {Cont[1]}|{Cont[11]}/{Cont[6]}|{(Cont[8] or 0) / 1000}K",
                            callback_data=f"r/channel_fleet?fleet={Cont[0]}",
                        )
                    )
                keyboard.append(row)
                row = []
            keyboard.append([
                InlineKeyboardButton(
                    text='Назад',
                    callback_data=f"r/channel?page={upPage}",
                    icon_custom_emoji_id="5258084656674250503",
                ) if upPage >= 0 else InlineKeyboardButton(text='-', callback_data='-'),
                InlineKeyboardButton(text=f"{currentPage}/{totalPages} стр.", callback_data="-"),
                InlineKeyboardButton(
                    text='➡️ Вперёд' if currentPage < totalPages else '-',
                    callback_data=f"r/channel?page={dowPage}" if currentPage < totalPages else '-',
                ),
            ])
        else:
            keyboard.append([InlineKeyboardButton(text="Пусто / подборки не найдены", callback_data="-")])
        keyboard.append([InlineKeyboardButton(text="Назад", callback_data="r/index", icon_custom_emoji_id="5258084656674250503")])
        await self.sendMsg(text=text, keyboard=keyboard)

    async def fleet_info(self, **kwargs):
        fleet_id = kwargs.get("fleet")[0]
        fleet = ChannelFleetList()
        fleetInfo = await fleet.get_fleet_one(id=fleet_id)
        group_list = await fleet.get_fleet_group_list(id=fleet_id)
        if fleetInfo:
            text = (
                f"<b>Название подборки:</b> {esc(fleetInfo[1])}\n"
                f"<b>Описание подборки:</b> {esc(fleetInfo[2] or 'Не указано')}\n"
                f"<b>Участников (тек./макс.):</b> {fleetInfo[11]}/{fleetInfo[6]}\n"
                f"<b>Тип подборки:</b> Канал\n"
                f"<b>Мин. подписчиков:</b> {fleetInfo[8]}\n"
                f"<b>Мин. просмотров:</b> {fleetInfo[9]}\n\n"
                "<b>Список участников:</b>\n"
            )
            if group_list:
                for index, group in enumerate(group_list):
                    short_name = await truncate_string(group[3], 20)
                    text += f"{index + 1}.{html_link(short_name, group[6])} {round((group[5] or 0) / 1000, 1)}k\n"
            else:
                text += "Сейчас нет участников в подборке\n"
            keyboard = []
            if fleetInfo[6] > fleetInfo[11]:
                text += "\n✅ В подборке есть свободные места, можно подать заявку!"
                keyboard.append([
                    InlineKeyboardButton(
                        text="➕ Подать заявку",
                        callback_data=f"r/channel_apply?fleet={fleetInfo[0]}&mi_me={fleetInfo[8]}",
                    )
                ])
            else:
                text += "\n‼️ Подборка заполнена, выберите другую!"
            keyboard.append([
                InlineKeyboardButton(text="Главная", callback_data="r/index", icon_custom_emoji_id="5257963315258204021"),
                InlineKeyboardButton(text="Назад", callback_data="r/channel", icon_custom_emoji_id="5258084656674250503"),
            ])
            await self.sendMsg(text=text, keyboard=keyboard)
        else:
            await self.query.answer(text="⛔ Подборка не найдена", show_alert=True)

    async def add_fleet(self, **kwargs):
        msg = await self.retChat()
        fleet, member = kwargs.get('fleet')[0], kwargs.get('mi_me')[0]
        user = self.data.get('user')
        if user:
            CF = ChannelFleetList(Msg=msg)
            my_group = await CF.get_user_group_list(id=user[0], member=safe_int(member))
            if my_group:
                text = (
                    "<b>Выбор канала</b>\n\n"
                    "Ниже отображаются только каналы, подходящие под требования\n\n"
                    f"Требуется подписчиков: {round(safe_int(member) / 1000, 1)}k\n"
                    "Обозначения: 🟢 Свободен 🟡 На проверке 🟣 В подборке 🔴 Заблокирован\n"
                    "Повторная заявка для канала, уже состоящего в подборке, автоматически снимет его с текущей\n"
                    "Убедитесь, что вы добавили бота в канал и назначили его администратором\n\n"
                    "👇 Выберите канал для отправки заявки"
                )
                keyboard = []
                for group in my_group:
                    ty_emoji = "🟢"
                    if group[10] == 1:
                        ty_emoji = "🟡"
                    elif group[10] == 2:
                        ty_emoji = "🟣"
                    elif group[10] == 10:
                        ty_emoji = "🔴"
                    keyboard.append([
                        InlineKeyboardButton(
                            text=f"{ty_emoji} {group[3]}|{round((group[5] or 0) / 1000, 1)}k",
                            callback_data=f"r/channel_submit?f={fleet}&g={group[0]}",
                        )
                    ])
                keyboard.append([
                    InlineKeyboardButton(text="Главная", callback_data="r/index", icon_custom_emoji_id="5257963315258204021"),
                    InlineKeyboardButton(text="Назад", callback_data=f"r/channel_fleet?fleet={fleet}", icon_custom_emoji_id="5258084656674250503"),
                ])
                await self.sendMsg(text=text, keyboard=keyboard)
            else:
                return await self.query.answer(
                    text="⚠️ Не найдено каналов, соответствующих требованиям подборки. Выбирайте подборку по числу подписчиков",
                    show_alert=True,
                )

    async def submit_fleet(self, **kwargs):
        msg = await self.retChat()
        fleet = ChannelFleetList()
        fleet_id, group_id = kwargs.get('f')[0], kwargs.get('g')[0]
        fleetInfo = await fleet.get_fleet_one(id=fleet_id)
        group = await fleet.get_user_group_one(id=group_id)
        if group and fleetInfo:
            if group[10] in [0, 1, 2]:
                isPrivi = await isPrivileges(chatId=to_peer_id(group[1]), typeG=group[4])
                if isPrivi == 1:
                    return await self.query.answer(
                        text="⚠️ В этом канале боту не выданы права, проверьте",
                        show_alert=True,
                    )
                elif isPrivi == 2:
                    return await self.query.answer(
                        text="⛔ Бот ещё не добавлен в этот канал",
                        show_alert=True,
                    )
                is_botList = await isBotBlacklist(Client=self.client, group=to_peer_id(group[1]))
                if len(is_botList) > 0:
                    text = f"<b>⚠️ В вашем канале {html_link(group[3], group[6])} обнаружены боты из чёрного списка</b>\n\n"
                    for is_bot in is_botList:
                        text += f"{esc(is_bot[0])}-@<code>{esc(is_bot[1])}</code> (копировать)\n"
                    text += "\nУдалите указанных ботов и отправьте заявку повторно"
                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[[InlineKeyboardButton(text="❌ Удалить сообщение", callback_data="r/del_msg")]]
                    )
                    return await msg.answer(
                        text=text,
                        reply_markup=keyboard,
                        link_preview_options=LinkPreviewOptions(is_disabled=True),
                    )
                await self.query.answer(
                    text='🎯 Заявка отправлена, ожидайте проверки администратором',
                    show_alert=True,
                )
                await fleet.put_group_one(id=group_id, fieet=fleet_id)
                await self.sendNotify(fleet=fleetInfo, group=group)
                await self.add_fleet(fleet=[fleetInfo[0]], mi_me=[fleetInfo[8]])
            elif group[10] == 10:
                await self.query.answer(
                    text='⚠️ Заблокирован за многократные нарушения, обратитесь в поддержку',
                    show_alert=True,
                )
            else:
                await self.query.answer(
                    text='⚠️ Не отправляйте заявку повторно, дождитесь проверки администратором',
                    show_alert=True,
                )
        else:
            await self.query.answer(text="⛔ Ошибка: информация о канале не найдена", show_alert=True)

    async def sendNotify(self, **kwargs):
        fleet, group, user = kwargs["fleet"], kwargs["group"], self.data.get("user")
        applicant = (
            html_link(user[3], f"https://t.me/{user[2]}")
            if user[2] and user[2] != 'Нет'
            else esc(user[3])
        )
        text = (
            "<b>🔆 Получена новая заявка в подборку</b>\n"
            f"<b>Название подборки:</b> {esc(fleet[1])}\n"
            "<b>Тип подборки:</b> Канал\n"
            f"<b>Описание подборки:</b> {esc(fleet[2] or 'Не указано')}\n"
            f"<b>Участников (тек./макс.):</b> {fleet[11]}/{fleet[6]}\n"
            f"<b>Мин. подписчиков:</b> {fleet[8]}\n"
            f"<b>Мин. просмотров:</b> {fleet[9]}\n\n"
            f"<b>ID канала:</b> {esc(group[1])}\n"
            f"<b>Канал:</b> {html_link(group[3], group[6])}\n"
            f"<b>Подписчиков:</b> {group[5]}\n"
            f"<b>ID заявителя:</b> {esc(user[1])}\n"
            f"<b>Заявитель:</b> {applicant}\n"
            "<b>Статус заявки:</b> 🔵 На проверке"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🟢 Одобрить", callback_data=f"a/review_pass?group={group[0]}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"a/review_reject?group={group[0]}"),
            ],
            [InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"a/review_ban?group={group[0]}")],
        ])
        await CarData().post_notify_msg(group=group, label="На проверке")
        await notify_admins(self.client, text=text, reply_markup=keyboard)
