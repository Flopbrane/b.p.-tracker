from __future__ import annotations

import sqlite3
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk
from typing import Any

import analysis
import db
from constants import (
    APP_TITLE,
    COLUMN_LABELS,
    DIZZINESS_VALUES,
    DRINKING_VALUES,
    EDITABLE_COLUMNS,
    JARDIANCE_VALUES,
    MEDICAL_DISCLAIMER,
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

REAL_FIELDS = {"sleep_hours", "weight"}
REQUIRED_FIELDS = {"record_date"}
COMBO_FIELDS = {
    "jardiance",
    "dizziness",
    "drinking_prev_night",
    "water_amount",
    "back_pain",
    "ear_face_pain",
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

        memo_row = (len(fields) + 3) // 4
        ttk.Label(parent, text="メモ").grid(row=memo_row, column=0, sticky="nw", padx=6, pady=4)
        self.memo_text = tk.Text(parent, height=4, width=80)
        self.memo_text.grid(row=memo_row, column=1, columnspan=7, sticky="ew", padx=6, pady=4)

        for column_index in range(8):
            parent.columnconfigure(column_index, weight=1)

    def _combo_values(self, widget_type: str) -> list[str]:
        if widget_type == "combo_jardiance":
            return JARDIANCE_VALUES
        if widget_type == "combo_dizziness":
            return DIZZINESS_VALUES
        if widget_type == "combo_drinking":
            return DRINKING_VALUES
        if widget_type == "combo_water":
            return WATER_VALUES
        return YES_NO_VALUES

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
            ("診察用レポート出力", self.export_report),
        ]

        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command).pack(side="left", padx=4)

        ttk.Label(button_frame, textvariable=self.status_var).pack(side="left", padx=12)

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


if __name__ == "__main__":
    main()
