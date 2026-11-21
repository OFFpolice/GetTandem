from config import *
from public.method import *
from data.data import *
class Index:
    def __init__(self, Client:Client, Query:CallbackQuery=None, Msg:Message=None, Data=None):
        self.client =Client
        self.query = Query
        self.msg = Msg
        self.data= Data
    async def retChat(self):
        if self.query:
            return self.query.message
        else:
            return self.msg
    async def sendMsg(self,**kwargs):
        msg = await self.retChat()
        try:
            if self.query:
                await self.client.edit_message_text(chat_id=msg.chat.id, message_id=msg.id, text=kwargs['text'],
                                                    reply_markup=InlineKeyboardMarkup(kwargs['keyboard']),
                                                    disable_web_page_preview=True)
            else:
                if len(bot_config.get('video'))>24:
                    await self.client.send_video(chat_id=msg.chat.id, video=bot_config.get('video'), caption=kwargs['text'],
                                                 reply_markup=InlineKeyboardMarkup(kwargs['keyboard']))
                else:
                    await msg.reply_text(text=kwargs['text'], reply_markup=InlineKeyboardMarkup(kwargs['keyboard']),
                                         disable_web_page_preview=True)
        except RPCError as e:
            print(e)
    async def welcome(self,**kwargs):
        msg = await self.retChat()
        user=self.data.get('user')
        Reply = [['Помощь']]
        if user[5] in [1, 2]:
            Reply = [['⚙Админ-панель']]
        text = f"**Добро пожаловать в: {bot_config.get('botName')}**\n\n" \
               f"{bot_config.get('indexTxt')}\n\n"
        await msg.reply_text(text, reply_markup=ReplyKeyboardMarkup(Reply, resize_keyboard=True),
                                 disable_web_page_preview=True)
    async def index(self,**kwargs):
        msg =await self.retChat()
        user=self.data.get('user')
        try:
            if user:
                text = f"======🏆 Главная меню подборок 🏆======\n\n" \
                       f"**🚀Telegram ВП:**  @{bot_config.get('botUserName')}\n\n" \
                       f"**UID {user[1]}** Уважаемый(ая) {user[3]}, здравствуйте:\n\n" \
                       f"**🔗Бот для взаимного продвижения и подборок🔗**\n\n" \
                       f"**Инструкция:** Добавьте этого бота в свою [группу](https://t.me/{bot_config.get('botUserName').replace('@', '')}?startgroup=true) | [канал](https://t.me/{bot_config.get('botUserName').replace('@', '')}?startchannel=true) и выдайте права администратора🔶\n" \
                       f"**Права администратора:** отправка сообщений / редактирование чужих сообщений / удаление чужих сообщений / приглашение пользователей. Без этих прав бот не сможет работать корректно\n\n" \
                       f"⚠️ Строго запрещено публиковать материалы с участием несовершеннолетних, зоофилию, насилие, кровь, шок-контент, политику, оружие и т.д. 【[Подробнее в правилах](https://t.me/hufen/3)】\n"
                keyboard=[
                    [InlineKeyboardButton("📍Добавить бота в группу",url=f"https://t.me/{bot_config['botUserName'].replace('@', '')}?startgroup=true"),
                     InlineKeyboardButton("📍Добавить бота в канал",url=f"https://t.me/{bot_config['botUserName'].replace('@', '')}?startchannel=true")],
                    [InlineKeyboardButton("⏺Подборки каналов",callback_data="r/channel"),InlineKeyboardButton("⏺Подборки групп",callback_data="r/group_fleets")],
                    [InlineKeyboardButton("❔Инструкция", url=f"https://t.me/{bot_config['publicGroup']}"),InlineKeyboardButton("📢Чат взаимопиара",url="https://t.me/hutui")],
                ]
                await self.sendMsg(text=text,keyboard=keyboard)
        except (RPCError,Exception) as E:
            print(E)
            await msg.reply_text(text=f'Ошибка: сделайте скриншот и обратитесь в поддержку {E}')

