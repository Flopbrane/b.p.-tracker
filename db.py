from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from constants import (
    DB_COLUMNS,
    DB_PATH,
    DATA_DIR,
    EDITABLE_COLUMNS,
    EVENT_COLUMNS,
    EVENT_EDITABLE_COLUMNS,
    EXTRA_COLUMN_SQL_TYPES,
    RETURN_HOME_COLUMNS,
    RETURN_HOME_EDITABLE_COLUMNS,
)


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS bp_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT NOT NULL UNIQUE,

    wake_time TEXT,
    sleep_time TEXT,
    sleep_hours REAL,
    weight REAL,

    wpH INTEGER,
    wpL INTEGER,
    wp_hr INTEGER,

    spH INTEGER,
    spL INTEGER,
    sp_hr INTEGER,

    auH INTEGER,
    auL INTEGER,
    au_hr INTEGER,

    st1H INTEGER,
    st1L INTEGER,
    st1_hr INTEGER,

    st3H INTEGER,
    st3L INTEGER,
    st3_hr INTEGER,

    concerta_time TEXT,
    jardiance TEXT,
    metgluco_count INTEGER,

    dizziness TEXT,
    drinking_prev_night TEXT,
    water_amount TEXT,
    back_pain TEXT,
    ear_face_pain TEXT,

    meal_memo TEXT,
    salt_memo TEXT,
    caffeine TEXT,
    exercise_movement TEXT,
    outing TEXT,
    bathing TEXT,
    sleep_quality TEXT,
    stress_level TEXT,
    pc_work_hours REAL,
    neck_shoulder_jaw_tension TEXT,
    teeth_clenching TEXT,
    headache TEXT,
    back_pain_detail TEXT,
    dizziness_detail TEXT,

    memo TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


CREATE_EVENT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS bp_event_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_date TEXT NOT NULL,
    event_time TEXT,
    event_type TEXT,

    before_sys INTEGER,
    before_dia INTEGER,
    before_pulse INTEGER,

    after_sys INTEGER,
    after_dia INTEGER,
    after_pulse INTEGER,

    after_1min_sys INTEGER,
    after_1min_dia INTEGER,
    after_1min_pulse INTEGER,

    symptom TEXT,
    memo TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


CREATE_RETURN_HOME_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS bp_return_home_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT NOT NULL,
    weekday TEXT,
    activity TEXT,
    return_time TEXT,

    return_sys INTEGER,
    return_dia INTEGER,
    return_pulse INTEGER,

    squat_sys INTEGER,
    squat_dia INTEGER,
    squat_pulse INTEGER,

    stand_now_sys INTEGER,
    stand_now_dia INTEGER,
    stand_now_pulse INTEGER,

    stand_1min_sys INTEGER,
    stand_1min_dia INTEGER,
    stand_1min_pulse INTEGER,

    stand_3min_sys INTEGER,
    stand_3min_dia INTEGER,
    stand_3min_pulse INTEGER,

    bedtime_sys INTEGER,
    bedtime_dia INTEGER,
    bedtime_pulse INTEGER,

    arrival_time TEXT,
    before_lunch_sys INTEGER,
    before_lunch_dia INTEGER,
    before_lunch_pulse INTEGER,
    meal_content TEXT,
    after_lunch_sys INTEGER,
    after_lunch_dia INTEGER,
    after_lunch_pulse INTEGER,

    memo TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """SQLite に接続し、列名で値を取り出せるようにします。"""
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        connection.execute(CREATE_TABLE_SQL)
        connection.execute(CREATE_EVENT_TABLE_SQL)
        connection.execute(CREATE_RETURN_HOME_TABLE_SQL)
        _add_missing_columns(connection)
        connection.commit()


def _add_missing_columns(connection: sqlite3.Connection) -> None:
    """既存DBに、後から増えた任意入力列だけを安全に追加します。"""
    existing_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(bp_records)").fetchall()
    }
    for column_name, sql_type in EXTRA_COLUMN_SQL_TYPES.items():
        if column_name not in existing_columns:
            connection.execute(f"ALTER TABLE bp_records ADD COLUMN {column_name} {sql_type}")


