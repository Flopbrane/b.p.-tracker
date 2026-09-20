# 血圧記録アプリ

血圧・脈拍・服薬・症状メモを SQLite に保存する tkinter アプリです。

このアプリは医療診断を行うものではありません。記録を整理し、医師に相談するための補助ツールです。

## 起動方法

```powershell
& "D:\Dev\venvs\venv_bptrack312\Scripts\python.exe" main.py
```

## Ver.0.4 でできること

- SQLite DB の自動作成
- 1日分の記録入力
- 保存
- 一覧表示
- 選択行読み込み
- 更新
- 削除
- CSV 出力
- 期間指定表示
- グラフ表示
- Hi-Level Sample 抽出
- Low-Level Sample 抽出
- マークポイント表示
- 診察用 HTML レポート出力

## データ保存先

- DB: `data/bp_tracker.sqlite3`
- CSV: `exports/`
- 診察用HTMLレポート: `reports/`

## 注意

画面上の「注意候補」「確認推奨」は診断ではありません。
記録を整理し、医師に相談するための目安として使ってください。