class Channel:
    def __init__(self, Client:Client, Query:CallbackQuery=None, Msg:Message=None, Data=None):
        self.client =Client
        self.query = Query
        self.msg = Msg
        self.data= Data
    async def retChat(self):
        if self.query:
            return self.query.message
        else:
            return self.msg
    async def sendMsg(self,**kwargs):
        msg = await self.retChat()
        try:
            if self.query:
                await self.client.edit_message_text(chat_id=msg.chat.id, message_id=msg.id, text=kwargs['text'],
                                                    reply_markup=InlineKeyboardMarkup(kwargs['keyboard']),
                                                    disable_web_page_preview=True)
            else:
                if len(bot_config.get('video'))>24:
                    await self.client.send_video(chat_id=msg.chat.id, video=bot_config.get('video'), caption=kwargs['text'],
                                                 reply_markup=InlineKeyboardMarkup(kwargs['keyboard']))
                else:
                    await msg.reply_text(text=kwargs['text'], reply_markup=InlineKeyboardMarkup(kwargs['keyboard']),
                                         disable_web_page_preview=True)
        except RPCError as e:
            print(e)
    async def index(self,**kwargs):
        OFFSET, LIMIT = int(kwargs.get('page')[0]) if kwargs.get('page') else 0, 30
        fleet = ChannelFleetList()
        fleetList,count = fleet.get_fleet(OFFSET=OFFSET,LIMIT=LIMIT)
        group_count= fleet.get_group_count()
        keyboard = []
        text = f"Каналы — Зал подборок\n\n" \
               f"Количество подборок: {len(fleetList)}\n" \
               f"Количество каналов: {group_count}\n" \
               f"Обозначения:\n" \
               f"🚒Рассылка/🕛Ожидание Название|Участники-Макс.|Мин. подписчиков\n\n" \
               f"Выберите нужную подборку ниже, а затем выберите канал для подачи заявки на участие." \

        if fleetList:
            totalPages, currentPage = math.ceil(count / LIMIT), math.ceil(OFFSET / LIMIT) + 1
            upPage, dowPage = OFFSET - LIMIT, OFFSET + LIMIT
            row,step = [],2
            for i in range(0, len(fleetList), step):
                batch = fleetList[i:i + step]
                for Cont in batch:
                    row.append(InlineKeyboardButton(f"{'🚒' if Cont[4] == 1 else '🕛'} {Cont[1]}|{Cont[11]}/{Cont[6]}|{Cont[8]/1000}K",callback_data=f"r/channel_fleet?fleet={Cont[0]}"))
                keyboard.append(row)
                row = []
            keyboard.append([InlineKeyboardButton(f"{'⬅️Назад' if upPage >= 0 else '-'}",callback_data=f"r/channel?page={upPage}" if upPage >= 0 else '-'),
                            InlineKeyboardButton(f"{currentPage}/{totalPages} стр.", callback_data="-"),
                            InlineKeyboardButton(f"️{'➡️Вперёд' if currentPage != totalPages else '-'}",callback_data=f"r/channel?page={dowPage}" if currentPage != totalPages else '-')])
        else:
            keyboard.append([InlineKeyboardButton(f"Пусто / подборки не найдены", callback_data="-")])
        keyboard.append([InlineKeyboardButton(f"Назад", callback_data="r/index")])
        await self.sendMsg(text=text,keyboard=keyboard)
    async def fleet_info(self,**kwargs):
        fleet_id = kwargs.get("fleet")[0]
        fleet=ChannelFleetList()
        fleetInfo,group_list= fleet.get_fleet_one(id=fleet_id),fleet.get_fleet_group_list(id=fleet_id)
        if fleetInfo:
            text = f"**Название подборки:** {fleetInfo[1]}\n" \
                      f"**Описание подборки:** {fleetInfo[2]}\n" \
                      f"**Участников (тек./макс.):** {fleetInfo[11]}/{fleetInfo[6]}\n" \
                      f"**Тип подборки:** Канал\n" \
                      f"**Мин. подписчиков:** {fleetInfo[8]}\n" \
                      f"**Мин. просмотров:** {fleetInfo[9]}\n\n" \
                      "**Список участников:**\n"
            if group_list:
                for index,group in enumerate(group_list):
                    text+=f"{index+1}.[{await truncate_string(group[3],20)}]({group[6]}) {round(group[5]/1000,1)}k\n"
            else:
                text+="Сейчас нет участников в подборке\n"
            keyboard=[]
            if fleetInfo[6]>fleetInfo[11]:
                text+="\n✅В подборке есть свободные места, можно подать заявку!"
                keyboard.append([InlineKeyboardButton(f"➕ Подать заявку",callback_data=f"r/channel_apply?fleet={fleetInfo[0]}&mi_me={fleetInfo[8]}")])
            else:
                text+="\n‼️Подборка заполнена, выберите другую!"
            # keyboard.append([InlineKeyboardButton(f"🚨 Пожаловаться", callback_data="r/channel_report")])
            keyboard.append([InlineKeyboardButton(f"Главная", callback_data="r/index"),InlineKeyboardButton(f"Назад", callback_data="r/channel")])
            await self.sendMsg(text=text,keyboard=keyboard)
    async def add_fleet(self,**kwargs):
        msg =await self.retChat()
        fleet,member= kwargs.get('fleet')[0],kwargs.get('mi_me')[0]
        user = self.data.get('user')
        if user:
            CF=ChannelFleetList(Msg=msg)
            my_group =await CF.get_user_group_list(id=user[0],member=member)
            if my_group:
                text = "**Выбор канала**\n\n" \
                       "Ниже отображаются только каналы, подходящие под требования\n\n" \
                       f"Требуется подписчиков: {round(int(member)/1000,1)}k\n" \
                       "Обозначения: 🟢Свободен 🟡На проверке 🟣В подборке 🔴Заблокирован\n" \
                       "Повторная заявка для канала, уже состоящего в подборке, автоматически снимет его с текущей\n" \
                       "Убедитесь, что вы добавили бота в канал и назначили его администратором\n\n" \
                       "👇Выберите канал для отправки заявки"
                keyboard = []
                for group in my_group:
                    ty_emoji= "🟢"
                    if group[10] == 1:
                        ty_emoji = "🟡"
                    elif group[10]==2:
                        ty_emoji= "🟣"
                    elif group[10]==10:
                        ty_emoji="🔴"
                    keyboard.append([InlineKeyboardButton(f"{ty_emoji} {group[3]}|{round(group[5]/1000,1)}k",callback_data=f"r/channel_submit?f={fleet}&g={group[0]}")])
                keyboard.append([InlineKeyboardButton("🏠 Главная", callback_data="r/index"),
                                 InlineKeyboardButton("↩️ Назад", callback_data=f"r/channel_fleet?fleet={fleet}")])
                await self.sendMsg(text=text,keyboard=keyboard)
            else:
                return await self.client.answer_callback_query(self.query.id, text="⚠️Не найдено каналов, соответствующих требованиям подборки. Выбирайте подборку по числу подписчиков",show_alert=True)
    async def submit_fleet(self,**kwargs):
        msg = await self.retChat()
        fleet = ChannelFleetList()
        fleet_id,group_id=kwargs.get('f')[0],kwargs.get('g')[0]
        fleetInfo, group = fleet.get_fleet_one(id=fleet_id),await fleet.get_user_group_one(id=group_id)
        if group:
            if group[10] in [0,1,2]:
                # print(group[1])
                isPrivi = await isPrivileges(chatId=group[1],typeG=group[4])
                if isPrivi == 1:
                    return await self.client.answer_callback_query(self.query.id, text="⚠️В этом чате/канале боту не выданы права, проверьте",show_alert=True)
                elif isPrivi == 2:
                    return await self.client.answer_callback_query(self.query.id, text="⛔Бот ещё не добавлен в эту группу или канал",show_alert=True)
                is_botList = await isBotBlacklist(Client=self.client,group=group[1])
                if len(is_botList)>0:
                    text = f"**⚠️ В вашем канале [{group[3]}]({group[6]}) обнаружены боты из чёрного списка**\n\n"
                    for is_bot in is_botList:
                        text += f"{is_bot[0]}-@`{is_bot[1]}` (копировать)\n"
                    text +="\nУдалите указанных ботов и отправьте заявку повторно"
                    keyboard = [[InlineKeyboardButton("❌ Удалить сообщение", callback_data=f"a/del_msg")]]
                    return await msg.reply_text(text=text,reply_markup=InlineKeyboardMarkup(keyboard))
                await self.client.answer_callback_query(self.query.id, text='🎯Заявка отправлена, ожидайте проверки администратором', show_alert=True)
                await fleet.put_group_one(id=group_id,fieet=fleet_id)
                await self.sendNotify(fleet=fleetInfo,group=group)
                await self.add_fleet(fleet=[fleetInfo[0]], mi_me=[fleetInfo[8]])
            elif group[10] ==10:
                await self.client.answer_callback_query(self.query.id, text='⚠️Заблокирован за многократные нарушения, обратитесь в поддержку',show_alert=True)
            else:
                await self.client.answer_callback_query(self.query.id, text='⚠️Не отправляйте заявку повторно, дождитесь проверки администратором',show_alert=True)
        else:
            await self.client.answer_callback_query(self.query.id,text="⛔Ошибка: информация о группе/канале не найдена",show_alert=True)
    async def sendNotify(self,**kwargs):
        fleet,group,user=kwargs["fleet"],kwargs["group"],self.data.get("user")
        text = "**🔆Получена новая заявка в подборку**\n" \
               f"**Название подборки:** {fleet[1]}\n" \
               f"**Тип подборки:** Канал\n" \
               f"**Описание подборки:** {fleet[2]}\n" \
               f"**Участников (тек./макс.):** {fleet[11]}/{fleet[6]}\n" \
               f"**Мин. подписчиков:** {fleet[8]}\n" \
               f"**Мин. просмотров:** {fleet[9]}\n\n" \
               f"**ID канала:** {group[1]}\n" \
               f"**Канал:** [{group[3]}]({group[6]})\n" \
               f"**Подписчиков:** {group[5]}\n" \
               f"**ID заявителя:** {user[1]}\n" \
               f"**Заявитель:** [{user[3]}](https://t.me/{user[2] or ''})\n" \
               "**Статус заявки:** 🔵 На проверке"
        keyboard = [[InlineKeyboardButton("🟢 Одобрить", callback_data=f"a/review_pass?group={group[0]}"),
                     InlineKeyboardButton("❌ Отклонить", callback_data=f"a/review_reject?group={group[0]}")],
                    [InlineKeyboardButton("🚫 Заблокировать", callback_data=f"a/review_ban?group={group[0]}")],
                    ]
        await CarData().post_notify_msg(group=group,label="На проверке")
        if int(bot_config["notifyType"])==0:
            await self.client.send_message(chat_id=bot_config['adminGroup'], text=text,
                                           reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)
        elif int(bot_config["notifyType"])==1:
            Channel = ChannelFleetList()
            adminList =await Channel.get_admini_list()
            for admin in adminList:
                try:
                    await self.client.send_message(chat_id=admin[1], text=text,
                                                   reply_markup=InlineKeyboardMarkup(keyboard),
                                                   disable_web_page_preview=True)
                except RPCError as e:
                    print(e)