def insert_record(record: dict[str, Any]) -> None:
    columns = EDITABLE_COLUMNS
    placeholders = ", ".join("?" for _ in columns)
    column_names = ", ".join(columns)
    values = [record.get(column) for column in columns]

    with get_connection() as connection:
        connection.execute(
            f"INSERT INTO bp_records ({column_names}) VALUES ({placeholders})",
            values,
        )
        connection.commit()


def update_record(record_id: int, record: dict[str, Any]) -> None:
    set_clause = ", ".join(f"{column} = ?" for column in EDITABLE_COLUMNS)
    values = [record.get(column) for column in EDITABLE_COLUMNS]
    values.append(record_id)

    with get_connection() as connection:
        connection.execute(
            f"""
            UPDATE bp_records
            SET {set_clause},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            values,
        )
        connection.commit()


def delete_record(record_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM bp_records WHERE id = ?", (record_id,))
        connection.commit()


def fetch_all_records() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM bp_records ORDER BY record_date DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_records_by_period(start_date: str, end_date: str) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM bp_records
            WHERE record_date BETWEEN ? AND ?
            ORDER BY record_date DESC
            """,
            (start_date, end_date),
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_record_by_id(record_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM bp_records WHERE id = ?",
            (record_id,),
        ).fetchone()
    if row is None:
        return None
    return dict(row)


def fetch_records_for_csv(
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    with get_connection() as connection:
        if start_date and end_date:
            rows = connection.execute(
                f"""
                SELECT {', '.join(DB_COLUMNS)}
                FROM bp_records
                WHERE record_date BETWEEN ? AND ?
                ORDER BY record_date
                """,
                (start_date, end_date),
            ).fetchall()
        else:
            rows = connection.execute(
                f"SELECT {', '.join(DB_COLUMNS)} FROM bp_records ORDER BY record_date"
            ).fetchall()
    return [dict(row) for row in rows]


def insert_event_record(record: dict[str, Any]) -> None:
    columns = EVENT_EDITABLE_COLUMNS
    placeholders = ", ".join("?" for _ in columns)
    column_names = ", ".join(columns)
    values = [record.get(column) for column in columns]

    with get_connection() as connection:
        connection.execute(
            f"INSERT INTO bp_event_records ({column_names}) VALUES ({placeholders})",
            values,
        )
        connection.commit()


def delete_event_record(record_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM bp_event_records WHERE id = ?", (record_id,))
        connection.commit()


def fetch_all_event_records() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM bp_event_records ORDER BY event_date DESC, event_time DESC, id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_event_records_by_period(start_date: str, end_date: str) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM bp_event_records
            WHERE event_date BETWEEN ? AND ?
            ORDER BY event_date DESC, event_time DESC, id DESC
            """,
            (start_date, end_date),
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_event_record_by_id(record_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            f"SELECT {', '.join(EVENT_COLUMNS)} FROM bp_event_records WHERE id = ?",
            (record_id,),
        ).fetchone()
    if row is None:
        return None
    return dict(row)


def insert_return_home_record(record: dict[str, Any]) -> None:
    columns = RETURN_HOME_EDITABLE_COLUMNS
    placeholders = ", ".join("?" for _ in columns)
    column_names = ", ".join(columns)
    values = [record.get(column) for column in columns]

    with get_connection() as connection:
        connection.execute(
            f"INSERT INTO bp_return_home_records ({column_names}) VALUES ({placeholders})",
            values,
        )
        connection.commit()


def delete_return_home_record(record_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM bp_return_home_records WHERE id = ?", (record_id,))
        connection.commit()


def fetch_all_return_home_records() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM bp_return_home_records
            ORDER BY record_date DESC, return_time DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_return_home_records_by_period(start_date: str, end_date: str) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM bp_return_home_records
            WHERE record_date BETWEEN ? AND ?
            ORDER BY record_date DESC, return_time DESC, id DESC
            """,
            (start_date, end_date),
        ).fetchall()
    return [dict(row) for row in rows]


def fetch_return_home_record_by_id(record_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            f"SELECT {', '.join(RETURN_HOME_COLUMNS)} FROM bp_return_home_records WHERE id = ?",
            (record_id,),
        ).fetchone()
    if row is None:
        return None
    return dict(row)
