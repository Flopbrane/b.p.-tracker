# -*- coding: utf-8 -*-
from __future__ import annotations

import calendar
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk


class MiniCalendarDialog(tk.Toplevel):
    """血圧記録アプリで使う小さな日付選択ダイアログです。"""

    def __init__(
        self,
        parent: tk.Misc | None = None,
        title: str = "日付選択",
        initial_date: date | None = None,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.selected_date: str | None = None

        today = initial_date or date.today()
        self.year_var = tk.StringVar(value=str(today.year))
        self.month_var = tk.StringVar(value=str(today.month))

        self._create_widgets()
        self.show_calendar()

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def _create_widgets(self) -> None:
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, padx=10, pady=10)

        year_entry = ttk.Entry(top_frame, textvariable=self.year_var, width=6)
        year_entry.pack(side=tk.LEFT)
        ttk.Label(top_frame, text="年").pack(side=tk.LEFT, padx=(2, 8))

        month_list = [str(month) for month in range(1, 13)]
        month_box = ttk.Combobox(
            top_frame,
            textvariable=self.month_var,
            values=month_list,
            width=4,
            state="readonly",
        )
        month_box.pack(side=tk.LEFT)
        ttk.Label(top_frame, text="月").pack(side=tk.LEFT, padx=(2, 8))

        ttk.Button(top_frame, text="表示", command=self.show_calendar).pack(side=tk.LEFT)

        self.cal_frame = ttk.Frame(self)
        self.cal_frame.pack(padx=10, pady=(0, 10))

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(bottom_frame, text="キャンセル", command=self.cancel).pack(side=tk.RIGHT)

    def show_calendar(self) -> None:
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            if month < 1 or month > 12:
                raise ValueError
        except ValueError:
            messagebox.showerror("入力エラー", "年と月を正しく入力してください。", parent=self)
            return

        for widget in self.cal_frame.winfo_children():
            widget.destroy()

        days_of_week = ["日", "月", "火", "水", "木", "金", "土"]
        for column, day_name in enumerate(days_of_week):
            ttk.Label(self.cal_frame, text=day_name, anchor="center", width=5).grid(
                row=0,
                column=column,
                padx=1,
                pady=1,
            )

        calendar.setfirstweekday(calendar.SUNDAY)
        month_weeks = calendar.monthcalendar(year, month)

        for row_index, week in enumerate(month_weeks, start=1):
            for column_index, day in enumerate(week):
                if day == 0:
                    ttk.Label(self.cal_frame, text="", width=5).grid(
                        row=row_index,
                        column=column_index,
                        padx=1,
                        pady=1,
                    )
                    continue

                button = ttk.Button(
                    self.cal_frame,
                    text=str(day),
                    width=5,
                    command=lambda selected_day=day: self.select_day(selected_day),
                )
                button.grid(row=row_index, column=column_index, padx=1, pady=1)

    def select_day(self, day: int) -> None:
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        self.selected_date = f"{year:04d}-{month:02d}-{day:02d}"
        self.destroy()

    def cancel(self) -> None:
        self.selected_date = None
        self.destroy()


def ask_date(
    parent: tk.Misc | None = None,
    title: str = "日付選択",
    initial_date: date | None = None,
) -> str | None:
    dialog = MiniCalendarDialog(parent=parent, title=title, initial_date=initial_date)
    dialog.wait_window()
    return dialog.selected_date


def main() -> None:
    root = tk.Tk()
    root.withdraw()
    selected_date = ask_date(root, "Mini Calendar")
    if selected_date:
        print(f"Selected date is: {selected_date}")
    root.destroy()


if __name__ == "__main__":
    main()
