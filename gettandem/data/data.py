from config import *
import aiosqlite
try:
    import asyncpg
except ImportError:
    asyncpg = None


_CORE_CONFIG_DEFAULTS = (
    ('adminGroup', '1'),
    ('msgGroup', '-'),
    ('restrict_limit', '30'),
    ('notifyType', '1'),
)

_DEFAULT_REJECT_TEXTS = (
    'В этой подборке уже нет мест, выберите другую',
    'Не соответствует тематике',
    'Низкое качество контента',
    'Недостаточно просмотров',
)


def _to_pg_query(query: str) -> str:
    out = []
    in_single = False
    param_idx = 1
    i = 0
    n = len(query)
    while i < n:
        ch = query[i]
        if ch == "'":
            out.append(ch)
            if in_single and i + 1 < n and query[i + 1] == "'":
                out.append("'")
                i += 2
                continue
            in_single = not in_single
            i += 1
            continue
        if not in_single and ch == '?':
            out.append(f"${param_idx}")
            param_idx += 1
            i += 1
            continue
        if not in_single and query[i:i + 6].upper() == ' LIKE ':
            out.append(' ILIKE ')
            i += 6
            continue
        out.append(ch)
        i += 1
    return ''.join(out)


class Card:
    def __init__(self, db_path=None, database_url=None):
        default_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'hutui.db')
        self.db_path = db_path or default_path
        if db_path is not None and database_url is None:
            self.database_url = ""
        else:
            self.database_url = (database_url if database_url is not None else DATABASE_URL).strip()
        self.use_postgres = bool(
            asyncpg is not None and self.database_url.startswith(('postgres://', 'postgresql://'))
        )
        self._write_lock = asyncio.Lock()
        self._pg_pool = None
        self._pg_pool_lock = asyncio.Lock()

    def _pg_dsn(self) -> str:
        if self.database_url.startswith('postgres://'):
            return 'postgresql://' + self.database_url[len('postgres://'):]
        return self.database_url

    async def _get_pg_pool(self):
        if self._pg_pool is not None:
            return self._pg_pool
        async with self._pg_pool_lock:
            if self._pg_pool is None:
                self._pg_pool = await asyncpg.create_pool(
                    dsn=self._pg_dsn(),
                    min_size=1,
                    max_size=10,
                )
        return self._pg_pool

    async def close(self):
        if self._pg_pool is not None:
            await self._pg_pool.close()
            self._pg_pool = None

    async def _connect_sqlite(self):
        conn = await aiosqlite.connect(self.db_path, timeout=30.0)
        await conn.execute("PRAGMA journal_mode=DELETE;")
        await conn.execute("PRAGMA synchronous=FULL;")
        await conn.execute("PRAGMA busy_timeout=10000;")
        return conn

    def _coerce_pg_params(self, stmt, data):
        args = list(data or ())
        params = stmt.get_parameters()
        coerced = []
        for idx, val in enumerate(args):
            if idx < len(params) and val is not None:
                ptype = params[idx].name
                if ptype in ('int2', 'int4', 'int8') and isinstance(val, str):
                    s = val.strip()
                    if s.lstrip('-').isdigit():
                        val = int(s)
                elif ptype in ('text', 'varchar', 'bpchar') and not isinstance(val, str):
                    val = str(val)
            coerced.append(val)
        return coerced

    async def _migrate_sqlite_to_pg(self, pg_conn):
        if not os.path.exists(self.db_path):
            return
        tables = (
            'advertising',
            'bot_blacklist',
            'chat_user',
            'config',
            'fleet_list',
            'group_list',
            'notify_msg',
        )
        total_pg = 0
        for tbl in tables:
            total_pg += await pg_conn.fetchval(f"SELECT COUNT(*) FROM {tbl}")
        if total_pg > 0:
            return
        try:
            async with aiosqlite.connect(self.db_path, timeout=10.0) as sq_conn:
                for tbl in tables:
                    async with sq_conn.execute(f"SELECT * FROM {tbl}") as cur:
                        rows = await cur.fetchall()
                        if not rows:
                            continue
                        cols = [d[0] for d in cur.description]
                    placeholders = ', '.join(f"${i}" for i in range(1, len(cols) + 1))
                    col_list = ', '.join(cols)
                    insert_sql = f"INSERT INTO {tbl} ({col_list}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                    for r in rows:
                        vals = []
                        for col_name, v in zip(cols, r):
                            if col_name == 'creation_time' and isinstance(v, str):
                                try:
                                    vals.append(datetime.datetime.fromisoformat(v))
                                except ValueError:
                                    vals.append(None)
                            else:
                                vals.append(v)
                        await pg_conn.execute(insert_sql, *vals)
                    await pg_conn.execute(
                        f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), COALESCE((SELECT MAX(id) FROM {tbl}), 1), (SELECT MAX(id) FROM {tbl}) IS NOT NULL)"
                    )
        except Exception as err:
            logging.warning(f"Миграция из SQLite в PostgreSQL пропущена: {err}")

    async def init_db(self):
        if self.use_postgres:
            await self._init_postgres()
        else:
            await self._init_sqlite()

    async def _init_postgres(self):
        try:
            pool = await self._get_pg_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS advertising (
                        id SERIAL PRIMARY KEY,
                        titel TEXT DEFAULT NULL,
                        url TEXT DEFAULT NULL,
                        creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS bot_blacklist (
                        id SERIAL PRIMARY KEY,
                        bot_name TEXT DEFAULT NULL,
                        state INTEGER DEFAULT 0,
                        creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS chat_user (
                        id SERIAL PRIMARY KEY,
                        chat_id TEXT DEFAULT NULL,
                        username TEXT DEFAULT NULL,
                        full_name TEXT DEFAULT NULL,
                        state INTEGER DEFAULT 0,
                        admin INTEGER DEFAULT 0,
                        creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS config (
                        id SERIAL PRIMARY KEY,
                        name TEXT DEFAULT NULL,
                        comm TEXT DEFAULT NULL
                    );

                    CREATE TABLE IF NOT EXISTS fleet_list (
                        id SERIAL PRIMARY KEY,
                        title TEXT DEFAULT NULL,
                        introduce TEXT DEFAULT NULL,
                        fleet_type INTEGER DEFAULT 0,
                        state INTEGER DEFAULT 0,
                        sign TEXT DEFAULT NULL,
                        total INTEGER DEFAULT 20,
                        count INTEGER DEFAULT 1,
                        mi_member INTEGER DEFAULT 1,
                        mi_read INTEGER DEFAULT 1,
                        creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS group_list (
                        id SERIAL PRIMARY KEY,
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
                        creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        label TEXT DEFAULT NULL
                    );

                    CREATE TABLE IF NOT EXISTS notify_msg (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER DEFAULT NULL,
                        group_id INTEGER DEFAULT NULL,
                        msg TEXT DEFAULT NULL,
                        creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
                await self._migrate_sqlite_to_pg(conn)
                await conn.execute(
                    "DELETE FROM config WHERE name IN ('botName', 'botUserName', 'indexTxt', 'publicGroup', 'video')"
                )
                total_cfg = await conn.fetchval("SELECT COUNT(*) FROM config")
                for key, default_val in _CORE_CONFIG_DEFAULTS:
                    exists = await conn.fetchval("SELECT COUNT(*) FROM config WHERE name=$1", key)
                    if not exists:
                        await conn.execute(
                            "INSERT INTO config (name, comm) VALUES ($1, $2)",
                            key,
                            default_val,
                        )
                if total_cfg == 0:
                    for txt in _DEFAULT_REJECT_TEXTS:
                        await conn.execute(
                            "INSERT INTO config (name, comm) VALUES ($1, $2)",
                            'rejectText',
                            txt,
                        )
                if ADMIN_ID:
                    u_cnt = await conn.fetchval(
                        "SELECT COUNT(*) FROM chat_user WHERE chat_id=$1",
                        str(ADMIN_ID),
                    )
                    if not u_cnt:
                        await conn.execute(
                            "INSERT INTO chat_user (chat_id, username, full_name, state, admin) VALUES ($1, $2, $3, $4, $5)",
                            str(ADMIN_ID), "OFFpolice", "OFFpolice", 0, 2,
                        )
        except Exception as err:
            logging.error(f"init_db(pg)-Ошибка инициализации базы данных: {err}")

    async def _init_sqlite(self):
        try:
            async with self._write_lock:
                db_dir = os.path.dirname(os.path.abspath(self.db_path))
                if db_dir:
                    os.makedirs(db_dir, exist_ok=True)
                conn = await self._connect_sqlite()
                try:
                    await conn.executescript(
                        """
                        CREATE TABLE IF NOT EXISTS advertising (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            titel TEXT DEFAULT NULL,
                            url TEXT DEFAULT NULL,
                            creation_time DATETIME DEFAULT CURRENT_TIMESTAMP
                        );

                        CREATE TABLE IF NOT EXISTS bot_blacklist (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            bot_name TEXT DEFAULT NULL,
                            state INTEGER DEFAULT 0,
                            creation_time DATETIME DEFAULT CURRENT_TIMESTAMP
                        );

                        CREATE TABLE IF NOT EXISTS chat_user (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            chat_id TEXT DEFAULT NULL,
                            username TEXT DEFAULT NULL,
                            full_name TEXT DEFAULT NULL,
                            state INTEGER DEFAULT 0,
                            admin INTEGER DEFAULT 0,
                            creation_time DATETIME DEFAULT CURRENT_TIMESTAMP
                        );

                        CREATE TABLE IF NOT EXISTS config (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT DEFAULT NULL,
                            comm TEXT DEFAULT NULL
                        );

                        CREATE TABLE IF NOT EXISTS fleet_list (
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

                        CREATE TABLE IF NOT EXISTS group_list (
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

                        CREATE TABLE IF NOT EXISTS notify_msg (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER DEFAULT NULL,
                            group_id INTEGER DEFAULT NULL,
                            msg TEXT DEFAULT NULL,
                            creation_time DATETIME DEFAULT CURRENT_TIMESTAMP
                        );
                        """
                    )
                    await conn.execute(
                        "DELETE FROM config WHERE name IN ('botName', 'botUserName', 'indexTxt', 'publicGroup', 'video')"
                    )
                    async with conn.execute("SELECT COUNT(*) FROM config") as cursor:
                        row = await cursor.fetchone()
                        total_cfg = row[0] if row else 0
                    for key, default_val in _CORE_CONFIG_DEFAULTS:
                        async with conn.execute("SELECT COUNT(*) FROM config WHERE name=?", (key,)) as cursor:
                            k_row = await cursor.fetchone()
                            if not k_row or k_row[0] == 0:
                                await conn.execute(
                                    "INSERT INTO config (name, comm) VALUES (?, ?)",
                                    (key, default_val),
                                )
                    if total_cfg == 0:
                        await conn.executemany(
                            "INSERT INTO config (name, comm) VALUES (?, ?)",
                            [('rejectText', txt) for txt in _DEFAULT_REJECT_TEXTS],
                        )
                    if ADMIN_ID:
                        async with conn.execute("SELECT COUNT(*) FROM chat_user WHERE chat_id=?", (str(ADMIN_ID),)) as cursor:
                            u_row = await cursor.fetchone()
                            if not u_row or u_row[0] == 0:
                                await conn.execute(
                                    "INSERT INTO chat_user (chat_id, username, full_name, state, admin) VALUES (?, ?, ?, ?, ?)",
                                    (str(ADMIN_ID), "OFFpolice", "OFFpolice", 0, 2),
                                )
                    await conn.commit()
                finally:
                    await conn.close()
        except Exception as err:
            logging.error(f"init_db-Ошибка инициализации базы данных: {err}")

    async def execute_query(self, query, data=None):
        if self.use_postgres:
            try:
                pool = await self._get_pg_pool()
                pg_query = _to_pg_query(query)
                async with pool.acquire() as conn:
                    stmt = await conn.prepare(pg_query)
                    args = self._coerce_pg_params(stmt, data)
                    rows = await stmt.fetch(*args)
                    return [tuple(r.values()) for r in rows]
            except Exception as err:
                logging.error(f"execute_query(pg)-Ошибка выполнения запроса: {err}")
                return []
        try:
            conn = await self._connect_sqlite()
            try:
                async with conn.execute(query, data or ()) as cursor:
                    return await cursor.fetchall()
            finally:
                await conn.close()
        except Exception as err:
            logging.error(f"execute_query-Ошибка выполнения запроса: {err}")
            return []

    async def execute_update(self, query, data=None):
        if self.use_postgres:
            try:
                pool = await self._get_pg_pool()
                pg_query = _to_pg_query(query)
                async with self._write_lock:
                    async with pool.acquire() as conn:
                        stmt = await conn.prepare(pg_query)
                        args = self._coerce_pg_params(stmt, data)
                        await stmt.fetch(*args)
                        return True
            except Exception as err:
                logging.error(f"execute_update(pg)-Ошибка выполнения обновления: {err}")
                return False
        try:
            async with self._write_lock:
                conn = await self._connect_sqlite()
                try:
                    await conn.execute(query, data or ())
                    await conn.commit()
                    return True
                finally:
                    await conn.close()
        except Exception as err:
            logging.error(f"execute_update-Ошибка выполнения обновления: {err}")
            return False

    async def select(self, query, data=None):
        return await self.execute_query(query, data)

    async def update(self, query, data=None):
        return await self.execute_update(query, data)

    async def insert(self, query, data=None):
        return await self.execute_update(query, data)

    async def delete(self, query, data=None):
        return await self.execute_update(query, data)


db = Card()


class ChatUser:
    '''Класс для работы с таблицей пользователей'''

    def __init__(self, Msg: Message = None):
        self.msg = Msg

    async def get(self, from_user):
        '''Поиск пользователя'''
        user = await db.select("SELECT * FROM chat_user WHERE chat_id=?", (str(from_user.id),))
        if user:
            return user[0]
        return []

    async def post(self, from_user):
        full_name = f"{from_user.first_name or ''}{(' ' + from_user.last_name) if from_user.last_name else ''}".strip() or 'Пользователь'
        is_super = 2 if ADMIN_ID and int(from_user.id) == ADMIN_ID else 0
        aad = "INSERT INTO chat_user (chat_id,username,full_name,admin) VALUES(?,?,?,?)"
        data = (str(from_user.id), from_user.username or 'Нет', full_name, is_super)
        if await db.insert(aad, data):
            return await self.get(from_user=from_user)
        return []

    async def get_or_create(self, from_user):
        user = await self.get(from_user=from_user)
        if user:
            updates = []
            params = []
            uname = from_user.username or 'Нет'
            full_name = f"{from_user.first_name or ''}{(' ' + from_user.last_name) if from_user.last_name else ''}".strip() or user[3] or 'Пользователь'
            if user[2] != uname:
                updates.append("username=?")
                params.append(uname)
            if user[3] != full_name:
                updates.append("full_name=?")
                params.append(full_name)
            if ADMIN_ID and int(from_user.id) == ADMIN_ID and user[5] != 2:
                updates.append("admin=2")
            if updates:
                params.append(str(from_user.id))
                await db.update(f"UPDATE chat_user SET {', '.join(updates)} WHERE chat_id=?", tuple(params))
                user = await self.get(from_user=from_user)
            return user
        else:
            return await self.post(from_user=from_user)


class ConfigData:
    async def get_config_list(self):
        data = await db.select("SELECT * FROM config")
        if data:
            return data
        return []

    async def put_config(self, comm, name):
        existing = await db.select("SELECT id FROM config WHERE name=?", (name,))
        if existing:
            return await db.update("UPDATE config SET comm=? WHERE name=?", (comm, name))
        return await db.insert("INSERT INTO config (name, comm) VALUES (?, ?)", (name, comm))

    async def get_rejectText_list(self):
        data = await db.select("SELECT * FROM config WHERE name='rejectText'")
        if data:
            return data
        return []

    async def del_rejectText(self, id):
        data = await db.delete("DELETE FROM config WHERE id=?", (id,))
        return data

    async def post_rejectText(self, text):
        data = await db.insert("INSERT INTO config (name,comm) VALUES(?,?)", ('rejectText', text))
        return data

    async def put_rejectText(self, id, text):
        data = await db.update("UPDATE config SET comm=? WHERE id=? AND name='rejectText'", (text, id))
        return data


class AdvertisingData:
    def __init__(self, Msg: Message = None):
        self.msg = Msg

    async def get_advertising_list(self):
        data = await db.select("SELECT * FROM advertising")
        if data:
            return data
        return []

    async def del_advertising(self, id):
        data = await db.delete("DELETE FROM advertising WHERE id=?", (id,))
        return data

    async def post_advertising(self, titel, url):
        data = await db.insert("INSERT INTO advertising (titel,url) VALUES(?,?)", (titel, url))
        return data

    async def put_advertising(self, id, titel, url):
        data = await db.update("UPDATE advertising SET titel=?,url=? WHERE id=?", (titel, url, id))
        return data


class CarData:
    # Данные подборок (Car) для панели администратора
    def __init__(self, Msg: Message = None):
        self.msg = Msg

    async def get_fleet(self, **kwargs):
        LIMIT, OFFSET = kwargs.get('LIMIT'), kwargs.get('OFFSET')
        count = await db.select("SELECT COUNT(*) FROM fleet_list WHERE fleet_type = 0")
        data = await db.select(
            "SELECT fleet_list.*, COUNT(group_list.id) AS group_count FROM fleet_list "
            "LEFT JOIN group_list ON fleet_list.id = group_list.fleet_list AND group_list.state=2 "
            "WHERE fleet_type = 0 GROUP BY fleet_list.id ORDER BY title LIMIT ? OFFSET ?",
            (LIMIT, OFFSET),
        )
        if data:
            return data, count[0][0]
        return [], 0

    async def get_fleet_group_list(self, id):
        group = await db.select("SELECT * FROM group_list WHERE fleet_list=? AND state=2", (id,))
        if group:
            return group
        return []

    async def get_fleet_one(self, id):
        fleet = await db.select(
            "SELECT fleet_list.*, COUNT(group_list.id) AS group_count "
            "FROM fleet_list "
            "LEFT JOIN group_list ON fleet_list.id = group_list.fleet_list AND group_list.state = 2 "
            "WHERE fleet_list.id = ? GROUP BY fleet_list.id",
            (id,),
        )
        if fleet:
            return fleet[0]
        return []

    async def get_user_group_one(self, id):
        my_group = await db.select("SELECT * FROM group_list WHERE id=?", (id,))
        if my_group:
            return my_group[0]
        return []

    async def post_car(self, car_title, car_type):
        data = await db.insert("INSERT INTO fleet_list (title,fleet_type) VALUES(?,?)", (car_title, car_type))
        return data

    async def put_car_titel(self, id, text):
        data = await db.update("UPDATE fleet_list SET title=? WHERE id=?", (text, id))
        return data

    async def put_car_introduce(self, id, text):
        data = await db.update("UPDATE fleet_list SET introduce=? WHERE id=?", (text, id))
        return data

    async def put_car_total(self, id, text):
        data = await db.update("UPDATE fleet_list SET total=? WHERE id=?", (text, id))
        return data

    async def put_car_mi_memberl(self, id, text):
        data = await db.update("UPDATE fleet_list SET mi_member=? WHERE id=?", (text, id))
        return data

    async def put_car_mi_mi_read(self, id, text):
        data = await db.update("UPDATE fleet_list SET mi_read=? WHERE id=?", (text, id))
        return data

    async def put_car_state(self, id, text):
        data = await db.update("UPDATE fleet_list SET state=? WHERE id=?", (text, id))
        return data

    async def put_car_pass_review(self, group, state, label, url=None, fleet_id=None):
        sets = ["state=?", "msg_id=0"]
        params = [state]
        if url is not None:
            sets.append("url=?")
            params.append(url)
        if fleet_id is not None:
            sets.append("fleet_list=?")
            params.append(fleet_id)
        params.append(group[0])
        group_d = await db.update(f"UPDATE group_list SET {', '.join(sets)} WHERE id=?", tuple(params))
        if group_d:
            await self.post_notify_msg(group=group, label=label)
            return True
        return False

    async def post_notify_msg(self, group, label):
        notify = await db.insert(
            "INSERT INTO notify_msg (user_id,group_id,msg) VALUES(?,?,?)",
            (group[12], group[0], label),
        )
        if notify:
            return True
        return False

    async def get_notify_msg(self, user=None, group=None):
        data = await db.select(
            "SELECT * FROM notify_msg WHERE group_id = ? AND user_id = ? ORDER BY id DESC LIMIT 1",
            (group, user),
        )
        if data:
            return data[0]
        return []

    async def get_user(self, id):
        user = await db.select("SELECT * FROM chat_user WHERE id=?", (id,))
        if user:
            return user[0]
        return []

    async def get_rejectText(self, id):
        data = await db.select("SELECT * FROM config WHERE name='rejectText' AND id=?", (id,))
        if data:
            return data[0]
        return []


class GroupData:
    # Данные каналов (Group) для панели администратора
    async def get_group_list(self, **kwargs):
        LIMIT, OFFSET = kwargs.get('LIMIT'), kwargs.get('OFFSET')
        search = kwargs.get('search')
        if search:
            search_val = search[0] if isinstance(search, list) else search
            data = await db.select(
                "SELECT * FROM group_list WHERE type='CHANNEL' AND title LIKE ? ORDER BY id LIMIT ? OFFSET ?",
                (f"%{search_val}%", LIMIT, OFFSET),
            )
        else:
            data = await db.select("SELECT * FROM group_list WHERE type='CHANNEL' ORDER BY id LIMIT ? OFFSET ?", (LIMIT, OFFSET))
        if data:
            return data
        return []

    async def get_group_index_count(self, **kwargs):
        count = await db.select(
            "SELECT (SELECT COUNT(*) FROM group_list) AS total_count,"
            "(SELECT COUNT(*) FROM group_list WHERE type='CHANNEL') AS CHANNEL_count,"
            "(SELECT COUNT(*) FROM group_list WHERE type='CHANNEL' AND state=2) AS CHANNEL_state_count,"
            "(SELECT COUNT(*) FROM group_list WHERE type='SUPERGROUP') AS SUPERGROUP_count,"
            "(SELECT COUNT(*) FROM group_list WHERE type='SUPERGROUP' AND state=2) AS SUPERGROUP_state_count"
        )
        if count:
            return count[0]
        return (0, 0, 0, 0, 0)

    async def get_group_info(self, id):
        data = await db.select("SELECT * FROM group_list WHERE id=?", (id,))
        if data:
            return data[0]
        return []

    async def get_fleet_one(self, id):
        fleet = await db.select("SELECT * FROM fleet_list WHERE id=?", (id,))
        if fleet:
            return fleet[0]
        return []

    async def get_user(self, id):
        user = await db.select("SELECT * FROM chat_user WHERE id=?", (id,))
        if user:
            return user[0]
        return []


class ChannelFleetList:
    def __init__(self, Msg: Message = None):
        self.msg = Msg

    async def get(self, **kwargs):
        data = await db.select("SELECT * FROM fleet_list ORDER BY sign")
        if data:
            return data
        return []

    async def get_fleet(self, **kwargs):
        LIMIT, OFFSET = kwargs.get('LIMIT'), kwargs.get('OFFSET')
        count = await db.select("SELECT COUNT(*) FROM fleet_list WHERE fleet_type = 0 AND state=1")
        data = await db.select(
            "SELECT fleet_list.*, COUNT(group_list.id) AS group_count FROM fleet_list "
            "LEFT JOIN group_list ON fleet_list.id = group_list.fleet_list AND group_list.state=2 "
            "WHERE fleet_type = 0 AND fleet_list.state=1 GROUP BY fleet_list.id ORDER BY title LIMIT ? OFFSET ?",
            (LIMIT, OFFSET),
        )
        if data:
            return data, count[0][0]
        return [], 0

    async def get_group_count(self, **kwargs):
        count = await db.select("SELECT COUNT(*) FROM group_list WHERE type='CHANNEL' AND state=2")
        if count:
            return count[0][0]
        return 0

    async def get_fleet_one(self, id):
        fleet = await db.select(
            "SELECT fleet_list.*, COUNT(group_list.id) AS group_count "
            "FROM fleet_list "
            "LEFT JOIN group_list ON fleet_list.id = group_list.fleet_list AND group_list.state = 2 "
            "WHERE fleet_list.id = ? GROUP BY fleet_list.id",
            (id,),
        )
        if fleet:
            return fleet[0]
        return []

    async def get_fleet_group_list(self, id):
        group = await db.select("SELECT * FROM group_list WHERE fleet_list=? AND state=2", (id,))
        if group:
            return group
        return []

    async def get_user_group_list(self, id, member):
        try:
            min_member = int(member)
        except (TypeError, ValueError):
            min_member = 0
        my_group = await db.select(
            "SELECT * FROM group_list WHERE chat_id=? AND type=? AND total_people>=?",
            (id, "CHANNEL", min_member),
        )
        if my_group:
            return my_group
        return []

    async def get_user_group_one(self, id):
        my_group = await db.select("SELECT * FROM group_list WHERE id=?", (id,))
        if my_group:
            return my_group[0]
        return []

    async def put_group_one(self, id, fieet):
        upData = await db.update("UPDATE group_list SET state=1,fleet_list=?,msg_id=0 WHERE id=?", (fieet, id))
        if upData:
            return True
        return False

    async def get_admini_list(self):
        admin = await db.select("SELECT * FROM chat_user WHERE admin IN (1,2)")
        if admin:
            return admin
        return []


class BotBlacklistDate:
    async def get_bot_blacklist_list(self):
        data = await db.select("SELECT * FROM bot_blacklist")
        if data:
            return data
        return []

    async def del_bot_blacklist(self, id):
        data = await db.delete("DELETE FROM bot_blacklist WHERE id=?", (id,))
        return data

    async def post_bot_blacklist(self, titel):
        data = await db.insert("INSERT INTO bot_blacklist (bot_name) VALUES(?)", (titel,))
        return data

    async def put_bot_blacklist(self, id, titel):
        data = await db.update("UPDATE bot_blacklist SET bot_name=? WHERE id=?", (titel, id))
        return data