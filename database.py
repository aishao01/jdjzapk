"""
database.py — SQLite 数据库层

两张表：
  - customers: 客户信息
  - records:   业务记录

使用说明：
  from database import get_db, init_db

  init_db()    # 建表（幂等）
  db = get_db()  # 获取连接（上下文管理器）
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Generator

from config import Database


# ──────────────────────────────────────────────
# Schema 定义（SQL 常量）
# ──────────────────────────────────────────────

CREATE_CUSTOMERS_TABLE = """
CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL DEFAULT '',
    phone       TEXT    NOT NULL DEFAULT '',
    address     TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);
"""

CREATE_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS records (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id         INTEGER NOT NULL DEFAULT 0,
    project_name        TEXT    NOT NULL DEFAULT '',
    date                TEXT    NOT NULL DEFAULT '',
    machine_type        TEXT    NOT NULL DEFAULT '',
    price               REAL    NOT NULL DEFAULT 0.0,
    unit                TEXT    NOT NULL DEFAULT '',
    am_start            TEXT    NOT NULL DEFAULT '',
    am_end              TEXT    NOT NULL DEFAULT '',
    pm_start            TEXT    NOT NULL DEFAULT '',
    pm_end              TEXT    NOT NULL DEFAULT '',
    ot_start            TEXT    NOT NULL DEFAULT '',
    ot_end              TEXT    NOT NULL DEFAULT '',
    total_hours         REAL    NOT NULL DEFAULT 0.0,
    total_amount        REAL    NOT NULL DEFAULT 0.0,
    date_range_start    TEXT    NOT NULL DEFAULT '',
    date_range_end      TEXT    NOT NULL DEFAULT '',
    construction_unit   TEXT    NOT NULL DEFAULT '',
    remarks             TEXT    NOT NULL DEFAULT '',
    issuer              TEXT    NOT NULL DEFAULT '',
    created_at          TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);
"""


# ──────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────

def ensure_db_dir() -> None:
    """确保数据库目录存在"""
    os.makedirs(Database.DB_DIR, exist_ok=True)


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    获取数据库连接的上下文管理器。

    用法:
        with get_db() as db:
            db.execute(...)
            db.commit()

    自动开启 foreign_keys，提交/回滚异常，关闭连接。
    """
    ensure_db_dir()
    conn = sqlite3.connect(Database.DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """初始化数据库，创建 customers 和 records 表（幂等）。"""
    with get_db() as db:
        db.execute(CREATE_CUSTOMERS_TABLE)
        db.execute(CREATE_RECORDS_TABLE)


def get_connection() -> sqlite3.Connection:
    """
    （备选）直接获取一个原始连接，不自动提交/回滚。
    使用后需手动 close()。
    """
    ensure_db_dir()
    conn = sqlite3.connect(Database.DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


# ──────────────────────────────────────────────
# 快速测试（python database.py 直接运行）
# ──────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print(f"[OK] Database initialized: {Database.DB_PATH}")
    with get_db() as db:
        tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        print(f"[TABLES] {[r['name'] for r in tables]}")
