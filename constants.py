from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
BACKUPS_DIR = BASE_DIR / "backups"
DB_PATH = DATA_DIR / "bp_tracker.sqlite3"

APP_TITLE = "血圧記録アプリ Ver.0.6"

MEDICAL_DISCLAIMER = (
    "このアプリは医療診断を行うものではありません。\n"
    "血圧・脈拍・服薬・症状を記録し、医師に相談するための補助ツールです。\n"
    "強い胸痛、背部痛、息苦しさ、冷や汗、意識が遠のく感じなどがある場合は、"
    "記録よりも受診を優先してください。"
)

JARDIANCE_VALUES = ["有", "無", "未入力"]
DIZZINESS_VALUES = ["無", "軽い", "強い", "未入力"]
DRINKING_VALUES = ["無", "少量", "多い", "未入力"]
WATER_VALUES = ["少ない", "普通", "多い", "未入力"]
YES_NO_VALUES = ["無", "有", "未入力"]
CAFFEINE_VALUES = ["無", "少量", "多い", "未入力"]
SLEEP_QUALITY_VALUES = ["良い", "普通", "悪い", "未入力"]
STRESS_VALUES = ["低い", "普通", "高い", "未入力"]

DB_COLUMNS = [
    "id",
    "record_date",
    "wake_time",
    "sleep_time",
    "sleep_hours",
    "weight",
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
    "st1_hr",
    "st3H",
    "st3L",
    "st3_hr",
    "concerta_time",
    "jardiance",
    "metgluco_count",
    "dizziness",
    "drinking_prev_night",
    "water_amount",
    "back_pain",
    "ear_face_pain",
    "meal_memo",
    "salt_memo",
    "caffeine",
    "exercise_movement",
    "outing",
    "bathing",
    "sleep_quality",
    "stress_level",
    "pc_work_hours",
    "neck_shoulder_jaw_tension",
    "teeth_clenching",
    "headache",
    "back_pain_detail",
    "dizziness_detail",
    "memo",
    "created_at",
    "updated_at",
]

EDITABLE_COLUMNS = [
    column
    for column in DB_COLUMNS
    if column not in {"id", "created_at", "updated_at"}
]

TREE_COLUMNS = [
    "id",
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
    "concerta_time",
    "jardiance",
    "dizziness",
    "drinking_prev_night",
    "caffeine",
    "sleep_quality",
    "stress_level",
    "memo",
]

REPORTS_DIR = BASE_DIR / "reports"

EXTRA_COLUMN_SQL_TYPES = {
    "meal_memo": "TEXT",
    "salt_memo": "TEXT",
    "caffeine": "TEXT",
    "exercise_movement": "TEXT",
    "outing": "TEXT",
    "bathing": "TEXT",
    "sleep_quality": "TEXT",
    "stress_level": "TEXT",
    "pc_work_hours": "REAL",
    "neck_shoulder_jaw_tension": "TEXT",
    "teeth_clenching": "TEXT",
    "headache": "TEXT",
    "back_pain_detail": "TEXT",
    "dizziness_detail": "TEXT",
}

COLUMN_LABELS = {
    "id": "ID",
    "record_date": "記録日",
    "wake_time": "起床時刻",
    "sleep_time": "就寝時刻",
    "sleep_hours": "睡眠時間",
    "weight": "体重",
    "wpH": "起床直後H",
    "wpL": "起床直後L",
    "wp_hr": "起床直後脈拍",
    "spH": "座位H",
    "spL": "座位L",
    "sp_hr": "座位脈拍",
    "auH": "排尿後H",
    "auL": "排尿後L",
    "au_hr": "排尿後脈拍",
    "st1H": "立位1分H",
    "st1L": "立位1分L",
    "st1_hr": "立位1分脈拍",
    "st3H": "立位3分H",
    "st3L": "立位3分L",
    "st3_hr": "立位3分脈拍",
    "concerta_time": "コンサータ時刻",
    "jardiance": "ジャディアンス",
    "metgluco_count": "メトグルコ回数",
    "dizziness": "立ちくらみ",
    "drinking_prev_night": "前夜飲酒",
    "water_amount": "水分量",
    "back_pain": "背部痛",
    "ear_face_pain": "耳痛・顔面痛",
    "meal_memo": "食事メモ",
    "salt_memo": "塩分メモ",
    "caffeine": "カフェイン摂取",
    "exercise_movement": "運動・自転車移動",
    "outing": "外出",
    "bathing": "入浴",
    "sleep_quality": "睡眠の質",
    "stress_level": "ストレス度",
    "pc_work_hours": "PC作業時間",
    "neck_shoulder_jaw_tension": "首・肩・顎の張り",
    "teeth_clenching": "食いしばり自覚",
    "headache": "頭痛",
    "back_pain_detail": "背部痛の詳細",
    "dizziness_detail": "めまい・ふらつき詳細",
    "memo": "メモ",
    "created_at": "作成日時",
    "updated_at": "更新日時",
}
