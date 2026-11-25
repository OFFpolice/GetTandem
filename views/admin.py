from config import *
from public.method import *


class Admin:
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
        markup = InlineKeyboardMarkup(inline_keyboard=kwargs['keyboard'])
        try:
            if self.query:
                await self.client.edit_message_text(
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    text=kwargs['text'],
                    reply_markup=markup,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            else:
                if len(bot_config.get('video') or '') > 24:
                    await self.client.send_video(
                        chat_id=msg.chat.id,
                        video=bot_config.get('video'),
                        caption=kwargs['text'],
                        reply_markup=markup,
                    )
                else:
                    await msg.answer(
                        text=kwargs['text'],
                        reply_markup=markup,
                        link_preview_options=LinkPreviewOptions(is_disabled=True),
                    )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                logging.warning(f"Admin.sendMsg TelegramBadRequest: {e}")
        except TelegramAPIError as e:
            logging.warning(f"Admin.sendMsg TelegramAPIError: {e}")

    async def index(self, **kwargs):
        text = (
            "✨✨✨✨✨✨✨✨✨✨✨✨\n\n"
            "======<b>🏆 Панель управления 🏆</b>======\n\n"
            "🌟<b>Добро пожаловать, администратор:</b>🌟\n"
            "  ✅ Здесь можно управлять функциями бота"
        )
        keyboard = [
            [
                InlineKeyboardButton(text="☸️ Настройки бота", callback_data="a/config"),
                InlineKeyboardButton(text="🅰️️ Реклама", callback_data="a/ad"),
            ],
            [
                InlineKeyboardButton(text="🚒 Подборки", callback_data="a/car"),
                InlineKeyboardButton(text="📇 Каналы", callback_data="a/group"),
            ],
            [
                InlineKeyboardButton(text="🤖 ЧС ботов", callback_data="a/bot_bl"),
                InlineKeyboardButton(text="👨‍💻 Пользователи", callback_data="a/user"),
            ],
        ]
        await self.sendMsg(text=text, keyboard=keyboard)

    async def config(self, **kwargs):
        cfg = await get_config()
        text = (
            "✨✨✨✨✨✨✨✨✨✨✨✨\n\n"
            "======<b>🏆 Настройки бота 🏆</b>======\n\n"
            "<b>🔸Инициализация меню:</b> настройка команд меню пользователя\n"
            f"<b>🔸Название бота:</b> {esc(cfg.get('botName'))}\n"
            f"<b>🔸Аккаунт бота:</b> {esc(cfg.get('botUserName'))}\n"
            f"<b>🔸Приветствие:</b>\n'{esc(cfg.get('indexTxt'))}'\n"
            f"<b>🔸Причины отказа:</b>\n{esc('|'.join(cfg.get('rejectText') or []))}\n"
            f"<b>🔸Видео-презентация:</b> {'🟢 Загружено' if len(cfg.get('video') or '') > 20 else '🚫 Не загружено'}\n"
            f"<b>🔸Админ-группа:</b> {esc(cfg.get('adminGroup'))}\n"
            f"<b>🔸Группа уведомлений:</b> {esc(cfg.get('msgGroup'))}\n"
            f"<b>🔸Чат для общения:</b> {esc(cfg.get('publicGroup'))}\n"
            f"<b>🔸Лимит запросов:</b> {esc(cfg.get('restrict_limit'))} \n(при превышении за 60 сек. — блокировка на 10 мин.)"
        )
        keyboard = [
            [InlineKeyboardButton(text="Инициализировать меню", callback_data="a/init_menu")],
            [
                InlineKeyboardButton(text="Изм. название бота", callback_data="a/edit_config?k=botName"),
                InlineKeyboardButton(text="Изм. аккаунт бота", callback_data="a/edit_config?k=botUserName"),
            ],
            [
                InlineKeyboardButton(text="Изм. приветствие", callback_data="a/edit_config?k=indexTxt"),
                InlineKeyboardButton(text="Причины отказа", callback_data="a/reject_words"),
            ],
            [
                InlineKeyboardButton(text="Изм. видео", callback_data="a/edit_config?k=video"),
                InlineKeyboardButton(text="Изм. админ-группу", callback_data="a/edit_config?k=adminGroup"),
            ],
            [
                InlineKeyboardButton(text="Изм. группу уведомлений", callback_data="a/edit_config?k=msgGroup"),
                InlineKeyboardButton(text="Изм. чат общения", callback_data="a/edit_config?k=publicGroup"),
            ],
            [InlineKeyboardButton(text="Изм. лимит запросов", callback_data="a/edit_config?k=restrict_limit")],
            [InlineKeyboardButton(text="↩️ Назад", callback_data="a/admin")],
        ]
        await self.sendMsg(text=text, keyboard=keyboard)

    async def modifBot(self, **kwargs):
        msg = await self.retChat()
        prompts = {
            "botName": "Введите название бота",
            "botUserName": "Введите юзернейм бота:Пример:@xxbot",
            "indexTxt": "Введите приветственный текст",
            "video": "Загрузите видео-презентацию",
            "adminGroup": "Введите ID админ-группы",
            "msgGroup": "Введите ID группы уведомлений",
            "publicGroup": "Введите чат для общения:Пример:@xxx",
            "restrict_limit": "Введите лимит запросов:Ответьте числом от 1 до 60",
            "addReject": "Введите причину отказа",
        }
        k = kwargs.get('k')[0] if kwargs.get('k') else None
        if k == "editReject":
            item_id = kwargs.get('id')[0]
            prompt = f"Введите новую причину отказа:{item_id}"
        elif k and k in prompts:
            prompt = prompts[k]
        else:
            prompt = kwargs.get('text')[0]
        txt = f"📲{prompt}"
        await msg.reply(text=esc(txt), reply_markup=ForceReply(selective=True))

    async def initialization(self, **kwargs):
        initial = await self.client.set_my_commands([
            BotCommand(command="start", description="Главная"),
            BotCommand(command="help", description="Помощь"),
        ])
        if initial and self.query:
            await self.query.answer(text='Меню успешно инициализировано', show_alert=True)

    async def reviewRejectionWords(self, **kwargs):
        '''Список причин отказа при модерации'''
        rejectText_list = await ConfigData().get_rejectText_list()
        text = (
            "======<b>🏆 Шаблоны причин отказа 🏆</b>======\n"
            "Быстрый выбор причины при отклонении заявки пользователя\n"
            "Обозначения: ➕Добавить ❌Удалить 🖍Изменить\n\n"
            "🚫<b>Список шаблонов причин отказа:</b>\n"
        )
        keyboard = []
        if rejectText_list:
            for index, rejectText in enumerate(rejectText_list):
                text += f"{index + 1}.{esc(rejectText[2])}\n"
                keyboard.append([
                    InlineKeyboardButton(text=f"{index + 1}.{rejectText[2]}", callback_data="-"),
                    InlineKeyboardButton(text="❌ Удалить", callback_data=f"a/del_reject_word?id={rejectText[0]}"),
                    InlineKeyboardButton(text="🖍 Изменить", callback_data=f"a/edit_config?k=editReject&id={rejectText[0]}"),
                ])
        else:
            text += "Пусто, не настроено"
            keyboard.append([InlineKeyboardButton(text="Список пуст", callback_data="-")])
        keyboard.append([InlineKeyboardButton(text="➕Добавить", callback_data="a/edit_config?k=addReject")])
        keyboard.append([
            InlineKeyboardButton(text="🏠 Админ-панель", callback_data="a/admin"),
            InlineKeyboardButton(text="↩️ Назад", callback_data="a/config"),
        ])
        await self.sendMsg(text=text, keyboard=keyboard)

    async def delReviewRejectionWords(self, **kwargs):
        '''Удаление причины отказа'''
        msg = await self.retChat()
        item_id = kwargs.get('id')[0]
        delData = await ConfigData().del_rejectText(id=item_id)
        if delData:
            await get_config()
            if self.query:
                await self.query.answer(text="✅Успешно удалено", cache_time=5)
            await self.reviewRejectionWords()
        else:
            await msgNotify(msg=msg, text="❕Ошибка удаления")


class Advertising:
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
        markup = InlineKeyboardMarkup(inline_keyboard=kwargs['keyboard'])
        try:
            if self.query:
                await self.client.edit_message_text(
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    text=kwargs['text'],
                    reply_markup=markup,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            else:
                if len(bot_config.get('video') or '') > 24:
                    await self.client.send_video(
                        chat_id=msg.chat.id,
                        video=bot_config.get('video'),
                        caption=kwargs['text'],
                        reply_markup=markup,
                    )
                else:
                    await msg.answer(
                        text=kwargs['text'],
                        reply_markup=markup,
                        link_preview_options=LinkPreviewOptions(is_disabled=True),
                    )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                logging.warning(f"Advertising.sendMsg TelegramBadRequest: {e}")
        except TelegramAPIError as e:
            logging.warning(f"Advertising.sendMsg TelegramAPIError: {e}")

    async def adInput(self, **kwargs):
        msg = await self.retChat()
        k = kwargs.get('k')[0] if kwargs.get('k') else None
        if k == "addAd":
            prompt = "Введите рекламу:Пример:Текст ВП&Ссылка"
        elif k == "editAd":
            item_id = kwargs.get('id')[0]
            prompt = f"Введите новую рекламу:{item_id}"
        else:
            prompt = kwargs.get('text')[0]
        txt = f"🗞️{prompt}"
        await msg.reply(text=esc(txt), reply_markup=ForceReply(selective=True))

    async def index(self, **kwargs):
        '''Управление рекламой'''
        advertising_list = await AdvertisingData().get_advertising_list()
        text = (
            "======<b>🏆 Управление рекламой 🏆</b>======\n"
            "Реклама, добавляемая при рассылке подборки\n"
            "Пример добавления: Взаимопиар&amp;https://t.me/+oYUJoUkMlfphN2M1\n"
            "Обозначения: ➕Добавить ❌Удалить 🖍Изменить\n\n"
            "🚫<b>Список рекламы:</b>\n"
        )
        keyboard = []
        if advertising_list:
            for index, advertising in enumerate(advertising_list):
                text += f"{index + 1}.{html_link(advertising[1], advertising[2])}\n"
                keyboard.append([
                    InlineKeyboardButton(text=f"{index + 1}.{advertising[1]}", callback_data="-"),
                    InlineKeyboardButton(text="❌ Удалить", callback_data=f"a/del_ad?id={advertising[0]}"),
                    InlineKeyboardButton(text="🖍 Изменить", callback_data=f"a/ad_input?k=editAd&id={advertising[0]}"),
                ])
        else:
            text += "Пусто, не настроено"
            keyboard.append([InlineKeyboardButton(text="Список пуст", callback_data="-")])
        keyboard.append([InlineKeyboardButton(text="➕Добавить", callback_data="a/ad_input?k=addAd")])
        keyboard.append([
            InlineKeyboardButton(text="🏠 Админ-панель", callback_data="a/admin"),
            InlineKeyboardButton(text="↩️ Назад", callback_data="a/admin"),
        ])
        await self.sendMsg(text=text, keyboard=keyboard)

    async def delAdvertising(self, **kwargs):
        '''Удаление рекламы'''
        msg = await self.retChat()
        item_id = kwargs.get('id')[0]
        delData = await AdvertisingData().del_advertising(id=item_id)
        if delData:
            if self.query:
                await self.query.answer(text="✅Успешно удалено", cache_time=5)
            await self.index()
        else:
            await msgNotify(msg=msg, text="❕Ошибка удаления")


class Car:
    # Управление подборками
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
        markup = InlineKeyboardMarkup(inline_keyboard=kwargs['keyboard'])
        try:
            if self.query:
                await self.client.edit_message_text(
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    text=kwargs['text'],
                    reply_markup=markup,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            else:
                if len(bot_config.get('video') or '') > 24:
                    await self.client.send_video(
                        chat_id=msg.chat.id,
                        video=bot_config.get('video'),
                        caption=kwargs['text'],
                        reply_markup=markup,
                    )
                else:
                    await msg.answer(
                        text=kwargs['text'],
                        reply_markup=markup,
                        link_preview_options=LinkPreviewOptions(is_disabled=True),
                    )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                logging.warning(f"Car.sendMsg TelegramBadRequest: {e}")
        except TelegramAPIError as e:
            logging.warning(f"Car.sendMsg TelegramAPIError: {e}")

    async def inputBot(self, **kwargs):
        msg = await self.retChat()
        k = kwargs.get('k')[0] if kwargs.get('k') else None
        item_id = kwargs.get('id')[0] if kwargs.get('id') else None
        prompts = {
            "addCar": "Введите название подборки каналов",
            "title": f"Введите новое название подборки:{item_id}",
            "intro": f"Введите новое описание подборки:{item_id}",
            "total": f"Введите макс. число участников:{item_id}",
            "minSub": f"Введите мин. число подписчиков:{item_id}",
            "minRead": f"Введите мин. число просмотров:{item_id}",
        }
        prompt = prompts[k] if k and k in prompts else kwargs.get('text')[0]
        txt = f"🚒{prompt}"
        await msg.reply(text=esc(txt), reply_markup=ForceReply(selective=True))

    async def index(self, **kwargs):
        '''Главная страница управления подборками'''
        msg = await self.retChat()
        user = self.data.get('user')
        try:
            if user:
                bot_uname = str(bot_config.get('botUserName') or '').lstrip('@')
                text = (
                    f"<b>🚀Telegram ВП:</b>  @{esc(bot_uname)}\n\n"
                    f"<b>UID {esc(user[1])}</b> Уважаемый администратор {esc(user[3])}, здравствуйте:\n\n"
                    "<b>Бот автоматического взаимопиара</b>\n\n"
                    "👇Нажмите кнопку ниже для перехода к управлению подборками каналов\n"
                )
                keyboard = [
                    [InlineKeyboardButton(text="🏵️Подборки каналов🏵️", callback_data="a/car_channel")],
                    [InlineKeyboardButton(text="↩️ Назад", callback_data="a/admin")],
                ]
                await self.sendMsg(text=text, keyboard=keyboard)
        except (TelegramAPIError, Exception) as E:
            logging.error(f"Car.index error: {E}")
            await msg.answer(text=f'Ошибка: сделайте скриншот и обратитесь в поддержку {esc(E)}')

    async def channel_car(self, **kwargs):
        OFFSET, LIMIT = int(kwargs.get('page')[0]) if kwargs.get('page') else 0, 20
        fleet = CarData()
        fleetList, count = await fleet.get_fleet(OFFSET=OFFSET, LIMIT=LIMIT)
        keyboard = []
        text = (
            "Каналы — Зал подборок\n\n"
            "Выберите подборку ниже, а затем выберите канал для управления или подачи заявки.\n\n"
            "Обозначения:\n"
            "🚒Рассылка/🕛Ожидание Название|Участники-Макс.|Мин. подписчиков\n\n"
            "Нажмите на нужную подборку ниже"
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
                            callback_data=f"a/car_fleet?fleet={Cont[0]}",
                        )
                    )
                keyboard.append(row)
                row = []
            keyboard.append([
                InlineKeyboardButton(
                    text='⬅️Назад' if upPage >= 0 else '-',
                    callback_data=f"a/car_channel?page={upPage}" if upPage >= 0 else '-',
                ),
                InlineKeyboardButton(text=f"{currentPage}/{totalPages} стр.", callback_data="-"),
                InlineKeyboardButton(
                    text='➡️Вперёд' if currentPage < totalPages else '-',
                    callback_data=f"a/car_channel?page={dowPage}" if currentPage < totalPages else '-',
                ),
            ])
        else:
            keyboard.append([InlineKeyboardButton(text="Пусто / подборки не найдены", callback_data="-")])
        keyboard.append([InlineKeyboardButton(text="➕ Добавить подборку", callback_data="a/car_input?k=addCar")])
        keyboard.append([
            InlineKeyboardButton(text="🏠 Админ-панель", callback_data="a/admin"),
            InlineKeyboardButton(text="↩️ Назад", callback_data="a/car"),
        ])
        await self.sendMsg(text=text, keyboard=keyboard)

    async def channel_fleet_info(self, **kwargs):
        fleet_id = kwargs.get("fleet")[0]
        fleet = CarData()
        fleetInfo = await fleet.get_fleet_one(id=fleet_id)
        group_list = await fleet.get_fleet_group_list(id=fleet_id)
        if fleetInfo:
            text = (
                f"<b>Название подборки:</b> {esc(fleetInfo[1])}\n"
                f"<b>Описание подборки:</b> {esc(fleetInfo[2] or 'Не указано')}\n"
                f"<b>Участников (тек./макс.):</b> {fleetInfo[11]}/{fleetInfo[6]}\n"
                "<b>Тип подборки:</b> Канал\n"
                f"<b>Мин. подписчиков:</b> {fleetInfo[8]}\n"
                f"<b>Мин. просмотров:</b> {fleetInfo[9]}\n"
                f"<b>Статус рассылки:</b> {'🚒 Запущена' if fleetInfo[4] == 1 else '🕛 Остановлена'} \n\n"
                "<b>Список участников:</b>\n"
            )
            keyboard = []
            if group_list:
                group_id, row = [], 1
                for index, group in enumerate(group_list):
                    short_name = await truncate_string(group[3], 20)
                    text += f"{index + 1}.{html_link(short_name, group[6])} {round((group[5] or 0) / 1000, 1)}k\n"
                    group_id.append(
                        InlineKeyboardButton(
                            text=f"{index + 1}",
                            callback_data=f"a/car_ch_info?fleet={fleetInfo[0]}&group={group[0]}",
                        )
                    )
                    if index + 1 == 8 * row or ((len(group_list) - (index + 1)) < 8 and len(group_list) == (index + 1)):
                        row += 1
                        keyboard.append(group_id)
                        group_id = []
            else:
                text += "Сейчас нет участников в подборке\n"
            if fleetInfo[6] > fleetInfo[11]:
                text += "\n✅В подборке есть свободные места"
            else:
                text += "\n‼️Подборка заполнена"
            keyboard.append([InlineKeyboardButton(text="===== Редактирование подборки =====", callback_data="-")])
            keyboard.append([
                InlineKeyboardButton(text="Название", callback_data=f"a/car_input?k=title&id={fleetInfo[0]}"),
                InlineKeyboardButton(text="Описание", callback_data=f"a/car_input?k=intro&id={fleetInfo[0]}"),
                InlineKeyboardButton(text="Места", callback_data=f"a/car_input?k=total&id={fleetInfo[0]}"),
                InlineKeyboardButton(text="Подп.", callback_data=f"a/car_input?k=minSub&id={fleetInfo[0]}"),
                InlineKeyboardButton(text="Просм.", callback_data=f"a/car_input?k=minRead&id={fleetInfo[0]}"),
            ])
            keyboard.append([
                InlineKeyboardButton(
                    text=f"Статус: {'🚒 Запущена' if fleetInfo[4] == 1 else '🕛 Остановлена'}",
                    callback_data=f"a/car_ch_state?fleet={fleetInfo[0]}&state={fleetInfo[4]}",
                )
            ])
            keyboard.append([
                InlineKeyboardButton(text="🏠 Админ-панель", callback_data="a/admin"),
                InlineKeyboardButton(text="↩️ Назад", callback_data="a/car_channel"),
            ])
            await self.sendMsg(text=text, keyboard=keyboard)
        else:
            if self.query:
                await self.query.answer("Подборка не найдена", show_alert=True)

    async def channel_fleet_state(self, **kwargs):
        msg = await self.retChat()
        fleet_id, state = kwargs.get("fleet")[0], kwargs.get("state")[0]
        carData = CarData()
        if state == '0':
            await carData.put_car_state(text=1, id=fleet_id)
            await msgNotify(msg=msg, text='Рассылка запущена')
        else:
            await carData.put_car_state(text=0, id=fleet_id)
            await msgNotify(msg=msg, text='Рассылка остановлена')
        await self.channel_fleet_info(fleet=[fleet_id])

    async def channel_info(self, **kwargs):
        group_id = kwargs.get('group')[0]
        car = CarData()
        group = await car.get_user_group_one(id=group_id)
        if not group:
            if self.query:
                return await self.query.answer("Канал не найден", show_alert=True)
            return
        fleetInfo = await car.get_fleet_one(id=group[11])
        user = await car.get_user(id=group[12])
        notify = await car.get_notify_msg(user=user[0], group=group[0]) if user else None
        applicant = (
            html_link(user[3], f"https://t.me/{user[2]}")
            if user and user[2] and user[2] != 'Нет'
            else esc(user[3] if user else 'Неизвестно')
        )
        text = (
            f"<b>Название подборки:</b> {esc(fleetInfo[1] if fleetInfo else 'Не выбрана')}\n"
            "<b>Тип подборки:</b> Канал\n"
            f"<b>Описание подборки:</b> {esc((fleetInfo[2] or 'Не указано') if fleetInfo else '-')}\n"
            f"<b>Участников (тек./макс.):</b> {f'{fleetInfo[11]}/{fleetInfo[6]}' if fleetInfo else '-'}\n"
            f"<b>Мин. подписчиков:</b> {fleetInfo[8] if fleetInfo else '-'}\n"
            f"<b>Мин. просмотров:</b> {fleetInfo[9] if fleetInfo else '-'}\n\n"
            f"<b>ID канала:</b> {esc(group[1])}\n"
            f"<b>Канал:</b> {html_link(group[3], group[6])}\n"
            f"<b>Подписчиков:</b> {group[5]}\n"
            f"<b>ID заявителя:</b> {esc(user[1] if user else '-')}\n"
            f"<b>Заявитель:</b> {applicant}\n"
            f"<b>Статус заявки:</b> {esc(notify[3] if notify else 'Неизвестно')} "
        )
        keyboard = []
        if group[10] == 2:
            keyboard.append([InlineKeyboardButton(text="⏬ Снять с подборки", callback_data=f"a/car_toggle?group={group[0]}")])
        elif group[10] in [0, 1]:
            keyboard.append([InlineKeyboardButton(text="⏫ Добавить в подборку", callback_data=f"a/car_toggle?group={group[0]}")])
        if group[10] == 10:
            keyboard.append([InlineKeyboardButton(text="🟢 Разблокировать", callback_data=f"a/car_ban?group={group[0]}")])
        else:
            keyboard.append([InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"a/car_ban?group={group[0]}")])
        keyboard.append([
            InlineKeyboardButton(text="🏠 Админ-панель", callback_data="a/admin"),
            InlineKeyboardButton(
                text="↩️ Назад",
                callback_data=f"a/car_fleet?fleet={fleetInfo[0]}" if fleetInfo else "a/car_channel",
            ),
        ])
        await self.sendMsg(text=text, keyboard=keyboard)

    async def downGroup(self, **kwargs):
        '''Снять или добавить в подборку'''
        car = CarData()
        group = await car.get_user_group_one(id=kwargs.get('group')[0])
        if not group:
            if self.query:
                return await self.query.answer("Канал не найден", show_alert=True)
            return
        if group[10] == 2:
            await car.put_car_pass_review(group=group, state=0, label="🔴 Канал снят с подборки администратором")
        elif group[10] in [0, 1]:
            invite_url = None
            if "/+" not in str(group[6] or '') and "joinchat/" not in str(group[6] or ''):
                try:
                    link = await self.client.create_chat_invite_link(to_peer_id(group[1]))
                    invite_url = link.invite_link
                except TelegramAPIError:
                    invite_url = None
            await car.put_car_pass_review(
                group=group,
                state=2,
                label="🟢 Канал добавлен в подборку администратором",
                url=invite_url,
            )
        await self.channel_info(group=[kwargs.get('group')[0]])
        await self.reviewNotify(group=[kwargs.get('group')[0]])

    async def banGroup(self, **kwargs):
        car = CarData()
        group = await car.get_user_group_one(id=kwargs.get('group')[0])
        if not group:
            if self.query:
                return await self.query.answer("Канал не найден", show_alert=True)
            return
        if group[10] == 10:
            await car.put_car_pass_review(group=group, state=0, label="🟢 Блокировка канала снята")
        else:
            await car.put_car_pass_review(group=group, state=10, label="🚫 Канал заблокирован администратором")
        await self.channel_info(group=[kwargs.get('group')[0]])
        await self.reviewNotify(group=[kwargs.get('group')[0]])

    async def reviewNotify(self, **kwargs):
        '''Формирование уведомления пользователю'''
        car = CarData()
        group = await car.get_user_group_one(id=kwargs.get('group')[0])
        if not group:
            return
        fleet = await car.get_fleet_one(id=group[11])
        toUser = await car.get_user(id=group[12])
        if not toUser:
            return
        notify = await car.get_notify_msg(user=toUser[0], group=group[0])
        applicant = (
            html_link(toUser[3], f"https://t.me/{toUser[2]}")
            if toUser[2] and toUser[2] != 'Нет'
            else esc(toUser[3])
        )
        text = (
            "<b>📣Системное уведомление</b>📣\n"
            f"<b>Название подборки:</b> {esc(fleet[1] if fleet else 'Не выбрана')}\n"
            "<b>Тип подборки:</b> Канал\n"
            f"<b>Описание подборки:</b> {esc((fleet[2] or 'Не указано') if fleet else '-')}\n"
            f"<b>Участников (тек./макс.):</b> {f'{fleet[11]}/{fleet[6]}' if fleet else '-'}\n"
            f"<b>Мин. подписчиков:</b> {fleet[8] if fleet else '-'}\n"
            f"<b>Мин. просмотров:</b> {fleet[9] if fleet else '-'}\n\n"
            f"<b>ID канала:</b> {esc(group[1])}\n"
            f"<b>Канал:</b> {html_link(group[3], group[6])}\n"
            f"<b>Подписчиков:</b> {group[5]}\n"
            f"<b>ID заявителя:</b> {esc(toUser[1])}\n"
            f"<b>Заявитель:</b> {applicant}\n"
            f"<b>Статус заявки:</b> {esc(notify[3] if notify else 'Неизвестно')} "
        )
        try:
            await self.client.send_message(
                chat_id=to_peer_id(toUser[1]),
                text=text,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
        except TelegramAPIError:
            msg = await self.retChat()
            await msgNotify(msg=msg, text='❗Не удалось уведомить пользователя', times=5)
        if len(str(bot_config.get("msgGroup") or "")) > 5:
            try:
                keyboards = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Участвовать в ВП", url=format_tg_url(bot_config.get('botUserName')))]
                ])
                await self.client.send_message(
                    chat_id=to_peer_id(bot_config["msgGroup"]),
                    text=text,
                    reply_markup=keyboards,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            except TelegramAPIError:
                msg = await self.retChat()
                await msgNotify(msg=msg, text='❗Не удалось уведомить группу сообщений', times=5)


class Review:
    # Модерация в админ-группе
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
        markup = InlineKeyboardMarkup(inline_keyboard=kwargs['keyboard'])
        try:
            if self.query:
                await self.client.edit_message_text(
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    text=kwargs['text'],
                    reply_markup=markup,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            else:
                if len(bot_config.get('video') or '') > 24:
                    await self.client.send_video(
                        chat_id=msg.chat.id,
                        video=bot_config.get('video'),
                        caption=kwargs['text'],
                        reply_markup=markup,
                    )
                else:
                    await msg.answer(
                        text=kwargs['text'],
                        reply_markup=markup,
                        link_preview_options=LinkPreviewOptions(is_disabled=True),
                    )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                logging.warning(f"Review.sendMsg TelegramBadRequest: {e}")
        except TelegramAPIError as e:
            logging.warning(f"Review.sendMsg TelegramAPIError: {e}")

    async def inputBot(self, **kwargs):
        msg = await self.retChat()
        group_id = kwargs.get('id')[0] if kwargs.get('id') else None
        prompt = f"Введите свою причину отказа:{group_id}" if group_id else kwargs.get('text')[0]
        txt = f"💭{prompt}"
        await msg.reply(text=esc(txt), reply_markup=ForceReply(selective=True))

    async def passReview(self, **kwargs):
        '''Одобрение заявки'''
        msg = await self.retChat()
        car = CarData()
        group = await car.get_user_group_one(id=kwargs.get('group')[0])
        if not group:
            return await msgNotify(msg=msg, text='❌Канал не найден', times=5)
        if not group[11] or int(group[11]) == 0:
            return await self.pickFleet(group=[group[0]])
        fleetInfo = await car.get_fleet_one(id=group[11])
        if not fleetInfo:
            return await self.pickFleet(group=[group[0]])
        elif not fleetInfo[6] > fleetInfo[11]:
            await car.put_car_pass_review(group=group, state=0, label='Отклонено: подборка заполнена')
            await msgNotify(msg=msg, text='❌Подборка заполнена, автоматический отказ', times=5)
            text, keyboard, user = await self.reviewNotify(group=[group[0]])
            return await self.sendReviewInfo(text=[text], keyboard=[keyboard], user_id=[user])
        try:
            link = await self.client.create_chat_invite_link(to_peer_id(group[1]))
            await car.put_car_pass_review(group=group, state=2, label='Одобрено', url=link.invite_link)
        except TelegramAPIError:
            await car.put_car_pass_review(group=group, state=0, label='Отклонено: нет прав на приглашение')
            await msgNotify(msg=msg, text='❌Нет прав на создание ссылки, заявка отклонена', times=5)
        text, keyboard, user = await self.reviewNotify(group=[group[0]])
        await self.sendReviewInfo(text=[text], keyboard=[keyboard], user_id=[user])

    async def pickFleet(self, **kwargs):
        '''Выбор подборки для добавления канала'''
        group_id = kwargs.get('group')[0]
        car = CarData()
        group = await car.get_user_group_one(id=group_id)
        if not group:
            if self.query:
                return await self.query.answer("❌ Канал не найден", show_alert=True)
            return
        fleetList, _ = await car.get_fleet(OFFSET=0, LIMIT=30)
        keyboard = []
        if fleetList:
            text = (
                f"<b>➕ Добавление канала «{esc(group[3])}» в подборку</b>\n\n"
                "Выберите подборку, в которую нужно добавить канал:"
            )
            for f in fleetList:
                status_icon = '🚒' if f[4] == 1 else '🕛'
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"{status_icon} {f[1]} ({f[11]}/{f[6]})",
                        callback_data=f"a/assign_fleet?group={group[0]}&fleet={f[0]}",
                    )
                ])
        else:
            text = (
                f"<b>➕ Добавление канала «{esc(group[3])}» в подборку</b>\n\n"
                "⚠️ Подборки ещё не созданы. Сначала создайте подборку каналов."
            )
            keyboard.append([InlineKeyboardButton(text="➕ Создать подборку", callback_data="a/car_input?k=addCar")])
        keyboard.append([InlineKeyboardButton(text="↩️ Назад", callback_data=f"a/review_back?group={group[0]}")])
        await self.sendMsg(text=text, keyboard=keyboard)

    async def assignFleet(self, **kwargs):
        '''Назначение канала в выбранную подборку и одобрение'''
        msg = await self.retChat()
        group_id, fleet_id = kwargs.get('group')[0], kwargs.get('fleet')[0]
        car = CarData()
        group = await car.get_user_group_one(id=group_id)
        if not group:
            return await msgNotify(msg=msg, text='❌Канал не найден', times=5)
        fleetInfo = await car.get_fleet_one(id=fleet_id)
        if not fleetInfo:
            return await msgNotify(msg=msg, text='❌Подборка не найдена', times=5)
        if not fleetInfo[6] > fleetInfo[11]:
            if self.query:
                return await self.query.answer('❌ В этой подборке нет свободных мест', show_alert=True)
            return await msgNotify(msg=msg, text='❌В этой подборке нет свободных мест', times=5)
        try:
            link = await self.client.create_chat_invite_link(to_peer_id(group[1]))
            await car.put_car_pass_review(
                group=group,
                state=2,
                label='Одобрено',
                url=link.invite_link,
                fleet_id=int(fleet_id),
            )
        except TelegramAPIError:
            await car.put_car_pass_review(
                group=group,
                state=0,
                label='Отклонено: нет прав на приглашение',
                fleet_id=int(fleet_id),
            )
            await msgNotify(msg=msg, text='❌Нет прав на создание ссылки, заявка отклонена', times=5)
        text, keyboard, user = await self.reviewNotify(group=[group[0]])
        await self.sendReviewInfo(text=[text], keyboard=[keyboard], user_id=[user])

    async def rejectReview(self, **kwargs):
        rejectText = await ConfigData().get_rejectText_list()
        content = []
        group_id = kwargs.get('group')[0]
        if rejectText:
            for audit in rejectText:
                content.append([
                    InlineKeyboardButton(
                        text=f"{audit[2]}",
                        callback_data=f"a/review_reason?group={group_id}&reason={audit[0]}",
                    )
                ])
        content.append([
            InlineKeyboardButton(text="🔡 Своя причина отказа", callback_data=f"a/custom_reason?id={group_id}"),
            InlineKeyboardButton(text="↩️ Назад", callback_data=f"a/review_back?group={group_id}"),
        ])
        text = (
            "✨✨✨✨✨✨✨✨✨✨✨✨\n\n"
            "======<b>🏆 Причина отказа 🏆</b>======\n"
            "Выберите причину отказа.\n"
            "Шаблоны причин настраиваются в конфигурации бота."
        )
        await self.sendMsg(text=text, keyboard=content)

    async def rejectReason(self, **kwargs):
        msg = await self.retChat()
        car = CarData()
        group = await car.get_user_group_one(id=kwargs.get('group')[0])
        if not group:
            return await msgNotify(msg=msg, text='❌Канал не найден')
        reply = {}
        if self.query:
            Text = await car.get_rejectText(id=kwargs.get('reason')[0])
            if not Text:
                return await self.query.answer("Шаблон причины не найден", show_alert=True)
            reply["Text"] = Text[2]
        else:
            reply["Text"] = kwargs.get('reason')[0]
            if msg.reply_to_message and msg.reply_to_message.reply_to_message:
                reply["reply_id"] = msg.reply_to_message.reply_to_message.message_id
        if await car.put_car_pass_review(group=group, state=0, label=f"Отклонено:{reply['Text']}"):
            text, keyboard, user = await self.reviewNotify(group=[group[0]])
            await self.sendReviewInfo(text=[text], keyboard=[keyboard], user_id=[user], reply_id=[reply.get("reply_id")])

    async def rejectBack(self, **kwargs):
        '''Возврат к деталям заявки'''
        text, keyboard, user = await self.reviewNotify(group=[kwargs.get("group")[0]])
        await self.sendMsg(text=text, keyboard=keyboard)

    async def reviewNotify(self, **kwargs):
        '''Формирование сообщения заявки'''
        car = CarData()
        group = await car.get_user_group_one(id=kwargs.get('group')[0])
        if not group:
            return "Канал не найден", [], None
        fleet = await car.get_fleet_one(id=group[11]) if group[11] else None
        toUser = await car.get_user(id=group[12])
        notify = await car.get_notify_msg(user=toUser[0], group=group[0]) if toUser else None
        applicant = (
            html_link(toUser[3], f"https://t.me/{toUser[2]}")
            if toUser and toUser[2] and toUser[2] != 'Нет'
            else esc(toUser[3] if toUser else 'Неизвестно')
        )
        text = (
            "<b>📣Системное уведомление</b>📣\n"
            f"<b>Название подборки:</b> {esc(fleet[1] if fleet else 'Не выбрана')}\n"
            "<b>Тип подборки:</b> Канал\n"
            f"<b>Описание подборки:</b> {esc((fleet[2] or 'Не указано') if fleet else '-')}\n"
            f"<b>Участников (тек./макс.):</b> {f'{fleet[11]}/{fleet[6]}' if fleet else '-'}\n"
            f"<b>Мин. подписчиков:</b> {fleet[8] if fleet else '-'}\n"
            f"<b>Мин. просмотров:</b> {fleet[9] if fleet else '-'}\n\n"
            f"<b>ID канала:</b> {esc(group[1])}\n"
            f"<b>Канал:</b> {html_link(group[3], group[6])}\n"
            f"<b>Подписчиков:</b> {group[5]}\n"
            f"<b>ID заявителя:</b> {esc(toUser[1] if toUser else '-')}\n"
            f"<b>Заявитель:</b> {applicant}\n"
        )
        keyboard = []
        status_label = esc(notify[3] if notify else 'Ожидает проверки')
        if group[10] == 1:
            text += f"<b>Статус заявки:</b> 🔵 {status_label} "
            keyboard.append([
                InlineKeyboardButton(text="🟢 Одобрить", callback_data=f"a/review_pass?group={group[0]}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"a/review_reject?group={group[0]}"),
            ])
            keyboard.append([InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"a/review_ban?group={group[0]}")])
        elif group[10] == 2:
            text += f"<b>Статус заявки:</b> 🟢 {status_label} "
            keyboard.append([InlineKeyboardButton(text="⏬ Снять с подборки", callback_data=f"a/review_down?group={group[0]}")])
            keyboard.append([InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"a/review_ban?group={group[0]}")])
        elif group[10] == 10:
            text += f"<b>Статус заявки:</b> 🚫 {status_label}"
            keyboard.append([InlineKeyboardButton(text="🟢 Разблокировать", callback_data=f"a/review_ban?group={group[0]}")])
        else:
            text += f"<b>Статус заявки:</b> ⚪ {status_label}"
            if fleet:
                keyboard.append([
                    InlineKeyboardButton(text="🟢 Добавить", callback_data=f"a/review_pass?group={group[0]}"),
                    InlineKeyboardButton(text="❌ Отклонить", callback_data=f"a/review_reject?group={group[0]}"),
                ])
                keyboard.append([
                    InlineKeyboardButton(text="➕ Выбрать подборку", callback_data=f"a/pick_fleet?group={group[0]}"),
                    InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"a/review_ban?group={group[0]}"),
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(text="➕ Добавить в подборку", callback_data=f"a/pick_fleet?group={group[0]}"),
                    InlineKeyboardButton(text="❌ Отклонить", callback_data=f"a/review_reject?group={group[0]}"),
                ])
                keyboard.append([InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"a/review_ban?group={group[0]}")])
        return text, keyboard, toUser

    async def sendReviewInfo(self, **kwargs):
        '''Отправка уведомления о результате проверки'''
        text, keyboard, user_id = kwargs.get("text")[0], kwargs.get("keyboard")[0], kwargs.get("user_id")[0]
        msg = await self.retChat()
        if kwargs.get("reply_id") and kwargs.get("reply_id")[0]:
            try:
                await self.client.edit_message_text(
                    chat_id=msg.chat.id,
                    message_id=kwargs.get("reply_id")[0],
                    text=text,
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            except TelegramAPIError as e:
                logging.warning(f"Ошибка редактирования сообщения проверки: {e}")
        else:
            await self.sendMsg(text=text, keyboard=keyboard)
        if user_id:
            try:
                await self.client.send_message(
                    chat_id=to_peer_id(user_id[1]),
                    text=text,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            except TelegramAPIError:
                await msgNotify(msg=msg, text='❗Не удалось уведомить пользователя', times=5)
        if len(str(bot_config.get("msgGroup") or "")) > 5:
            try:
                keyboards = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Участвовать в ВП", url=format_tg_url(bot_config.get('botUserName')))]
                ])
                await self.client.send_message(
                    chat_id=to_peer_id(bot_config["msgGroup"]),
                    text=text,
                    reply_markup=keyboards,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            except TelegramAPIError:
                await msgNotify(msg=msg, text='❗Не удалось уведомить группу сообщений', times=5)

    async def banGroup(self, **kwargs):
        car = CarData()
        group = await car.get_user_group_one(id=kwargs.get('group')[0])
        if not group:
            if self.query:
                return await self.query.answer("Канал не найден", show_alert=True)
            return
        if group[10] == 10:
            await car.put_car_pass_review(group=group, state=0, label="Ваш канал разблокирован")
        else:
            await car.put_car_pass_review(group=group, state=10, label="Ваш канал заблокирован администратором")
        text, keyboard, user = await self.reviewNotify(group=kwargs.get('group'))
        await self.sendReviewInfo(text=[text], keyboard=[keyboard], user_id=[user])

    async def downGroup(self, **kwargs):
        '''Снять с подборки'''
        car = CarData()
        group = await car.get_user_group_one(id=kwargs.get('group')[0])
        if not group:
            if self.query:
                return await self.query.answer("Канал не найден", show_alert=True)
            return
        await car.put_car_pass_review(group=group, state=0, label="Ваш канал снят с подборки администратором")
        text, keyboard, user = await self.reviewNotify(group=kwargs.get('group'))
        await self.sendReviewInfo(text=[text], keyboard=[keyboard], user_id=[user])


class Group:
    # Управление каналами
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
        markup = InlineKeyboardMarkup(inline_keyboard=kwargs['keyboard'])
        try:
            if self.query:
                await self.client.edit_message_text(
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    text=kwargs['text'],
                    reply_markup=markup,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            else:
                if len(bot_config.get('video') or '') > 24:
                    await self.client.send_video(
                        chat_id=msg.chat.id,
                        video=bot_config.get('video'),
                        caption=kwargs['text'],
                        reply_markup=markup,
                    )
                else:
                    await msg.answer(
                        text=kwargs['text'],
                        reply_markup=markup,
                        link_preview_options=LinkPreviewOptions(is_disabled=True),
                    )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                logging.warning(f"Group.sendMsg TelegramBadRequest: {e}")
        except TelegramAPIError as e:
            logging.warning(f"Group.sendMsg TelegramAPIError: {e}")

    async def inputBot(self, **kwargs):
        msg = await self.retChat()
        k = kwargs.get('k')[0] if kwargs.get('k') else None
        prompt = "Введите название канала:" if k == "search" else kwargs.get('text')[0]
        txt = f"🏵️‍{prompt}"
        await msg.reply(text=esc(txt), reply_markup=ForceReply(selective=True))

    async def index(self, **kwargs):
        OFFSET, LIMIT = int(kwargs.get('page')[0]) if kwargs.get('page') else 0, 20
        search = kwargs.get('search')
        groupData = GroupData()
        group = await groupData.get_group_list(OFFSET=OFFSET, LIMIT=LIMIT, search=search)
        group_count = await groupData.get_group_index_count()
        keyboard = []
        text = (
            "Каналы — Управление\n\n"
            f"Всего каналов: {group_count[1]} | В подборке {group_count[2]} | Снято {group_count[1] - group_count[2]}\n"
            "Обозначения:\n"
            "🏵️‍Канал — Название\n\n"
            "Нажмите на кнопку ниже для подробностей"
        )
        if group and group_count:
            totalPages, currentPage = math.ceil(group_count[1] / LIMIT) or 1, math.ceil(OFFSET / LIMIT) + 1
            upPage, dowPage = OFFSET - LIMIT, OFFSET + LIMIT
            for key in group:
                keyboard.append([InlineKeyboardButton(text=f"🏵️‍-{key[3]} ", callback_data=f"a/group_info?group={key[0]}")])
            keyboard.append([
                InlineKeyboardButton(
                    text='⬅️Назад' if upPage >= 0 else '-',
                    callback_data=f"a/group?page={upPage}" if upPage >= 0 else '-',
                ),
                InlineKeyboardButton(text=f"{currentPage}/{totalPages} стр.", callback_data="-"),
                InlineKeyboardButton(
                    text='➡️Вперёд' if currentPage < totalPages else '-',
                    callback_data=f"a/group?page={dowPage}" if currentPage < totalPages else '-',
                ),
            ])
        else:
            keyboard.append([InlineKeyboardButton(text="Пусто / не найдено", callback_data="-")])
        keyboard.append([InlineKeyboardButton(text="🔎 Поиск", callback_data="a/group_input?k=search")])
        keyboard.append([
            InlineKeyboardButton(text="🏠 Админ-панель", callback_data="a/admin"),
            InlineKeyboardButton(text="↩️ Назад", callback_data="a/admin"),
        ])
        await self.sendMsg(text=text, keyboard=keyboard)

    async def groupInfo(self, **kwargs):
        group_id = kwargs.get('group')[0]
        groupData = GroupData()
        group_info = await groupData.get_group_info(id=group_id)
        if group_info:
            user = await groupData.get_user(id=group_info[12])
            fleet = await groupData.get_fleet_one(id=group_info[11])
            group_type = 'Канал'
            group_fleet_state = (
                "⚪ Свободен" if group_info[10] == 0
                else "🟡 На проверке" if group_info[10] == 1
                else "🟢 В подборке" if group_info[10] == 2
                else "🚫 Заблокирован" if group_info[10] == 10
                else "Неизвестный статус"
            )
            text = (
                "✨✨✨✨✨✨✨✨✨✨✨✨\n"
                f"💡<b>Данные: {group_type}</b>💡\n\n"
                f"〖ID ({group_type})〗{esc(group_info[1])}\n"
                f"〖Юзернейм〗{esc('@' + group_info[2] if group_info[2] else 'Не указан')}\n"
                f"〖Название〗{esc(group_info[3])}\n"
                f"〖Подписчиков〗{group_info[5]}\n"
                f"〖ID сообщения ВП〗{group_info[7]}\n"
                f"〖Приведено подписчиков〗{group_info[9]}\n"
                f"〖Статус〗{group_fleet_state}\n"
                f"〖Подборка〗{esc(fleet[1] if fleet else 'Не выбрана')}\n\n"
                f"〖ID владельца〗{esc(user[1] if user else '-')}\n"
                f"〖Владелец〗{esc(user[3] if user else 'Неизвестно')}\n"
            )
            keyboard = []
            if group_info[10] == 10:
                keyboard.append([InlineKeyboardButton(text="🟢 Разблокировать", callback_data=f"a/group_ban?group={group_info[0]}")])
            else:
                keyboard.append([InlineKeyboardButton(text="🚫 Заблокировать", callback_data=f"a/group_ban?group={group_info[0]}")])
            keyboard.append([
                InlineKeyboardButton(text="🏠 Админ-панель", callback_data="a/admin"),
                InlineKeyboardButton(text="↩️ Назад", callback_data="a/group"),
            ])
            await self.sendMsg(text=text, keyboard=keyboard)
        else:
            if self.query:
                await self.query.answer("Ошибка: канал не существует или удалён")

    async def banGroup(self, **kwargs):
        car = CarData()
        group = await car.get_user_group_one(id=kwargs.get('group')[0])
        if not group:
            if self.query:
                return await self.query.answer("Ошибка: канал не существует или удалён")
            return
        if group[10] == 10:
            await car.put_car_pass_review(group=group, state=0, label="🟢 Блокировка канала снята")
        else:
            await car.put_car_pass_review(group=group, state=10, label="🚫 Канал заблокирован администратором")
        await self.groupInfo(group=[kwargs.get('group')[0]])
        await self.reviewNotify(group=[kwargs.get('group')[0]])

    async def reviewNotify(self, **kwargs):
        '''Формирование уведомления пользователю'''
        car = CarData()
        group = await car.get_user_group_one(id=kwargs.get('group')[0])
        if not group:
            return
        toUser = await car.get_user(id=group[12])
        if not toUser:
            return
        notify = await car.get_notify_msg(user=toUser[0], group=group[0])
        applicant = (
            html_link(toUser[3], f"https://t.me/{toUser[2]}")
            if toUser[2] and toUser[2] != 'Нет'
            else esc(toUser[3])
        )
        text = (
            "<b>📣Системное уведомление</b>📣\n"
            f"<b>ID канала:</b> {esc(group[1])}\n"
            f"<b>Канал:</b> {html_link(group[3], group[6])}\n"
            f"<b>Подписчиков:</b> {group[5]}\n"
            f"<b>ID заявителя:</b> {esc(toUser[1])}\n"
            f"<b>Заявитель:</b> {applicant}\n"
            f"<b>Статус заявки:</b> {esc(notify[3] if notify else 'Неизвестно')} "
        )
        try:
            await self.client.send_message(
                chat_id=to_peer_id(toUser[1]),
                text=text,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
        except TelegramAPIError:
            msg = await self.retChat()
            await msgNotify(msg=msg, text='❗Не удалось уведомить пользователя', times=5)
        if len(str(bot_config.get("msgGroup") or "")) > 5:
            try:
                keyboards = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Участвовать в ВП", url=format_tg_url(bot_config.get('botUserName')))]
                ])
                await self.client.send_message(
                    chat_id=to_peer_id(bot_config["msgGroup"]),
                    text=text,
                    reply_markup=keyboards,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            except TelegramAPIError:
                msg = await self.retChat()
                await msgNotify(msg=msg, text='❗Не удалось уведомить группу сообщений', times=5)


class User:
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
        markup = InlineKeyboardMarkup(inline_keyboard=kwargs['keyboard'])
        try:
            if self.query:
                await self.client.edit_message_text(
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    text=kwargs['text'],
                    reply_markup=markup,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            else:
                if len(bot_config.get('video') or '') > 24:
                    await self.client.send_video(
                        chat_id=msg.chat.id,
                        video=bot_config.get('video'),
                        caption=kwargs['text'],
                        reply_markup=markup,
                    )
                else:
                    await msg.answer(
                        text=kwargs['text'],
                        reply_markup=markup,
                        link_preview_options=LinkPreviewOptions(is_disabled=True),
                    )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                logging.warning(f"User.sendMsg TelegramBadRequest: {e}")
        except TelegramAPIError as e:
            logging.warning(f"User.sendMsg TelegramAPIError: {e}")

    async def inputBot(self, **kwargs):
        msg = await self.retChat()
        k = kwargs.get('k')[0] if kwargs.get('k') else None
        prompt = "Введите юзернейм или имя:" if k == "search" else kwargs.get('text')[0]
        txt = f"👨‍💻{prompt}"
        await msg.reply(text=esc(txt), reply_markup=ForceReply(selective=True))

    async def getUser(self, **kwargs):
        WHERE, OFFSET, LIMIT = "", 0, 20
        params = []
        if kwargs.get('page'):
            OFFSET = int(kwargs.get('page')[0])
        search_val = None
        if kwargs.get('search'):
            search_val = kwargs.get('search')[0] if isinstance(kwargs.get('search'), list) else kwargs.get('search')
            WHERE += "AND (full_name LIKE ? OR username LIKE ?) "
            params.extend([f"%{search_val}%", f"%{search_val}%"])
        userType = int(kwargs.get('type')[0]) if kwargs.get('type') else 0
        if search_val and not kwargs.get('type'):
            base_where = "admin IN (0, 1, 2)"
            count_params = list(params)
            list_params = list(params) + [LIMIT, OFFSET]
        else:
            base_where = "admin=?"
            count_params = [userType] + params
            list_params = [userType] + params + [LIMIT, OFFSET]
        total_row = await db.select(
            f"SELECT COUNT(*) FROM chat_user WHERE {base_where} {WHERE}",
            tuple(count_params),
        )
        counts_row = await db.select(
            "SELECT (SELECT COUNT(*) FROM chat_user WHERE admin=0) AS state_count,"
            "(SELECT COUNT(*) FROM chat_user WHERE admin=1) AS admin_count"
        )
        total_count = total_row[0][0] if total_row else 0
        state_count = counts_row[0][0] if counts_row else 0
        admin_count = counts_row[0][1] if counts_row else 0
        userList = await db.select(
            f"SELECT * FROM chat_user WHERE {base_where} {WHERE} ORDER BY id DESC LIMIT ? OFFSET ?",
            tuple(list_params),
        )
        if userList and len(userList) > 0:
            totalPages, currentPage = (math.ceil(total_count / LIMIT) or 1), int(OFFSET / LIMIT) + 1
            upPage, dowPage = OFFSET - LIMIT, OFFSET + LIMIT
            content = []
            for user in userList:
                content.append([
                    InlineKeyboardButton(
                        text=f"{'👮‍' if user[5] == 1 else '👑' if user[5] == 2 else '👳‍'}{user[3]}",
                        callback_data=f"a/user_info?user={user[0]}",
                    )
                ])
            search_q = f"&search={search_val}" if search_val else ""
            type_q = f"&type={userType}" if (kwargs.get('type') or not search_val) else ""
            content.append([
                InlineKeyboardButton(
                    text='Назад' if upPage >= 0 else '-',
                    callback_data=f"a/user?page={upPage}{type_q}{search_q}" if upPage >= 0 else '-',
                ),
                InlineKeyboardButton(text=f"{currentPage}/{totalPages}", callback_data="-"),
                InlineKeyboardButton(
                    text='Вперёд' if currentPage < totalPages else '-',
                    callback_data=f"a/user?page={dowPage}{type_q}{search_q}" if currentPage < totalPages else '-',
                ),
            ])
        else:
            content = [[InlineKeyboardButton(text="Пусто / нет пользователей", callback_data="-")]]
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f"{'🟢' if userType == 0 and not search_val else ''}Обычные",
                    callback_data="a/user?type=0",
                ),
                InlineKeyboardButton(
                    text=f"{'🟢' if userType == 1 else ''}Администраторы",
                    callback_data="a/user?type=1",
                ),
            ],
            [InlineKeyboardButton(text="Поиск пользователя", callback_data="a/user_input?k=search")],
            [InlineKeyboardButton(text="↩️ Назад", callback_data="a/admin")],
        ]
        text = (
            "✨✨✨✨✨✨✨✨✨✨✨✨\n\n"
            "======<b>🏆 Поиск пользователей 🏆</b>======\n"
            f"〖Количество〗{total_count} чел.\n"
            f"👮‍Администраторы: {admin_count}\n"
            f"👳Пользователи: {state_count}\n"
        )
        await self.sendMsg(text=text, keyboard=content + keyboard)

    async def userInfo(self, **kwargs):
        userID = kwargs.get('user')[0]
        user = await db.select("SELECT * FROM chat_user WHERE id = ?", (userID,))
        if not user:
            if self.query:
                return await self.query.answer("Пользователь не найден", show_alert=True)
            return
        text = (
            "✨✨✨✨✨✨✨✨✨✨✨✨\n"
            "💡<b>Профиль пользователя</b>💡\n\n"
            f"〖ID пользователя〗<code>{esc(user[0][1] or 'Нет')}</code> (нажмите для копирования)\n"
            f"〖Юзернейм〗<code>{esc(user[0][2] or 'Нет')}</code> (нажмите для копирования)\n"
            f"〖Имя〗<code>{esc(user[0][3] or 'Нет')}</code> (нажмите для копирования)\n"
            f"〖Статус〗{'🟢Активен' if user[0][4] == 0 else '🔴Заблокирован'}\n"
            f"〖Права〗{'👮‍Администратор' if user[0][5] == 1 else '👑Супер-админ' if user[0][5] == 2 else '👳‍Пользователь'}\n"
        )
        keyboard = []
        if user[0][5] == 0:
            keyboard.append([InlineKeyboardButton(text="🔐Назначить админом", callback_data=f"a/set_admin?user={user[0][0]}&p=0")])
        elif user[0][5] == 1:
            keyboard.append([InlineKeyboardButton(text="🔓Снять админа", callback_data=f"a/set_admin?user={user[0][0]}&p=1")])
        if user[0][4] == 0:
            keyboard.append([InlineKeyboardButton(text="🚷 Заблокировать", callback_data=f"a/ban_user?user={user[0][0]}")])
        else:
            keyboard.append([InlineKeyboardButton(text="✅ Разблокировать", callback_data=f"a/ban_user?user={user[0][0]}")])
        keyboard.append([InlineKeyboardButton(text="↩️ Назад", callback_data="a/user")])
        await self.sendMsg(text=text, keyboard=keyboard)

    async def setAdmin(self, **kwargs):
        msg = await self.retChat()
        if kwargs.get('user'):
            actor_id = self.query.from_user.id if self.query and self.query.from_user else msg.chat.id
            user = await db.select("SELECT * FROM chat_user WHERE chat_id = ?", (str(actor_id),))
            if user and user[0][5] == 2:
                pa = 1 if kwargs.get('p')[0] == '0' else 0
                if await db.update("UPDATE chat_user SET admin=? WHERE id=?", (pa, kwargs.get('user')[0])):
                    await self.query.answer(text='Права администратора обновлены', show_alert=True)
                    await self.userInfo(user=kwargs.get('user'))
                else:
                    await self.query.answer(text='Ошибка базы данных', show_alert=True)
            elif user and user[0][5] == 1:
                await self.query.answer(text='Ошибка: у вас нет прав назначать администраторов', show_alert=True)
            else:
                await self.query.answer(text='Ошибка: пользователь не найден', show_alert=True)

    async def banUser(self, **kwargs):
        user = await db.select("SELECT * FROM chat_user WHERE id=?", (kwargs.get('user')[0],))
        if not user:
            if self.query:
                return await self.query.answer("Пользователь не найден", show_alert=True)
            return
        if user[0][4] == 1:
            await db.update("UPDATE chat_user SET state=0 WHERE id=?", (user[0][0],))
            await self.reviewNotify(user=[user[0][0]])
        else:
            await db.update("UPDATE chat_user SET state=1 WHERE id=?", (user[0][0],))
            await self.reviewNotify(user=[user[0][0]])
        await self.userInfo(user=[kwargs.get('user')[0]])

    async def backReview(self, **kwargs):
        # Удаление текущего сообщения
        msg = await self.retChat()
        try:
            await self.client.delete_message(msg.chat.id, msg.message_id)
        except TelegramAPIError as e:
            logging.debug(f"Ошибка удаления сообщения: {e}")

    async def reviewNotify(self, **kwargs):
        '''Формирование уведомления пользователю'''
        car = CarData()
        toUser = await car.get_user(id=kwargs.get('user')[0])
        if not toUser:
            return
        text = (
            "✨✨✨✨✨✨✨✨✨✨✨✨\n"
            "💡<b>Профиль пользователя</b>💡\n\n"
            f"〖ID пользователя〗<code>{esc(toUser[1] or 'Нет')}</code> (нажмите для копирования)\n"
            f"〖Юзернейм〗<code>{esc(toUser[2] or 'Нет')}</code> (нажмите для копирования)\n"
            f"〖Имя〗<code>{esc(toUser[3] or 'Нет')}</code> (нажмите для копирования)\n"
            f"〖Статус〗{'🟢Активен' if toUser[4] == 0 else '🔴Заблокирован'}\n"
            f"〖Уведомление〗<b> {'🟢 Ваш аккаунт разблокирован администратором' if toUser[4] == 0 else '🔴 Ваш аккаунт заблокирован администратором'}</b>"
        )
        try:
            await self.client.send_message(
                chat_id=to_peer_id(toUser[1]),
                text=text,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
        except TelegramAPIError:
            msg = await self.retChat()
            await msgNotify(msg=msg, text='❗Не удалось уведомить пользователя', times=5)
        if len(str(bot_config.get("msgGroup") or "")) > 5:
            try:
                keyboards = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Участвовать в ВП", url=format_tg_url(bot_config.get('botUserName')))]
                ])
                await self.client.send_message(
                    chat_id=to_peer_id(bot_config["msgGroup"]),
                    text=text,
                    reply_markup=keyboards,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            except TelegramAPIError:
                msg = await self.retChat()
                await msgNotify(msg=msg, text='❗Не удалось уведомить группу сообщений', times=5)


class BotBlacklist:
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
        markup = InlineKeyboardMarkup(inline_keyboard=kwargs['keyboard'])
        try:
            if self.query:
                await self.client.edit_message_text(
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    text=kwargs['text'],
                    reply_markup=markup,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            else:
                if len(bot_config.get('video') or '') > 24:
                    await self.client.send_video(
                        chat_id=msg.chat.id,
                        video=bot_config.get('video'),
                        caption=kwargs['text'],
                        reply_markup=markup,
                    )
                else:
                    await msg.answer(
                        text=kwargs['text'],
                        reply_markup=markup,
                        link_preview_options=LinkPreviewOptions(is_disabled=True),
                    )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                logging.warning(f"BotBlacklist.sendMsg TelegramBadRequest: {e}")
        except TelegramAPIError as e:
            logging.warning(f"BotBlacklist.sendMsg TelegramAPIError: {e}")

    async def botInput(self, **kwargs):
        msg = await self.retChat()
        k = kwargs.get('k')[0] if kwargs.get('k') else None
        if k == "addBot":
            prompt = "Введите юзернейм бота:Пример:@Xxbot"
        elif k == "editBot":
            item_id = kwargs.get('id')[0]
            prompt = f"Введите новый юзернейм бота:{item_id}"
        else:
            prompt = kwargs.get('text')[0]
        txt = f"🤖{prompt}"
        await msg.reply(text=esc(txt), reply_markup=ForceReply(selective=True))

    async def index(self, **kwargs):
        '''Чёрный список ботов'''
        bl_list = await BotBlacklistDate().get_bot_blacklist_list()
        text = (
            "======<b>🏆 Чёрный список ботов 🏆</b>======\n"
            "При подаче заявки и при рассылке проверяется наличие ботов из ЧС; при обнаружении канал снимается с подборки\n"
            "Инструкция: введите юзернейм бота с @, например @xxxbot\n"
            "Обозначения: ➕Добавить ❌Удалить 🖍Изменить\n\n"
            "🚫<b>Список заблокированных ботов:</b>\n"
        )
        keyboard = []
        if bl_list:
            for index, item in enumerate(bl_list):
                text += f"{index + 1}. {esc(item[1])}\n"
                keyboard.append([
                    InlineKeyboardButton(text=f"{index + 1}.{item[1]}", callback_data="-"),
                    InlineKeyboardButton(text="❌ Удалить", callback_data=f"a/del_bot_bl?id={item[0]}"),
                    InlineKeyboardButton(text="🖍 Изменить", callback_data=f"a/bot_bl_input?k=editBot&id={item[0]}"),
                ])
        else:
            text += "Пусто, не настроено"
            keyboard.append([InlineKeyboardButton(text="Список пуст", callback_data="-")])
        keyboard.append([InlineKeyboardButton(text="➕Добавить", callback_data="a/bot_bl_input?k=addBot")])
        keyboard.append([
            InlineKeyboardButton(text="🏠 Админ-панель", callback_data="a/admin"),
            InlineKeyboardButton(text="↩️ Назад", callback_data="a/admin"),
        ])
        await self.sendMsg(text=text, keyboard=keyboard)

    async def delBotBlacklist(self, **kwargs):
        '''Удаление бота из чёрного списка'''
        msg = await self.retChat()
        item_id = kwargs.get('id')[0]
        delData = await BotBlacklistDate().del_bot_blacklist(id=item_id)
        if delData:
            if self.query:
                await self.query.answer(text="✅Успешно удалено", cache_time=5)
            await self.index()
        else:
            await msgNotify(msg=msg, text="❕Ошибка удаления")
