from __future__ import annotations

import sqlite3
from typing import Any

import db
from constants import DB_COLUMNS


BP_RANGES = {
    "wpH": (70, 250),
    "spH": (70, 250),
    "auH": (70, 250),
    "st1H": (70, 250),
    "st3H": (70, 250),
    "wpL": (40, 150),
    "spL": (40, 150),
    "auL": (40, 150),
    "st1L": (40, 150),
    "st3L": (40, 150),
    "wp_hr": (30, 220),
    "sp_hr": (30, 220),
    "au_hr": (30, 220),
    "st1_hr": (30, 220),
    "st3_hr": (30, 220),
}


def _format_ok(ok: bool) -> str:
    return "OK" if ok else "確認が必要"


def _table_exists(connection: sqlite3.Connection) -> bool:
    row = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'bp_records'"
    ).fetchone()
    return row is not None


def _event_table_exists(connection: sqlite3.Connection) -> bool:
    row = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'bp_event_records'"
    ).fetchone()
    return row is not None


def _return_home_table_exists(connection: sqlite3.Connection) -> bool:
    row = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'bp_return_home_records'"
    ).fetchone()
    return row is not None


def _find_missing_columns(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute("PRAGMA table_info(bp_records)").fetchall()
    existing_columns = {row["name"] for row in rows}
    return [column for column in DB_COLUMNS if column not in existing_columns]


def _find_duplicate_dates(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT record_date, COUNT(*) AS count
        FROM bp_records
        GROUP BY record_date
        HAVING COUNT(*) > 1
        ORDER BY record_date
        """
    ).fetchall()
    return [dict(row) for row in rows]


def _find_unusual_values(records: list[dict[str, Any]]) -> list[str]:
    findings: list[str] = []
    for record in records:
        record_date = record.get("record_date") or "日付不明"
        for column, (minimum, maximum) in BP_RANGES.items():
            value = record.get(column)
            if value is None:
                continue
            try:
                number = int(value)
            except (TypeError, ValueError):
                findings.append(f"{record_date}: {column} が数値ではありません ({value})")
                continue
            if number < minimum or number > maximum:
                findings.append(f"{record_date}: {column}={number} が確認候補です")
    return findings


def _find_sparse_records(records: list[dict[str, Any]]) -> list[str]:
    check_columns = [column for column in DB_COLUMNS if column not in {"id", "created_at", "updated_at"}]
    sparse_records: list[str] = []
    for record in records:
        empty_count = sum(1 for column in check_columns if record.get(column) in {None, ""})
        if empty_count >= len(check_columns) - 5:
            sparse_records.append(str(record.get("record_date") or "日付不明"))
    return sparse_records


def build_health_check_report() -> str:
    """DBを読み取り専用の観点で確認し、結果テキストを返します。"""
    lines = ["DB整合性チェック", "自動修復や削除は行っていません。", ""]

    try:
        db.initialize_database()
        connection = db.get_connection()
    except sqlite3.Error as error:
        return f"DB接続: 確認が必要\n詳細: {error}"

    with connection:
        table_ok = _table_exists(connection)
        event_table_ok = _event_table_exists(connection)
        return_home_table_ok = _return_home_table_exists(connection)
        lines.append(f"DB接続: OK")
        lines.append(f"テーブル: {_format_ok(table_ok)}")
        lines.append(f"イベントテーブル: {_format_ok(event_table_ok)}")
        lines.append(f"帰宅後データテーブル: {_format_ok(return_home_table_ok)}")
        if not table_ok:
            return "\n".join(lines)

        missing_columns = _find_missing_columns(connection)
        lines.append(f"必須カラム: {_format_ok(not missing_columns)}")
        if missing_columns:
            lines.append("不足カラム: " + ", ".join(missing_columns))

        duplicate_dates = _find_duplicate_dates(connection)
        lines.append(f"日付重複: {'なし' if not duplicate_dates else str(len(duplicate_dates)) + '件'}")
        for duplicate in duplicate_dates[:10]:
            lines.append(f"- {duplicate['record_date']}: {duplicate['count']}件")

    records = db.fetch_all_records()
    event_records = db.fetch_all_event_records() if event_table_ok else []
    return_home_records = db.fetch_all_return_home_records() if return_home_table_ok else []
    unusual_values = _find_unusual_values(records)
    sparse_records = _find_sparse_records(records)

    lines.append(f"不自然な血圧・脈拍値: {'なし' if not unusual_values else str(len(unusual_values)) + '件'}")
    for finding in unusual_values[:20]:
        lines.append(f"- {finding}")

    lines.append(f"空欄が多い記録: {'なし' if not sparse_records else str(len(sparse_records)) + '件'}")
    for record_date in sparse_records[:20]:
        lines.append(f"- {record_date}")

    lines.append("")
    lines.append(f"確認対象レコード数: {len(records)}件")
    lines.append(f"イベント記録数: {len(event_records)}件")
    lines.append(f"帰宅後データ記録数: {len(return_home_records)}件")
    return "\n".join(lines)
