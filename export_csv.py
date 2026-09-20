from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any

from constants import DB_COLUMNS, EXPORTS_DIR


def export_records_to_csv(
    records: list[dict[str, Any]],
    export_dir: Path = EXPORTS_DIR,
    start_date: str | None = None,
    end_date: str | None = None,
) -> Path:
    export_dir.mkdir(parents=True, exist_ok=True)
    if start_date and end_date:
        start_text = start_date.replace("-", "")
        end_text = end_date.replace("-", "")
        file_name = f"bp_records_{start_text}_{end_text}.csv"
    else:
        today_text = date.today().strftime("%Y%m%d")
        file_name = f"bp_records_{today_text}.csv"
    export_path = export_dir / file_name

    with export_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=DB_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    return export_path
