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
