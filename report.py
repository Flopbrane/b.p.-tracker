from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path
from typing import Any

from analysis import filter_high_level_samples, filter_low_level_samples, make_mark_points
from constants import COLUMN_LABELS, MEDICAL_DISCLAIMER, REPORTS_DIR


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    return escape(str(value))


def _record_table(records: list[dict[str, Any]]) -> str:
    columns = [
        "record_date",
        "wpH",
        "wpL",
        "wp_hr",
        "spH",
        "spL",
        "sp_hr",
        "auH",
        "auL",
        "au_hr",
        "st1H",
        "st1L",
        "st3H",
        "st3L",
        "dizziness",
        "drinking_prev_night",
        "memo",
    ]
    header = "".join(f"<th>{escape(COLUMN_LABELS[column])}</th>" for column in columns)
    rows = []
    for record in records:
        cells = "".join(f"<td>{_format_value(record.get(column))}</td>" for column in columns)
        rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def _mark_point_table(records: list[dict[str, Any]]) -> str:
    rows = []
    for record in records:
        for point in make_mark_points(record):
            rows.append(
                "<tr>"
                f"<td>{_format_value(record.get('record_date'))}</td>"
                f"<td>{escape(point['point'])}</td>"
                f"<td>{escape(point['value'])}</td>"
                f"<td>{escape(point['level'])}</td>"
                f"<td>{escape(point['purpose'])}</td>"
                "</tr>"
            )
    return (
        "<table><thead><tr>"
        "<th>記録日</th><th>見るポイント</th><th>値</th><th>判定候補</th><th>目的</th>"
        "</tr></thead><tbody>"
        f"{''.join(rows)}"
        "</tbody></table>"
    )


def export_medical_report(
    records: list[dict[str, Any]],
    start_date: str | None = None,
    end_date: str | None = None,
    report_dir: Path = REPORTS_DIR,
) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    today_text = date.today().strftime("%Y%m%d")
    if start_date and end_date:
        file_name = f"bp_report_{start_date.replace('-', '')}_{end_date.replace('-', '')}.html"
        period_text = f"{escape(start_date)} から {escape(end_date)}"
    else:
        file_name = f"bp_report_{today_text}.html"
        period_text = "全期間"

    high_samples = filter_high_level_samples(records)
    low_samples = filter_low_level_samples(records)
    html = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>血圧記録 診察用レポート</title>
  <style>
    body {{ font-family: "Yu Gothic", "Meiryo", sans-serif; line-height: 1.6; margin: 24px; color: #222; }}
    h1, h2 {{ margin-bottom: 8px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 28px; font-size: 13px; }}
    th, td {{ border: 1px solid #bbb; padding: 6px 8px; vertical-align: top; }}
    th {{ background: #f0f3f7; }}
    .notice {{ border: 1px solid #d49a5b; background: #fff8ef; padding: 12px; white-space: pre-line; }}
  </style>
</head>
<body>
  <h1>血圧記録 診察用レポート</h1>
  <p>対象期間: {period_text}</p>
  <div class="notice">{escape(MEDICAL_DISCLAIMER)}</div>

  <h2>全記録</h2>
  {_record_table(records)}

  <h2>Hi-Level Sample</h2>
  {_record_table(high_samples) if high_samples else "<p>該当する記録はありません。</p>"}

  <h2>Low-Level Sample</h2>
  {_record_table(low_samples) if low_samples else "<p>該当する記録はありません。</p>"}

  <h2>マークポイント</h2>
  {_mark_point_table(records)}
</body>
</html>
"""
    report_path = report_dir / file_name
    report_path.write_text(html, encoding="utf-8")
    return report_path
