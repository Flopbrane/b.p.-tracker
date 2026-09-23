from __future__ import annotations

from typing import Any


SYSTOLIC_COLUMNS = ["wpH", "spH", "auH", "st1H", "st3H"]
DIASTOLIC_COLUMNS = ["wpL", "spL", "auL", "st1L", "st3L"]
HIGH_MEMO_WORDS = ["背部痛", "胸痛", "息苦しい"]


def calculate_difference(left: Any, right: Any) -> int | None:
    """血圧差を安全に計算します。どちらかが未入力なら None を返します。"""
    if left is None or right is None:
        return None
    try:
        return int(left) - int(right)
    except (TypeError, ValueError):
        return None


def check_orthostatic_hint(record: dict[str, Any]) -> str:
    """座位から立位への変化を確認し、診断ではない注意文を返します。"""
    sp_h = record.get("spH")
    sp_l = record.get("spL")
    st1_h = record.get("st1H")
    st1_l = record.get("st1L")
    st3_h = record.get("st3H")
    st3_l = record.get("st3L")

    st1_h_drop = calculate_difference(sp_h, st1_h)
    st1_l_drop = calculate_difference(sp_l, st1_l)
    st3_h_drop = calculate_difference(sp_h, st3_h)
    st3_l_drop = calculate_difference(sp_l, st3_l)

    drops = [st1_h_drop, st1_l_drop, st3_h_drop, st3_l_drop]
    if all(value is None for value in drops):
        return "データ不足"

    systolic_drop = any(value is not None and value >= 20 for value in [st1_h_drop, st3_h_drop])
    diastolic_drop = any(value is not None and value >= 10 for value in [st1_l_drop, st3_l_drop])

    if systolic_drop or diastolic_drop:
        return "起立性低血圧の可能性あり。医師に相談するための記録として保存してください。"
    return "通常範囲"


def make_mark_points(record: dict[str, Any]) -> list[dict[str, str]]:
    """1件の記録から、確認用の差分ポイントを作ります。"""
    points = [
        ("起床直後と排尿後座位の差", "wpH", "auH", "朝の体位変化・自律神経の切り替え"),
        ("起床直後と座位の差", "wpH", "spH", "起床直後から座位への変動"),
        ("座位と立位1分後の差", "spH", "st1H", "起立時の変動確認"),
        ("座位と立位3分後の差", "spH", "st3H", "起立時の変動確認"),
    ]
    results: list[dict[str, str]] = []

    for title, left_key, right_key, purpose in points:
        difference = calculate_difference(record.get(left_key), record.get(right_key))
        if difference is None:
            value_text = "データ不足"
            level = "データ不足"
        else:
            value_text = f"{difference} mmHg"
            level = "確認推奨" if abs(difference) >= 20 else "通常範囲"

        results.append(
            {
                "point": title,
                "value": value_text,
                "level": level,
                "purpose": purpose,
            }
        )

    results.append(
        {
            "point": "座位から立位の低下目安",
            "value": check_orthostatic_hint(record),
            "level": check_orthostatic_hint(record),
            "purpose": "医師に相談するための記録整理",
        }
    )
    return results


def is_high_level_sample(record: dict[str, Any]) -> bool:
    for column in SYSTOLIC_COLUMNS:
        value = record.get(column)
        if value is not None and int(value) >= 140:
            return True

    for column in DIASTOLIC_COLUMNS:
        value = record.get(column)
        if value is not None and int(value) >= 90:
            return True

    memo = str(record.get("memo") or "")
    return any(word in memo for word in HIGH_MEMO_WORDS)


def is_low_level_sample(record: dict[str, Any]) -> bool:
    for column in SYSTOLIC_COLUMNS:
        value = record.get(column)
        if value is not None and int(value) < 100:
            return True

    st1_drop = calculate_difference(record.get("spH"), record.get("st1H"))
    st3_drop = calculate_difference(record.get("spH"), record.get("st3H"))
    if st1_drop is not None and st1_drop >= 20:
        return True
    if st3_drop is not None and st3_drop >= 20:
        return True

    return record.get("dizziness") == "強い"


def filter_high_level_samples(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if is_high_level_sample(record)]


def filter_low_level_samples(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if is_low_level_sample(record)]


