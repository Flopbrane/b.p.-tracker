from __future__ import annotations

import sqlite3
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk
from typing import Any

import analysis
import backup
import db
import db_health
from constants import (
    APP_TITLE,
    CAFFEINE_VALUES,
    COLUMN_LABELS,
    DIZZINESS_VALUES,
    DRINKING_VALUES,
    EDITABLE_COLUMNS,
    EVENT_COLUMN_LABELS,
    EVENT_EDITABLE_COLUMNS,
    EVENT_SYMPTOM_VALUES,
    EVENT_TREE_COLUMNS,
    EVENT_TYPE_VALUES,
    JARDIANCE_VALUES,
    MEDICAL_DISCLAIMER,
    RETURN_HOME_ACTIVITY_VALUES,
    RETURN_HOME_COLUMN_LABELS,
    RETURN_HOME_EDITABLE_COLUMNS,
    RETURN_HOME_TREE_COLUMNS,
    SLEEP_QUALITY_VALUES,
    STRESS_VALUES,
    TREE_COLUMNS,
    WATER_VALUES,
    YES_NO_VALUES,
)
from export_csv import export_records_to_csv
from final_mini_calendar import ask_date
from graph_view import show_bp_graphs
from report import export_medical_report


INTEGER_FIELDS = {
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
    "metgluco_count",
}

REAL_FIELDS = {"sleep_hours", "weight", "pc_work_hours"}
REQUIRED_FIELDS = {"record_date"}
COMBO_FIELDS = {
    "jardiance",
    "dizziness",
    "drinking_prev_night",
    "water_amount",
    "back_pain",
    "ear_face_pain",
    "caffeine",
    "outing",
    "bathing",
    "sleep_quality",
    "stress_level",
    "neck_shoulder_jaw_tension",
    "teeth_clenching",
    "headache",
}


class BloodPressureApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1280x820")
        self.selected_record_id: int | None = None
        self.vars: dict[str, tk.StringVar] = {}
        self.current_records: list[dict[str, Any]] = []
        self.current_start_date: str | None = None
        self.current_end_date: str | None = None
        self.status_var = tk.StringVar(value="全期間表示")

        db.initialize_database()

        self._create_widgets()
        self.load_all_records()

    def _create_widgets(self) -> None:
        disclaimer = ttk.Label(
            self.root,
            text=MEDICAL_DISCLAIMER,
            foreground="#7a2d00",
            justify="left",
            wraplength=1200,
        )
        disclaimer.pack(fill="x", padx=12, pady=(10, 6))

        main_area = ttk.Frame(self.root)
        main_area.pack(fill="both", expand=True, padx=12, pady=6)

        form_frame = ttk.LabelFrame(main_area, text="入力フォーム")
        form_frame.pack(side="top", fill="x")

        self._create_form(form_frame)
        self._create_input_aids(main_area)
        self._create_buttons(main_area)
        self._create_tree(main_area)

    def _create_form(self, parent: ttk.Frame) -> None:
        fields = [
            ("record_date", "記録日 (YYYY-MM-DD)", "entry"),
            ("wake_time", "起床時刻", "entry"),
            ("sleep_time", "就寝時刻", "entry"),
            ("sleep_hours", "睡眠時間", "entry"),
            ("weight", "体重", "entry"),
            ("wpH", "起床直後 H", "entry"),
            ("wpL", "起床直後 L", "entry"),
            ("wp_hr", "起床直後 pulse", "entry"),
            ("spH", "座位 H", "entry"),
            ("spL", "座位 L", "entry"),
            ("sp_hr", "座位 pulse", "entry"),
            ("auH", "排尿後 H", "entry"),
            ("auL", "排尿後 L", "entry"),
            ("au_hr", "排尿後 pulse", "entry"),
            ("st1H", "立位1分 H", "entry"),
            ("st1L", "立位1分 L", "entry"),
            ("st1_hr", "立位1分 pulse", "entry"),
            ("st3H", "立位3分 H", "entry"),
            ("st3L", "立位3分 L", "entry"),
            ("st3_hr", "立位3分 pulse", "entry"),
            ("concerta_time", "コンサータ時刻", "entry"),
            ("jardiance", "ジャディアンス", "combo_jardiance"),
            ("metgluco_count", "メトグルコ回数", "entry"),
            ("dizziness", "立ちくらみ", "combo_dizziness"),
            ("drinking_prev_night", "前夜飲酒", "combo_drinking"),
            ("water_amount", "水分量", "combo_water"),
            ("back_pain", "背部痛", "combo_yes_no"),
            ("ear_face_pain", "耳痛・顔面痛", "combo_yes_no"),
            ("meal_memo", "食事メモ", "entry"),
            ("salt_memo", "塩分メモ", "entry"),
            ("caffeine", "カフェイン摂取", "combo_caffeine"),
            ("exercise_movement", "運動・自転車移動", "entry"),
            ("outing", "外出", "combo_yes_no"),
            ("bathing", "入浴", "combo_yes_no"),
            ("sleep_quality", "睡眠の質", "combo_sleep_quality"),
            ("stress_level", "ストレス度", "combo_stress"),
            ("pc_work_hours", "PC作業時間", "entry"),
            ("neck_shoulder_jaw_tension", "首・肩・顎の張り", "combo_yes_no"),
            ("teeth_clenching", "食いしばり自覚", "combo_yes_no"),
            ("headache", "頭痛", "combo_yes_no"),
            ("back_pain_detail", "背部痛の詳細", "entry"),
            ("dizziness_detail", "めまい・ふらつき詳細", "entry"),
        ]

        for index, (column, label_text, widget_type) in enumerate(fields):
            row = index // 4
            col = (index % 4) * 2
            ttk.Label(parent, text=label_text).grid(row=row, column=col, sticky="w", padx=6, pady=4)

            variable = tk.StringVar()
            self.vars[column] = variable

            if widget_type == "entry":
                widget = ttk.Entry(parent, textvariable=variable, width=18)
            else:
                widget = ttk.Combobox(
                    parent,
                    textvariable=variable,
                    values=self._combo_values(widget_type),
                    state="readonly",
                    width=16,
                )
                variable.set("未入力")

            widget.grid(row=row, column=col + 1, sticky="ew", padx=6, pady=4)
            if column == "record_date":
                widget.bind("<Button-1>", self.choose_record_date)

        memo_row = (len(fields) + 3) // 4
        ttk.Label(parent, text="メモ").grid(row=memo_row, column=0, sticky="nw", padx=6, pady=4)
        self.memo_text = tk.Text(parent, height=4, width=80)
        self.memo_text.grid(row=memo_row, column=1, columnspan=7, sticky="ew", padx=6, pady=4)

        for column_index in range(8):
            parent.columnconfigure(column_index, weight=1)
        self.vars["record_date"].set(date.today().isoformat())

    def _combo_values(self, widget_type: str) -> list[str]:
        if widget_type == "combo_jardiance":
            return JARDIANCE_VALUES
        if widget_type == "combo_dizziness":
            return DIZZINESS_VALUES
        if widget_type == "combo_drinking":
            return DRINKING_VALUES
        if widget_type == "combo_water":
            return WATER_VALUES
        if widget_type == "combo_caffeine":
            return CAFFEINE_VALUES
        if widget_type == "combo_sleep_quality":
            return SLEEP_QUALITY_VALUES
        if widget_type == "combo_stress":
            return STRESS_VALUES
        return YES_NO_VALUES

    def _create_input_aids(self, parent: ttk.Frame) -> None:
        aid_frame = ttk.LabelFrame(parent, text="入力補助")
        aid_frame.pack(fill="x", pady=(8, 0))

        ttk.Label(aid_frame, text="コンサータ").pack(side="left", padx=(6, 2))
        for time_text in ["07:00", "07:30", "08:00", "08:30", "09:00"]:
            ttk.Button(
                aid_frame,
                text=time_text,
                command=lambda value=time_text: self.vars["concerta_time"].set(value),
            ).pack(side="left", padx=2, pady=4)

        ttk.Label(aid_frame, text="メトグルコ").pack(side="left", padx=(12, 2))
        for count_text in ["0", "1", "2", "3"]:
            ttk.Button(
                aid_frame,
                text=count_text,
                command=lambda value=count_text: self.vars["metgluco_count"].set(value),
            ).pack(side="left", padx=2, pady=4)

        ttk.Button(aid_frame, text="前回一部コピー", command=self.copy_previous_partial_record).pack(
            side="left",
            padx=(12, 2),
            pady=4,
        )
        ttk.Button(aid_frame, text="メモテンプレート追加", command=self.append_memo_template).pack(
            side="left",
            padx=2,
            pady=4,
        )

    def _create_buttons(self, parent: ttk.Frame) -> None:
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=8)

        buttons = [
            ("保存", self.save_record),
            ("選択行読み込み", self.load_selected_record),
            ("更新", self.update_selected_record),
            ("削除", self.delete_selected_record),
            ("全期間表示", self.load_all_records),
            ("期間指定表示", self.load_period_records),
            ("CSV出力", self.export_csv),
            ("グラフ表示", self.show_graph),
            ("Hi-Level Sample 抽出", self.show_high_level_samples),
            ("Low-Level Sample 抽出", self.show_low_level_samples),
            ("マークポイント表示", self.show_mark_points),
            ("トリガー分析表示", self.show_trigger_analysis),
            ("帰宅後データ", self.open_return_home_window),
            ("診察用レポート出力", self.export_report),
            ("バックアップ作成", self.create_backup),
            ("DB整合性チェック", self.show_db_health),
        ]

        max_columns = 7
        for index, (text, command) in enumerate(buttons):
            row = index // max_columns
            column = index % max_columns
            ttk.Button(button_frame, text=text, command=command).grid(row=row, column=column, padx=4, pady=3, sticky="ew")

        ttk.Label(button_frame, textvariable=self.status_var).grid(
            row=(len(buttons) // max_columns) + 1,
            column=0,
            columnspan=max_columns,
            sticky="w",
            padx=4,
            pady=(4, 0),
        )

        for column in range(max_columns):
            button_frame.columnconfigure(column, weight=1)

    def _create_tree(self, parent: ttk.Frame) -> None:
        tree_frame = ttk.LabelFrame(parent, text="保存済み記録")
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=TREE_COLUMNS, show="headings", height=14)
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        for column in TREE_COLUMNS:
            self.tree.heading(column, text=COLUMN_LABELS[column])
            width = 90
            if column == "memo":
                width = 260
            elif column == "record_date":
                width = 110
            self.tree.column(column, width=width, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

    def _collect_form_data(self) -> dict[str, Any] | None:
        record: dict[str, Any] = {}

        for column in EDITABLE_COLUMNS:
            if column == "memo":
                value = self.memo_text.get("1.0", "end").strip()
            else:
                value = self.vars[column].get().strip()

            if column in REQUIRED_FIELDS and not value:
                messagebox.showerror("入力エラー", "日付が未入力です。")
                return None

            if value == "":
                record[column] = None
                continue

            try:
                if column in INTEGER_FIELDS:
                    record[column] = int(value)
                elif column in REAL_FIELDS:
                    record[column] = float(value)
                else:
                    record[column] = value
            except ValueError:
                messagebox.showerror("入力エラー", f"{COLUMN_LABELS[column]} には数字を入力してください。")
                return None

        return record

    def save_record(self) -> None:
        record = self._collect_form_data()
        if record is None:
            return

        if not self._confirm_record_action("保存", record):
            return

        try:
            db.insert_record(record)
        except sqlite3.IntegrityError:
            messagebox.showerror("保存エラー", "同じ記録日のデータがすでにあります。更新を使ってください。")
            return
        except sqlite3.Error as error:
            messagebox.showerror("保存エラー", f"DB保存に失敗しました。\n{error}")
            return

        messagebox.showinfo("保存完了", "記録を保存しました。")
        self.clear_form()
        self.load_all_records()

    def load_all_records(self) -> None:
        self.current_start_date = None
        self.current_end_date = None
        self.selected_record_id = None
        self.status_var.set("全期間表示")
        try:
            records = db.fetch_all_records()
        except sqlite3.Error as error:
            messagebox.showerror("読み込みエラー", f"DB読み込みに失敗しました。\n{error}")
            return
        self._display_records(records)

    def load_period_records(self) -> None:
        period = self._ask_period()
        if period is None:
            return

        start_date, end_date = period
        try:
            records = db.fetch_records_by_period(start_date, end_date)
        except sqlite3.Error as error:
            messagebox.showerror("読み込みエラー", f"DB読み込みに失敗しました。\n{error}")
            return

        self.current_start_date = start_date
        self.current_end_date = end_date
        self.selected_record_id = None
        self.status_var.set(f"期間指定表示: {start_date} から {end_date} / {len(records)}件")
        self._display_records(records)

    def _display_records(self, records: list[dict[str, Any]]) -> None:
        self.current_records = records
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        for record in records:
            values = [record.get(column) if record.get(column) is not None else "" for column in TREE_COLUMNS]
            self.tree.insert("", "end", values=values)

    def _ask_period(self) -> tuple[str, str] | None:
        start_date = ask_date(self.root, title="開始日を選択", initial_date=date.today())
        if not start_date:
            return None
        end_initial_date = date.fromisoformat(start_date)
        end_date = ask_date(self.root, title="終了日を選択", initial_date=end_initial_date)
        if not end_date:
            return None
        if start_date > end_date:
            messagebox.showerror("期間指定エラー", "開始日は終了日以前の日付にしてください。")
            return None
        return start_date, end_date

    def choose_record_date(self, event: tk.Event | None = None) -> str:
        current_value = self.vars["record_date"].get().strip()
        try:
            initial_date = date.fromisoformat(current_value) if current_value else date.today()
        except ValueError:
            initial_date = date.today()

        selected_date = ask_date(self.root, title="記録日を選択", initial_date=initial_date)
        if selected_date:
            self.vars["record_date"].set(selected_date)
        return "break"

    def load_selected_record(self) -> None:
        record_id = self._get_selected_record_id()
        if record_id is None:
            messagebox.showwarning("選択エラー", "読み込む行を選択してください。")
            return

        record = db.fetch_record_by_id(record_id)
        if record is None:
            messagebox.showerror("読み込みエラー", "選択した記録が見つかりません。")
            return

        self.selected_record_id = record_id
        for column in EDITABLE_COLUMNS:
            value = record.get(column)
            if column == "memo":
                self.memo_text.delete("1.0", "end")
                self.memo_text.insert("1.0", "" if value is None else str(value))
            else:
                self.vars[column].set("" if value is None else str(value))

    def update_selected_record(self) -> None:
        if self.selected_record_id is None:
            messagebox.showwarning("更新エラー", "更新対象が選択されていません。")
            return

        record = self._collect_form_data()
        if record is None:
            return

        if not self._confirm_record_action("更新", record):
            return

        try:
            db.update_record(self.selected_record_id, record)
        except sqlite3.IntegrityError:
            messagebox.showerror("更新エラー", "同じ記録日のデータがすでにあります。")
            return
        except sqlite3.Error as error:
            messagebox.showerror("更新エラー", f"DB更新に失敗しました。\n{error}")
            return

        messagebox.showinfo("更新完了", "記録を更新しました。")
        self.clear_form()
        self.load_all_records()

    def delete_selected_record(self) -> None:
        record_id = self._get_selected_record_id()
        if record_id is None:
            messagebox.showwarning("削除エラー", "削除対象が選択されていません。")
            return

        if not messagebox.askyesno("削除確認", "選択した記録を削除しますか？"):
            return

        try:
            db.delete_record(record_id)
        except sqlite3.Error as error:
            messagebox.showerror("削除エラー", f"DB削除に失敗しました。\n{error}")
            return

        messagebox.showinfo("削除完了", "記録を削除しました。")
        self.clear_form()
        self.load_all_records()

    def export_csv(self) -> None:
        records = db.fetch_records_for_csv(self.current_start_date, self.current_end_date)
        if not records:
            messagebox.showwarning("CSV出力", "出力するデータがありません。")
            return

        try:
            export_path = export_records_to_csv(
                records,
                start_date=self.current_start_date,
                end_date=self.current_end_date,
            )
        except OSError as error:
            messagebox.showerror("CSV出力エラー", f"CSV出力に失敗しました。\n{error}")
            return

        messagebox.showinfo("CSV出力完了", f"CSVを出力しました。\n{export_path}")

    def show_graph(self) -> None:
        if not self.current_records:
            messagebox.showwarning("グラフ表示", "グラフ表示対象データが存在しません。")
            return
        show_bp_graphs(self.current_records)

    def show_high_level_samples(self) -> None:
        records = analysis.filter_high_level_samples(self.current_records)
        self.status_var.set(f"Hi-Level Sample: {len(records)}件")
        self._display_records(records)

    def show_low_level_samples(self) -> None:
        records = analysis.filter_low_level_samples(self.current_records)
        self.status_var.set(f"Low-Level Sample: {len(records)}件")
        self._display_records(records)

    def show_mark_points(self) -> None:
        record = self._get_selected_full_record()
        if record is None:
            if not self.current_records:
                messagebox.showwarning("マークポイント", "表示対象データが存在しません。")
                return
            records = self.current_records
            title = "マークポイント一覧"
        else:
            records = [record]
            title = f"マークポイント: {record.get('record_date')}"

        lines: list[str] = []
        for target_record in records:
            lines.append(f"記録日: {target_record.get('record_date')}")
            for point in analysis.make_mark_points(target_record):
                lines.append(
                    f"・{point['point']} / {point['value']} / {point['level']} / {point['purpose']}"
                )
            lines.append("")
        self._show_text_window(title, "\n".join(lines))

    def show_trigger_analysis(self) -> None:
        if not self.current_records:
            messagebox.showwarning("トリガー分析", "分析対象データが存在しません。")
            return
        text = analysis.make_trigger_analysis_text(self.current_records)
        self._show_text_window("トリガー分析", text)

    def export_report(self) -> None:
        records = db.fetch_records_for_csv(self.current_start_date, self.current_end_date)
        if not records:
            messagebox.showwarning("レポート出力", "出力するデータがありません。")
            return

        try:
            report_path = export_medical_report(
                records,
                start_date=self.current_start_date,
                end_date=self.current_end_date,
            )
        except OSError as error:
            messagebox.showerror("レポート出力エラー", f"レポート出力に失敗しました。\n{error}")
            return

        messagebox.showinfo("レポート出力完了", f"診察用HTMLレポートを出力しました。\n{report_path}")

    def create_backup(self) -> None:
        try:
            backup_path = backup.create_database_backup()
        except OSError as error:
            messagebox.showerror("バックアップエラー", f"バックアップに失敗しました。\n{error}")
            return

        messagebox.showinfo("バックアップ完了", f"DBをバックアップしました。\n{backup_path}")

    def show_db_health(self) -> None:
        report_text = db_health.build_health_check_report()
        self._show_text_window("DB整合性チェック", report_text)

    def open_event_window(self) -> None:
        EventRecordWindow(self.root)

    def open_return_home_window(self) -> None:
        ReturnHomeRecordWindow(self.root)

    def copy_previous_partial_record(self) -> None:
        records = db.fetch_all_records()
        if not records:
            messagebox.showinfo("前回一部コピー", "コピー元になる記録がありません。")
            return

        previous = records[0]
        copy_columns = [
            "wake_time",
            "sleep_time",
            "sleep_hours",
            "concerta_time",
            "jardiance",
            "metgluco_count",
            "water_amount",
            "caffeine",
            "sleep_quality",
            "stress_level",
        ]
        for column in copy_columns:
            value = previous.get(column)
            if value is not None and column in self.vars:
                self.vars[column].set(str(value))

        messagebox.showinfo("前回一部コピー", "前回記録から一部の入力値をコピーしました。")

    def append_memo_template(self) -> None:
        template = "\n".join(
            [
                "立ちくらみ: ",
                "背部痛: ",
                "前夜飲酒: ",
                "水分: ",
                "睡眠: ",
            ]
        )
        current_text = self.memo_text.get("1.0", "end").strip()
        insert_text = f"\n{template}" if current_text else template
        self.memo_text.insert("end", insert_text)

    def _confirm_record_action(self, action_name: str, record: dict[str, Any]) -> bool:
        summary = (
            f"{action_name}しますか？\n\n"
            f"記録日: {record.get('record_date')}\n"
            f"起床直後: {record.get('wpH') or ''} / {record.get('wpL') or ''} "
            f"pulse {record.get('wp_hr') or ''}\n"
            f"座位: {record.get('spH') or ''} / {record.get('spL') or ''} "
            f"pulse {record.get('sp_hr') or ''}\n"
            f"排尿後: {record.get('auH') or ''} / {record.get('auL') or ''} "
            f"pulse {record.get('au_hr') or ''}"
        )
        return messagebox.askyesno(f"{action_name}確認", summary)

    def _show_text_window(self, title: str, text: str) -> None:
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("900x520")
        text_area = tk.Text(window, wrap="word")
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        text_area.insert("1.0", text)
        text_area.configure(state="disabled")

    def _get_selected_full_record(self) -> dict[str, Any] | None:
        record_id = self._get_selected_record_id()
        if record_id is None:
            return None
        return db.fetch_record_by_id(record_id)

    def clear_form(self) -> None:
        self.selected_record_id = None
        for column, variable in self.vars.items():
            if column in COMBO_FIELDS:
                variable.set("未入力")
            else:
                variable.set("")
        self.vars["record_date"].set(date.today().isoformat())
        self.memo_text.delete("1.0", "end")

    def _get_selected_record_id(self) -> int | None:
        selected_items = self.tree.selection()
        if not selected_items:
            return None

        values = self.tree.item(selected_items[0], "values")
        if not values:
            return None

        try:
            return int(values[0])
        except ValueError:
            return None


def main() -> None:
    root = tk.Tk()
    BloodPressureApp(root)
    root.mainloop()


class EventRecordWindow:
    def __init__(self, parent: tk.Misc) -> None:
        self.window = tk.Toplevel(parent)
        self.window.title("姿勢変化イベント記録")
        self.window.geometry("1180x680")
        self.vars: dict[str, tk.StringVar] = {}
        self.memo_text: tk.Text
        self.tree: ttk.Treeview

        self._create_widgets()
        self.clear_form()
        self.load_events()

    def _create_widgets(self) -> None:
        notice = ttk.Label(
            self.window,
            text="この記録は医療診断ではありません。しゃがみ込み、立ち上がり、入浴後などの前後差を医師に相談するための補助記録です。",
            foreground="#7a2d00",
            wraplength=1120,
            justify="left",
        )
        notice.pack(fill="x", padx=10, pady=(10, 6))

        form_frame = ttk.LabelFrame(self.window, text="イベント入力")
        form_frame.pack(fill="x", padx=10, pady=6)

        fields = [
            ("event_date", "日付", "entry"),
            ("event_time", "時刻", "entry"),
            ("event_type", "イベント", "combo_event_type"),
            ("symptom", "症状", "combo_symptom"),
            ("before_sys", "前 H", "entry"),
            ("before_dia", "前 L", "entry"),
            ("before_pulse", "前 pulse", "entry"),
            ("after_sys", "後 H", "entry"),
            ("after_dia", "後 L", "entry"),
            ("after_pulse", "後 pulse", "entry"),
            ("after_1min_sys", "1分後 H", "entry"),
            ("after_1min_dia", "1分後 L", "entry"),
            ("after_1min_pulse", "1分後 pulse", "entry"),
        ]

        for index, (column, label_text, widget_type) in enumerate(fields):
            row = index // 4
            grid_column = (index % 4) * 2
            ttk.Label(form_frame, text=label_text).grid(row=row, column=grid_column, sticky="w", padx=6, pady=4)
            variable = tk.StringVar()
            self.vars[column] = variable
            if widget_type == "combo_event_type":
                widget = ttk.Combobox(form_frame, textvariable=variable, values=EVENT_TYPE_VALUES, state="readonly", width=18)
            elif widget_type == "combo_symptom":
                widget = ttk.Combobox(form_frame, textvariable=variable, values=EVENT_SYMPTOM_VALUES, state="readonly", width=18)
            else:
                widget = ttk.Entry(form_frame, textvariable=variable, width=20)
            widget.grid(row=row, column=grid_column + 1, sticky="ew", padx=6, pady=4)
            if column == "event_date":
                widget.bind("<Button-1>", self.choose_event_date)

        memo_row = (len(fields) + 3) // 4
        ttk.Label(form_frame, text="メモ").grid(row=memo_row, column=0, sticky="nw", padx=6, pady=4)
        self.memo_text = tk.Text(form_frame, height=3, width=80)
        self.memo_text.grid(row=memo_row, column=1, columnspan=7, sticky="ew", padx=6, pady=4)

        for column in range(8):
            form_frame.columnconfigure(column, weight=1)

        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", padx=10, pady=6)
        ttk.Button(button_frame, text="イベント保存", command=self.save_event).pack(side="left", padx=4)
        ttk.Button(button_frame, text="選択イベント削除", command=self.delete_selected_event).pack(side="left", padx=4)
        ttk.Button(button_frame, text="再読み込み", command=self.load_events).pack(side="left", padx=4)
        ttk.Button(button_frame, text="入力クリア", command=self.clear_form).pack(side="left", padx=4)

        tree_frame = ttk.LabelFrame(self.window, text="イベント一覧")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tree = ttk.Treeview(tree_frame, columns=EVENT_TREE_COLUMNS, show="headings", height=12)
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        for column in EVENT_TREE_COLUMNS:
            self.tree.heading(column, text=EVENT_COLUMN_LABELS[column])
            width = 90
            if column in {"event_type", "judgement", "memo"}:
                width = 180
            self.tree.column(column, width=width, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

    def choose_event_date(self, event: tk.Event | None = None) -> str:
        current_value = self.vars["event_date"].get().strip()
        try:
            initial_date = date.fromisoformat(current_value) if current_value else date.today()
        except ValueError:
            initial_date = date.today()
        selected_date = ask_date(self.window, title="イベント日を選択", initial_date=initial_date)
        if selected_date:
            self.vars["event_date"].set(selected_date)
        return "break"

    def _collect_event_data(self) -> dict[str, Any] | None:
        record: dict[str, Any] = {}
        integer_columns = {
            "before_sys",
            "before_dia",
            "before_pulse",
            "after_sys",
            "after_dia",
            "after_pulse",
            "after_1min_sys",
            "after_1min_dia",
            "after_1min_pulse",
        }

        for column in EVENT_EDITABLE_COLUMNS:
            if column == "memo":
                value = self.memo_text.get("1.0", "end").strip()
            else:
                value = self.vars[column].get().strip()

            if column == "event_date" and not value:
                messagebox.showerror("入力エラー", "イベント日が未入力です。", parent=self.window)
                return None

            if value == "":
                record[column] = None
                continue

            if column in integer_columns:
                try:
                    record[column] = int(value)
                except ValueError:
                    messagebox.showerror("入力エラー", f"{EVENT_COLUMN_LABELS[column]} には数字を入力してください。", parent=self.window)
                    return None
            else:
                record[column] = value

        return record

    def save_event(self) -> None:
        record = self._collect_event_data()
        if record is None:
            return

        summary = analysis.make_event_summary(record)
        message = (
            "イベント記録を保存しますか？\n\n"
            f"日付: {record.get('event_date')}\n"
            f"イベント: {record.get('event_type') or ''}\n"
            f"H差分: {summary.get('sys_diff') if summary.get('sys_diff') is not None else 'データ不足'}\n"
            f"確認表示: {summary.get('judgement')}"
        )
        if not messagebox.askyesno("保存確認", message, parent=self.window):
            return

        try:
            db.insert_event_record(record)
        except sqlite3.Error as error:
            messagebox.showerror("保存エラー", f"イベント記録の保存に失敗しました。\n{error}", parent=self.window)
            return

        messagebox.showinfo("保存完了", "イベント記録を保存しました。", parent=self.window)
        self.clear_form()
        self.load_events()

    def load_events(self) -> None:
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        try:
            records = db.fetch_all_event_records()
        except sqlite3.Error as error:
            messagebox.showerror("読み込みエラー", f"イベント記録の読み込みに失敗しました。\n{error}", parent=self.window)
            return

        for record in records:
            summary = analysis.make_event_summary(record)
            values = [summary.get(column) if summary.get(column) is not None else "" for column in EVENT_TREE_COLUMNS]
            self.tree.insert("", "end", values=values)

    def delete_selected_event(self) -> None:
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("削除エラー", "削除対象のイベントを選択してください。", parent=self.window)
            return

        values = self.tree.item(selected_items[0], "values")
        if not values:
            return

        record_id = int(values[0])
        if not messagebox.askyesno("削除確認", "選択したイベント記録を削除しますか？", parent=self.window):
            return

        try:
            db.delete_event_record(record_id)
        except sqlite3.Error as error:
            messagebox.showerror("削除エラー", f"イベント記録の削除に失敗しました。\n{error}", parent=self.window)
            return

        self.load_events()

    def clear_form(self) -> None:
        for column, variable in self.vars.items():
            if column == "event_date":
                variable.set(date.today().isoformat())
            elif column == "event_type":
                variable.set(EVENT_TYPE_VALUES[0])
            elif column == "symptom":
                variable.set("なし")
            else:
                variable.set("")
        self.memo_text.delete("1.0", "end")


class ReturnHomeRecordWindow:
    def __init__(self, parent: tk.Misc) -> None:
        self.window = tk.Toplevel(parent)
        self.window.title("帰宅後データ記録")
        self.window.geometry("1280x760")
        self.vars: dict[str, tk.StringVar] = {}
        self.memo_text: tk.Text
        self.tree: ttk.Treeview

        self._create_widgets()
        self.clear_form()
        self.load_records()

    def _create_widgets(self) -> None:
        notice = ttk.Label(
            self.window,
            text="この記録は医療診断ではありません。帰宅後のしゃがみ込み・立ち上がり前後差を、医師に相談するための補助記録として保存します。",
            foreground="#7a2d00",
            wraplength=1220,
            justify="left",
        )
        notice.pack(fill="x", padx=10, pady=(10, 6))

        form_frame = ttk.LabelFrame(self.window, text="帰宅後データ入力")
        form_frame.pack(fill="x", padx=10, pady=6)

        fields = [
            ("record_date", "日付", "entry"),
            ("weekday", "曜日", "readonly"),
            ("activity", "活動内容", "combo_activity"),
            ("return_time", "帰宅時間", "entry"),
            ("return_sys", "帰宅時 H", "entry"),
            ("return_dia", "帰宅時 L", "entry"),
            ("return_pulse", "帰宅時 hr", "entry"),
            ("squat_sys", "しゃがみ込み H", "entry"),
            ("squat_dia", "しゃがみ込み L", "entry"),
            ("squat_pulse", "しゃがみ込み hr", "entry"),
            ("stand_now_sys", "立ち上がり直後 H", "entry"),
            ("stand_now_dia", "立ち上がり直後 L", "entry"),
            ("stand_now_pulse", "立ち上がり直後 hr", "entry"),
            ("stand_1min_sys", "立ち上がり1分 H", "entry"),
            ("stand_1min_dia", "立ち上がり1分 L", "entry"),
            ("stand_1min_pulse", "立ち上がり1分 hr", "entry"),
            ("stand_3min_sys", "立ち上がり3分 H", "entry"),
            ("stand_3min_dia", "立ち上がり3分 L", "entry"),
            ("stand_3min_pulse", "立ち上がり3分 hr", "entry"),
            ("bedtime_sys", "就寝時 H", "entry"),
            ("bedtime_dia", "就寝時 L", "entry"),
            ("bedtime_pulse", "就寝時 hr", "entry"),
            ("arrival_time", "到着時", "entry"),
            ("before_lunch_sys", "昼食前 H", "entry"),
            ("before_lunch_dia", "昼食前 L", "entry"),
            ("before_lunch_pulse", "昼食前 hr", "entry"),
            ("meal_content", "食事内容", "entry"),
            ("after_lunch_sys", "昼食後 H", "entry"),
            ("after_lunch_dia", "昼食後 L", "entry"),
            ("after_lunch_pulse", "昼食後 hr", "entry"),
        ]

        for index, (column, label_text, widget_type) in enumerate(fields):
            row = index // 4
            grid_column = (index % 4) * 2
            ttk.Label(form_frame, text=label_text).grid(row=row, column=grid_column, sticky="w", padx=6, pady=4)
            variable = tk.StringVar()
            self.vars[column] = variable

            if widget_type == "combo_activity":
                widget = ttk.Combobox(
                    form_frame,
                    textvariable=variable,
                    values=RETURN_HOME_ACTIVITY_VALUES,
                    state="readonly",
                    width=18,
                )
            else:
                state = "readonly" if widget_type == "readonly" else "normal"
                widget = ttk.Entry(form_frame, textvariable=variable, width=20, state=state)

            widget.grid(row=row, column=grid_column + 1, sticky="ew", padx=6, pady=4)
            if column == "record_date":
                widget.bind("<Button-1>", self.choose_record_date)
                widget.bind("<FocusOut>", self.update_weekday_from_date)

        memo_row = (len(fields) + 3) // 4
        ttk.Label(form_frame, text="メモ").grid(row=memo_row, column=0, sticky="nw", padx=6, pady=4)
        self.memo_text = tk.Text(form_frame, height=3, width=80)
        self.memo_text.grid(row=memo_row, column=1, columnspan=7, sticky="ew", padx=6, pady=4)

        for column in range(8):
            form_frame.columnconfigure(column, weight=1)

        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", padx=10, pady=6)
        ttk.Button(button_frame, text="帰宅後データ保存", command=self.save_record).pack(side="left", padx=4)
        ttk.Button(button_frame, text="選択データ削除", command=self.delete_selected_record).pack(side="left", padx=4)
        ttk.Button(button_frame, text="再読み込み", command=self.load_records).pack(side="left", padx=4)
        ttk.Button(button_frame, text="入力クリア", command=self.clear_form).pack(side="left", padx=4)

        tree_frame = ttk.LabelFrame(self.window, text="帰宅後データ一覧")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tree = ttk.Treeview(tree_frame, columns=RETURN_HOME_TREE_COLUMNS, show="headings", height=12)
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        for column in RETURN_HOME_TREE_COLUMNS:
            self.tree.heading(column, text=RETURN_HOME_COLUMN_LABELS[column])
            width = 95
            if column in {"activity", "judgement"}:
                width = 150
            elif column == "memo":
                width = 220
            elif column.startswith("diff_"):
                width = 145
            self.tree.column(column, width=width, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

    def choose_record_date(self, event: tk.Event | None = None) -> str:
        current_value = self.vars["record_date"].get().strip()
        try:
            initial_date = date.fromisoformat(current_value) if current_value else date.today()
        except ValueError:
            initial_date = date.today()

        selected_date = ask_date(self.window, title="帰宅後データの日付を選択", initial_date=initial_date)
        if selected_date:
            self.vars["record_date"].set(selected_date)
            self.update_weekday_from_date()
        return "break"

    def update_weekday_from_date(self, event: tk.Event | None = None) -> None:
        date_text = self.vars["record_date"].get().strip()
        self.vars["weekday"].set(self._weekday_text(date_text))

    def _weekday_text(self, date_text: str) -> str:
        try:
            weekday_index = date.fromisoformat(date_text).weekday()
        except ValueError:
            return ""
        return ["月", "火", "水", "木", "金", "土", "日"][weekday_index]

    def _collect_record_data(self) -> dict[str, Any] | None:
        record: dict[str, Any] = {}
        integer_columns = {
            "return_sys",
            "return_dia",
            "return_pulse",
            "squat_sys",
            "squat_dia",
            "squat_pulse",
            "stand_now_sys",
            "stand_now_dia",
            "stand_now_pulse",
            "stand_1min_sys",
            "stand_1min_dia",
            "stand_1min_pulse",
            "stand_3min_sys",
            "stand_3min_dia",
            "stand_3min_pulse",
            "bedtime_sys",
            "bedtime_dia",
            "bedtime_pulse",
            "before_lunch_sys",
            "before_lunch_dia",
            "before_lunch_pulse",
            "after_lunch_sys",
            "after_lunch_dia",
            "after_lunch_pulse",
        }

        self.update_weekday_from_date()
        for column in RETURN_HOME_EDITABLE_COLUMNS:
            if column == "memo":
                value = self.memo_text.get("1.0", "end").strip()
            else:
                value = self.vars[column].get().strip()

            if column == "record_date" and not value:
                messagebox.showerror("入力エラー", "日付が未入力です。", parent=self.window)
                return None

            if value == "":
                record[column] = None
                continue

            if column in integer_columns:
                try:
                    record[column] = int(value)
                except ValueError:
                    messagebox.showerror("入力エラー", f"{RETURN_HOME_COLUMN_LABELS[column]} には数字を入力してください。", parent=self.window)
                    return None
            else:
                record[column] = value

        return record

    def save_record(self) -> None:
        record = self._collect_record_data()
        if record is None:
            return

        summary = analysis.make_return_home_summary(record)
        message = (
            "帰宅後データを保存しますか？\n\n"
            f"日付: {record.get('record_date')}（{record.get('weekday') or ''}）\n"
            f"活動内容: {record.get('activity') or ''}\n"
            f"帰宅時H - しゃがみ込みH: {self._value_or_data_shortage(summary.get('diff_return_squat'))}\n"
            f"しゃがみ込みH - 立ち上がり直後H: {self._value_or_data_shortage(summary.get('diff_squat_stand_now'))}\n"
            f"しゃがみ込みH - 立ち上がり1分H: {self._value_or_data_shortage(summary.get('diff_squat_stand_1min'))}\n"
            f"しゃがみ込みH - 立ち上がり3分H: {self._value_or_data_shortage(summary.get('diff_squat_stand_3min'))}\n"
            f"確認表示: {summary.get('judgement')}"
        )
        if not messagebox.askyesno("保存確認", message, parent=self.window):
            return

        try:
            db.insert_return_home_record(record)
        except sqlite3.Error as error:
            messagebox.showerror("保存エラー", f"帰宅後データの保存に失敗しました。\n{error}", parent=self.window)
            return

        messagebox.showinfo("保存完了", "帰宅後データを保存しました。", parent=self.window)
        self.clear_form()
        self.load_records()

    def _value_or_data_shortage(self, value: Any) -> str:
        if value is None:
            return "データ不足"
        return f"{value} mmHg"

    def load_records(self) -> None:
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        try:
            records = db.fetch_all_return_home_records()
        except sqlite3.Error as error:
            messagebox.showerror("読み込みエラー", f"帰宅後データの読み込みに失敗しました。\n{error}", parent=self.window)
            return

        for record in records:
            summary = analysis.make_return_home_summary(record)
            values = [summary.get(column) if summary.get(column) is not None else "" for column in RETURN_HOME_TREE_COLUMNS]
            self.tree.insert("", "end", values=values)

    def delete_selected_record(self) -> None:
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("削除エラー", "削除対象の帰宅後データを選択してください。", parent=self.window)
            return

        values = self.tree.item(selected_items[0], "values")
        if not values:
            return

        record_id = int(values[0])
        if not messagebox.askyesno("削除確認", "選択した帰宅後データを削除しますか？", parent=self.window):
            return

        try:
            db.delete_return_home_record(record_id)
        except sqlite3.Error as error:
            messagebox.showerror("削除エラー", f"帰宅後データの削除に失敗しました。\n{error}", parent=self.window)
            return

        self.load_records()

    def clear_form(self) -> None:
        today_text = date.today().isoformat()
        for column, variable in self.vars.items():
            if column == "record_date":
                variable.set(today_text)
            elif column == "weekday":
                variable.set(self._weekday_text(today_text))
            elif column == "activity":
                variable.set(RETURN_HOME_ACTIVITY_VALUES[0])
            else:
                variable.set("")
        self.memo_text.delete("1.0", "end")


if __name__ == "__main__":
    main()
