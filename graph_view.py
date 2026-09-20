from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt

from analysis import calculate_difference


def _values(records: list[dict[str, Any]], column: str) -> list[int | None]:
    values: list[int | None] = []
    for record in records:
        value = record.get(column)
        values.append(None if value is None else int(value))
    return values


def show_bp_graphs(records: list[dict[str, Any]]) -> None:
    """血圧・脈拍・差分の4グラフを表示します。"""
    sorted_records = sorted(records, key=lambda record: record.get("record_date") or "")
    dates = [str(record.get("record_date") or "") for record in sorted_records]

    plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "MS Gothic"]
    figure, axes = plt.subplots(2, 2, figsize=(12, 8))
    figure.suptitle("血圧・脈拍の推移")

    axes[0][0].plot(dates, _values(sorted_records, "wpH"), marker="o", label="起床直後H")
    axes[0][0].plot(dates, _values(sorted_records, "spH"), marker="o", label="座位H")
    axes[0][0].plot(dates, _values(sorted_records, "auH"), marker="o", label="排尿後H")
    axes[0][0].set_title("朝の収縮期血圧")
    axes[0][0].set_ylabel("mmHg")
    axes[0][0].legend()

    axes[0][1].plot(dates, _values(sorted_records, "wpL"), marker="o", label="起床直後L")
    axes[0][1].plot(dates, _values(sorted_records, "spL"), marker="o", label="座位L")
    axes[0][1].plot(dates, _values(sorted_records, "auL"), marker="o", label="排尿後L")
    axes[0][1].set_title("朝の拡張期血圧")
    axes[0][1].set_ylabel("mmHg")
    axes[0][1].legend()

    axes[1][0].plot(dates, _values(sorted_records, "wp_hr"), marker="o", label="起床直後 pulse")
    axes[1][0].plot(dates, _values(sorted_records, "sp_hr"), marker="o", label="座位 pulse")
    axes[1][0].plot(dates, _values(sorted_records, "au_hr"), marker="o", label="排尿後 pulse")
    axes[1][0].set_title("脈拍")
    axes[1][0].set_ylabel("回/分")
    axes[1][0].legend()

    wp_au_diffs = [calculate_difference(record.get("wpH"), record.get("auH")) for record in sorted_records]
    sp_st1_diffs = [calculate_difference(record.get("spH"), record.get("st1H")) for record in sorted_records]
    sp_st3_diffs = [calculate_difference(record.get("spH"), record.get("st3H")) for record in sorted_records]
    axes[1][1].plot(dates, wp_au_diffs, marker="o", label="起床直後H - 排尿後H")
    axes[1][1].plot(dates, sp_st1_diffs, marker="o", label="座位H - 立位1分H")
    axes[1][1].plot(dates, sp_st3_diffs, marker="o", label="座位H - 立位3分H")
    axes[1][1].set_title("血圧差")
    axes[1][1].set_ylabel("mmHg")
    axes[1][1].legend()

    for axis in axes.flat:
        axis.set_xlabel("記録日")
        axis.tick_params(axis="x", rotation=45)
        axis.grid(True, alpha=0.3)

    figure.tight_layout()
    plt.show()
