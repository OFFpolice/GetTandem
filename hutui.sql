-- SQLite schema and initial seed data for GetTandem

BEGIN TRANSACTION;

DROP TABLE IF EXISTS advertising;
CREATE TABLE advertising (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  titel TEXT DEFAULT NULL,
  url TEXT DEFAULT NULL,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO advertising (id, titel, url, creation_time) VALUES (6, 'Взаимопиар 2', 'https://t.me/+oYUJoUkMlfphN2M1', NULL);
INSERT INTO advertising (id, titel, url, creation_time) VALUES (7, 'Взаимопиар', 'https://t.me/+oYUJoUkMlfphN2M1', NULL);
INSERT INTO advertising (id, titel, url, creation_time) VALUES (9, 'Взаимопиар 3', 'https://t.me/+oYUJoUkMlfphN2M1', NULL);

DROP TABLE IF EXISTS bot_blacklist;
CREATE TABLE bot_blacklist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  bot_name TEXT DEFAULT NULL,
  state INTEGER DEFAULT 0,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO bot_blacklist (id, bot_name, state, creation_time) VALUES (3, '@hutui01bot', 0, '2023-10-31 15:37:15');
INSERT INTO bot_blacklist (id, bot_name, state, creation_time) VALUES (4, '@hutui1bot', 0, '2023-10-31 15:37:23');
INSERT INTO bot_blacklist (id, bot_name, state, creation_time) VALUES (5, '@TGMFHTbot', 0, '2023-10-31 15:37:29');
INSERT INTO bot_blacklist (id, bot_name, state, creation_time) VALUES (6, '@haloukt1_bot', 0, '2023-10-31 15:37:36');
INSERT INTO bot_blacklist (id, bot_name, state, creation_time) VALUES (7, '@hutuiZSbot', 0, '2023-10-31 15:37:48');
INSERT INTO bot_blacklist (id, bot_name, state, creation_time) VALUES (8, '@zyehtbot', 0, '2023-10-31 15:37:58');
INSERT INTO bot_blacklist (id, bot_name, state, creation_time) VALUES (9, '@tkhutuibot', 0, '2023-10-31 15:38:07');

DROP TABLE IF EXISTS chat_user;
CREATE TABLE chat_user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chat_id TEXT DEFAULT NULL,
  username TEXT DEFAULT NULL,
  full_name TEXT DEFAULT NULL,
  state INTEGER DEFAULT 0,
  admin INTEGER DEFAULT 0,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO chat_user (id, chat_id, username, full_name, state, admin, creation_time) VALUES (612, '5692641141', 'mao_zong', 'MaoZong', 0, 2, '2023-09-27 00:34:44');
INSERT INTO chat_user (id, chat_id, username, full_name, state, admin, creation_time) VALUES (616, '1471417837', 'lmmppll', '鬼怪', 0, 1, '2023-10-18 23:50:04');
INSERT INTO chat_user (id, chat_id, username, full_name, state, admin, creation_time) VALUES (617, '5966721929', 'Нет', 'B𝗼', 0, 1, '2023-10-21 22:41:36');
INSERT INTO chat_user (id, chat_id, username, full_name, state, admin, creation_time) VALUES (618, '6148737329', 'Нет', '🥹😆', 1, 0, '2023-10-22 03:27:43');
INSERT INTO chat_user (id, chat_id, username, full_name, state, admin, creation_time) VALUES (622, '936592623', 'Slee_mao', 'SleepyCat', 0, 2, '2023-10-22 10:05:57');
INSERT INTO chat_user (id, chat_id, username, full_name, state, admin, creation_time) VALUES (623, '1295', 'Нет', '@Huaren', 0, 0, '2023-10-22 17:17:03');
INSERT INTO chat_user (id, chat_id, username, full_name, state, admin, creation_time) VALUES (624, '6698677206', 'YWN888999', 'User', 0, 0, '2023-10-31 23:52:24');
INSERT INTO chat_user (id, chat_id, username, full_name, state, admin, creation_time) VALUES (625, '6042901473', 'agent47promo', 'Agent47', 0, 1, '2023-11-06 23:37:08');

DROP TABLE IF EXISTS config;
CREATE TABLE config (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT DEFAULT NULL,
  comm TEXT DEFAULT NULL
);

INSERT INTO config (id, name, comm) VALUES (1, 'botName', 'Бот взаимопиара 1');
INSERT INTO config (id, name, comm) VALUES (2, 'botUserName', '@FlashCloudBot');
INSERT INTO config (id, name, comm) VALUES (8, 'indexTxt', 'Добро пожаловать в бот взаимопиара');
INSERT INTO config (id, name, comm) VALUES (11, 'adminGroup', '-1001977340890');
INSERT INTO config (id, name, comm) VALUES (12, 'publicGroup', '@sepigzs');
INSERT INTO config (id, name, comm) VALUES (16, 'msgGroup', '-');
INSERT INTO config (id, name, comm) VALUES (17, 'video', '');
INSERT INTO config (id, name, comm) VALUES (19, 'restrict_limit', '30');
INSERT INTO config (id, name, comm) VALUES (20, 'notifyType', '0');
INSERT INTO config (id, name, comm) VALUES (22, 'rejectText', 'В этой подборке уже нет мест, выберите другую');
INSERT INTO config (id, name, comm) VALUES (23, 'rejectText', 'Не соответствует тематике');
INSERT INTO config (id, name, comm) VALUES (24, 'rejectText', 'Низкое качество контента');
INSERT INTO config (id, name, comm) VALUES (25, 'rejectText', 'Недостаточно просмотров');

DROP TABLE IF EXISTS fleet_list;
CREATE TABLE fleet_list (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT DEFAULT NULL,
  introduce TEXT DEFAULT NULL,
  fleet_type INTEGER DEFAULT 0,
  state INTEGER DEFAULT 0,
  sign TEXT DEFAULT NULL,
  total INTEGER DEFAULT 20,
  count INTEGER DEFAULT 1,
  mi_member INTEGER DEFAULT 1,
  mi_read INTEGER DEFAULT 1,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO fleet_list (id, title, introduce, fleet_type, state, sign, total, count, mi_member, mi_read, creation_time) VALUES (8, 'Группа A1', NULL, 0, 1, NULL, 20, 1, 1, 1, '2023-10-25 11:23:03');

DROP TABLE IF EXISTS group_list;
CREATE TABLE group_list (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  group_id TEXT DEFAULT NULL,
  username TEXT DEFAULT NULL,
  title TEXT DEFAULT NULL,
  type TEXT DEFAULT NULL,
  total_people INTEGER DEFAULT NULL,
  url TEXT DEFAULT NULL,
  msg_id INTEGER DEFAULT 0,
  out_fan INTEGER DEFAULT 0,
  input_fan INTEGER DEFAULT 0,
  state INTEGER DEFAULT 0,
  fleet_list INTEGER DEFAULT 0,
  chat_id INTEGER DEFAULT NULL,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  label TEXT DEFAULT NULL
);

INSERT INTO group_list (id, group_id, username, title, type, total_people, url, msg_id, out_fan, input_fan, state, fleet_list, chat_id, creation_time, label) VALUES (212, '-1001926767085', 'anniutes', 'Тестовый канал', 'CHANNEL', 85, 'https://t.me/+K4HlbH17FFhhOGNl', 0, 0, 0, 1, 8, 612, '2023-10-25 11:24:08', NULL);
INSERT INTO group_list (id, group_id, username, title, type, total_people, url, msg_id, out_fan, input_fan, state, fleet_list, chat_id, creation_time, label) VALUES (213, '-1001977340890', '', 'Тестовая группа', 'SUPERGROUP', 4, 'https://t.me/+zK1UylU7DvtlNDc1', 0, 0, 0, 0, 0, 612, '2023-10-25 11:24:44', NULL);
INSERT INTO group_list (id, group_id, username, title, type, total_people, url, msg_id, out_fan, input_fan, state, fleet_list, chat_id, creation_time, label) VALUES (214, '-1001909433562', '', 'Тестовый канал 2', 'CHANNEL', 20, 'https://t.me/+aYU-bOyGsDlmMGM1', 0, 0, 0, 0, 8, 612, '2023-10-28 17:53:45', NULL);

DROP TABLE IF EXISTS notify_msg;
CREATE TABLE notify_msg (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER DEFAULT NULL,
  group_id INTEGER DEFAULT NULL,
  msg TEXT DEFAULT NULL,
  creation_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

COMMIT;
