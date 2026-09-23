from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from constants import BACKUPS_DIR, DB_PATH


def create_database_backup(
    db_path: Path = DB_PATH,
    backup_dir: Path = BACKUPS_DIR,
) -> Path:
    """SQLite DB を日時付きファイル名でバックアップします。"""
    if not db_path.exists():
        raise FileNotFoundError(f"DBファイルが見つかりません: {db_path}")

    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"bp_tracker_backup_{timestamp}.sqlite3"

    counter = 1
    while backup_path.exists():
        backup_path = backup_dir / f"bp_tracker_backup_{timestamp}_{counter}.sqlite3"
        counter += 1

    shutil.copy2(db_path, backup_path)
    return backup_path