def _average_bp(records: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    high_values = [int(record["wpH"]) for record in records if record.get("wpH") is not None]
    low_values = [int(record["wpL"]) for record in records if record.get("wpL") is not None]
    if not high_values or not low_values:
        return None, None
    return sum(high_values) / len(high_values), sum(low_values) / len(low_values)


def _format_average(records: list[dict[str, Any]]) -> str:
    high_average, low_average = _average_bp(records)
    if high_average is None or low_average is None:
        return "データ不足"
    return f"平均 {high_average:.1f} / {low_average:.1f}（{len(records)}件）"


def _judgement_from_difference(high_diff: float | None, low_diff: float | None) -> str:
    if high_diff is None or low_diff is None:
        return "データ不足"
    if abs(high_diff) >= 10 or abs(low_diff) >= 5:
        return "確認推奨"
    return "通常範囲"


def _compare_two_groups(
    title: str,
    true_label: str,
    true_records: list[dict[str, Any]],
    false_label: str,
    false_records: list[dict[str, Any]],
) -> list[str]:
    true_high, true_low = _average_bp(true_records)
    false_high, false_low = _average_bp(false_records)

    lines = [f"【{title}】"]
    lines.append(f"{true_label}: {_format_average(true_records)}")
    lines.append(f"{false_label}: {_format_average(false_records)}")

    if true_high is None or true_low is None or false_high is None or false_low is None:
        lines.append("差分: データ不足")
        lines.append("判定: データ不足")
    else:
        high_diff = true_high - false_high
        low_diff = true_low - false_low
        lines.append(f"差分: 収縮期 {high_diff:+.1f} / 拡張期 {low_diff:+.1f}")
        lines.append(f"判定: {_judgement_from_difference(high_diff, low_diff)}")

    lines.append("")
    return lines


def _group_by_text(records: list[dict[str, Any]], column: str, values: list[str]) -> list[str]:
    lines: list[str] = []
    for value in values:
        group_records = [record for record in records if record.get(column) == value]
        lines.append(f"- {value}: {_format_average(group_records)}")
    return lines


def _sleep_bucket(record: dict[str, Any]) -> str:
    sleep_hours = record.get("sleep_hours")
    if sleep_hours is None:
        return "未入力"
    hours = float(sleep_hours)
    if hours < 6:
        return "6時間未満"
    if hours <= 8:
        return "6〜8時間"
    return "8時間超"


def _concerta_bucket(record: dict[str, Any]) -> str:
    value = str(record.get("concerta_time") or "").strip()
    if not value:
        return "未入力"
    try:
        hour = int(value.split(":")[0])
    except (ValueError, IndexError):
        return "時刻形式未確認"
    if hour < 8:
        return "8時前"
    if hour < 10:
        return "8〜10時"
    return "10時以降"


def _bucket_lines(records: list[dict[str, Any]], title: str, bucket_func: Any, order: list[str]) -> list[str]:
    lines = [f"【{title}】"]
    for bucket_name in order:
        group_records = [record for record in records if bucket_func(record) == bucket_name]
        lines.append(f"- {bucket_name}: {_format_average(group_records)}")
    lines.append("")
    return lines


def make_trigger_analysis_text(records: list[dict[str, Any]]) -> str:
    """条件別に朝の起床直後血圧を比較するための文章を作ります。"""
    lines = [
        "トリガー分析",
        "この表示は医療診断ではありません。記録を見返し、医師に相談するための確認候補です。",
        "",
    ]

    drinking_yes = [
        record
        for record in records
        if record.get("drinking_prev_night") in {"少量", "多い"}
    ]
    drinking_no = [record for record in records if record.get("drinking_prev_night") == "無"]
    lines.extend(_compare_two_groups("前夜飲酒", "前夜飲酒ありの日", drinking_yes, "前夜飲酒なしの日", drinking_no))

    jardiance_yes = [record for record in records if record.get("jardiance") == "有"]
    jardiance_no = [record for record in records if record.get("jardiance") == "無"]
    lines.extend(_compare_two_groups("ジャディアンス服用", "服用ありの日", jardiance_yes, "服用なしの日", jardiance_no))

    dizziness_yes = [
        record
        for record in records
        if record.get("dizziness") in {"軽い", "強い"}
    ]
    dizziness_no = [record for record in records if record.get("dizziness") == "無"]
    lines.extend(_compare_two_groups("立ちくらみ", "立ちくらみありの日", dizziness_yes, "立ちくらみなしの日", dizziness_no))

    back_pain_yes = [record for record in records if record.get("back_pain") == "有"]
    back_pain_no = [record for record in records if record.get("back_pain") == "無"]
    lines.extend(_compare_two_groups("背部痛", "背部痛ありの日", back_pain_yes, "背部痛なしの日", back_pain_no))

    lines.append("【水分量別】")
    lines.extend(_group_by_text(records, "water_amount", ["少ない", "普通", "多い", "未入力"]))
    lines.append("")

    lines.extend(_bucket_lines(records, "睡眠時間別", _sleep_bucket, ["6時間未満", "6〜8時間", "8時間超", "未入力"]))
    lines.extend(_bucket_lines(records, "コンサータ服用時刻別", _concerta_bucket, ["8時前", "8〜10時", "10時以降", "時刻形式未確認", "未入力"]))

    return "\n".join(lines)
