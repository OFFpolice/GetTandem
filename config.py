# Библиотека и конфигурация бота (aiogram 3)
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType, ChatMemberStatus
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.filters import Command, or_f
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ForceReply,
    ReplyKeyboardMarkup,
    Message,
    ChatMemberUpdated,
    BotCommand,
    LinkPreviewOptions,
    ChatMemberAdministrator,
    ChatMemberOwner,
)
from urllib.parse import urlparse, parse_qs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import html
import os
import re
import json
import uvloop
import redis
import socket
import math
import datetime
import logging

uvloop.install()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a',
    filename='run.log'
)

redis_client = redis.Redis(host='127.0.0.1', port=6379, db=2)

bot_config = {
    "botName": "Бот не настроен",
    "indexTxt": "Приветственный текст не настроен",
    "botUserName": "Бот не настроен",
    "publicGroup": "Не настроено",
    "adminGroup": 1,
    "msgGroup": 1,
    "notifyType": 1,
    "rejectText": [],
    "restrict_limit": 60,
    "video": ''
}

scheduler = AsyncIOScheduler(
    timezone='Asia/Shanghai',
    job_defaults={'max_instances': 1, 'coalesce': False}
)

cli_obj = {
    "name": "HuTuiBot",
    "bot_token": "9228971316:AAF0_3xXw5tfe510TAAPC4IqYZk2vXKLI4E",
}

bot = Bot(
    token=cli_obj["bot_token"],
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
app = bot