# Библиотека и конфигурация бота (aiogram 3)
import os
from os.path import join, dirname
from dotenv import load_dotenv

BASE_DIR = dirname(os.path.abspath(__file__))
dotenv_path = join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

BOT_TOKEN = str(os.getenv("BOT_TOKEN") or "").strip()
_admin_id_raw = str(os.getenv("ADMIN_ID") or "").strip()
ADMIN_ID = int(_admin_id_raw) if _admin_id_raw.lstrip("-").isdigit() else 0
DATABASE_URL = str(os.getenv("DATABASE_URL") or "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в .env")

import pydantic
if hasattr(pydantic, "FailFast") and getattr(pydantic.FailFast, "__hash__", None) is None:
    pydantic.FailFast.__hash__ = lambda self: hash((type(self), getattr(self, "fail_fast", True)))

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
    BotCommandScopeDefault,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
    LinkPreviewOptions,
    ChatMemberAdministrator,
    ChatMemberOwner,
)
from urllib.parse import urlparse, parse_qs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import html
import re
import json
import time
import threading
try:
    import uvloop
    uvloop.install()
except Exception:
    pass

try:
    import redis
except ImportError:
    redis = None

import socket
import math
import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a',
    filename=join(BASE_DIR, 'run.log'),
    encoding='utf-8',
)


class _MemoryRedisFallback:
    """In-memory TTL store used automatically if Redis server is unavailable."""

    def __init__(self):
        self._data = {}
        self._exp = {}
        self._lock = threading.Lock()

    def _prune(self, key):
        exp = self._exp.get(key)
        if exp is not None and time.monotonic() >= exp:
            self._data.pop(key, None)
            self._exp.pop(key, None)

    def get(self, key):
        with self._lock:
            self._prune(key)
            return self._data.get(key)

    def set(self, key, value, ex=None):
        with self._lock:
            self._data[key] = value
            if ex is not None:
                self._exp[key] = time.monotonic() + float(ex)
            else:
                self._exp.pop(key, None)
            return True

    def incr(self, key, amount=1):
        with self._lock:
            self._prune(key)
            val = int(self._data.get(key) or 0) + amount
            self._data[key] = str(val)
            return val

    def expire(self, key, seconds):
        with self._lock:
            self._prune(key)
            if key in self._data:
                self._exp[key] = time.monotonic() + float(seconds)
                return True
            return False

    def delete(self, *keys):
        with self._lock:
            removed = 0
            for k in keys:
                if k in self._data:
                    removed += 1
                self._data.pop(k, None)
                self._exp.pop(k, None)
            return removed


class _SafeRedisClient:
    def __init__(self, host='127.0.0.1', port=6379, db=2):
        self._fallback = _MemoryRedisFallback()
        self._client = None
        self._use_fallback = redis is None
        if not self._use_fallback:
            self._client = redis.Redis(host=host, port=port, db=db, socket_connect_timeout=1)
            try:
                self._client.ping()
            except Exception:
                self._use_fallback = True
                logging.warning("Redis недоступен, используется встроенный in-memory кеш")

    def _call(self, method, *args, **kwargs):
        if not self._use_fallback:
            try:
                return getattr(self._client, method)(*args, **kwargs)
            except Exception:
                self._use_fallback = True
                logging.warning("Потеряно соединение с Redis, переключение на in-memory кеш")
        return getattr(self._fallback, method)(*args, **kwargs)

    def get(self, key):
        return self._call("get", key)

    def set(self, key, value, ex=None):
        return self._call("set", key, value, ex=ex)

    def incr(self, key, amount=1):
        return self._call("incr", key, amount=amount)

    def expire(self, key, seconds):
        return self._call("expire", key, seconds)

    def delete(self, *keys):
        return self._call("delete", *keys)


redis_client = _SafeRedisClient(host='127.0.0.1', port=6379, db=2)

bot_config = {
    "adminGroup": 1,
    "msgGroup": 1,
    "notifyType": 1,
    "rejectText": [],
    "restrict_limit": 60
}

try:
    scheduler = AsyncIOScheduler(
        timezone='Asia/Shanghai',
        job_defaults={'max_instances': 1, 'coalesce': False}
    )
except Exception:
    scheduler = AsyncIOScheduler(
        timezone=datetime.timezone.utc,
        job_defaults={'max_instances': 1, 'coalesce': False}
    )

cli_obj = {
    "name": "HuTuiBot",
    "bot_token": BOT_TOKEN,
}

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
app = bot