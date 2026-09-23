# AGENTS.md

## Project Name

bp_tracker_app

## use venv path

このプロジェクトでは、Python の仮想環境を使用してください。  
仮想環境は以下の通りです。

```bash
D:\Dev\venvs\venv_bptrack312\Scripts\python.exe
```

## Purpose

このプロジェクトは、血圧・脈拍・服薬・飲酒・立ちくらみ・体調メモなどを記録し、  
血圧変動のトリガーを探すための Python GUI アプリです。

主な目的は、以下の情報を整理・可視化することです。

- 起床直後の血圧
- 座位での血圧
- 排尿後の血圧
- 立位1分後・3分後の血圧
- コンサータ服用時刻
- ジャディアンス服用有無
- メトグルコ服用回数
- 前夜の飲酒
- 立ちくらみの有無
- 水分量
- 背部痛、耳痛、顔面痛などのメモ
- 体重 ※任意入力。体重計購入後に使う予定

このアプリは医療診断を行うものではありません。  
記録を整理し、医師に相談するための補助ツールです。

---

## Language

コードコメント、README、画面表示、エラーメッセージは、基本的に日本語で記述してください。

---

## Target User

Python初心者でも理解しやすい構成を優先してください。

ユーザーは Windows 11 環境で VS Code を使用します。  
将来的に PyInstaller で exe 化する可能性があります。

---

## Development Policy

### Important

- いきなり大きな構成にしないでください。
- まずは動作する最小構成を優先してください。
- ~~医療判断をアプリ側で断定しないでください。~~
- いきなり医療判断を行わず、「注意」「確認推奨」などの表現に留めてください。
- データは SQLite に保存してください。
- GUI はまず tkinter で作成してください。
- グラフは matplotlib を使用してください。
- 表示・集計には pandas を使用しても構いません。

---

## Recommended Project Structure

```text
bp_tracker_app/
│
├─ main.py
├─ db.py
├─ analysis.py
├─ graph_view.py
├─ export_csv.py
├─ constants.py
│
├─ data/
│   └─ bp_tracker.sqlite3
│
├─ exports/
│   └─ .gitkeep
│
└─ README.md
````

最初は `main.py` にまとめても構いません。
ただし、機能が増えてきたら上記のように分割してください。

---

## Database

SQLite を使用してください。

DB ファイルの保存先は以下です。

```text
data/bp_tracker.sqlite3
```

`data/` フォルダが存在しない場合は、自動作成してください。

---

## Table Design

まずは 1 テーブル構成で構いません。

```sql
CREATE TABLE IF NOT EXISTS bp_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT NOT NULL UNIQUE,

    wake_time TEXT,
    sleep_time TEXT,
    sleep_hours REAL,
    weight REAL,

    wpH INTEGER,
    wpL INTEGER,
    wp_hr INTEGER,

    spH INTEGER,
    spL INTEGER,
    sp_hr INTEGER,

    auH INTEGER,
    auL INTEGER,
    au_hr INTEGER,

    st1H INTEGER,
    st1L INTEGER,
    st1_hr INTEGER,

    st3H INTEGER,
    st3L INTEGER,
    st3_hr INTEGER,

    concerta_time TEXT,
    jardiance TEXT,
    metgluco_count INTEGER,

    dizziness TEXT,
    drinking_prev_night TEXT,
    water_amount TEXT,
    back_pain TEXT,
    ear_face_pain TEXT,

    memo TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## Column Meanings

| Column              | Meaning                |
| ------------------- | ---------------------- |
| record_date         | 記録日                 |
| wake_time           | 起床時刻               |
| sleep_time          | 就寝時刻               |
| sleep_hours         | 睡眠時間               |
| weight              | 体重。任意入力         |
| wpH                 | 起床直後の収縮期血圧   |
| wpL                 | 起床直後の拡張期血圧   |
| wp_hr               | 起床直後の脈拍         |
| spH                 | 座位直後の収縮期血圧   |
| spL                 | 座位直後の拡張期血圧   |
| sp_hr               | 座位直後の脈拍         |
| auH                 | 排尿後座位の収縮期血圧 |
| auL                 | 排尿後座位の拡張期血圧 |
| au_hr               | 排尿後座位の脈拍       |
| st1H                | 立位1分後の収縮期血圧  |
| st1L                | 立位1分後の拡張期血圧  |
| st1_hr              | 立位1分後の脈拍        |
| st3H                | 立位3分後の収縮期血圧  |
| st3L                | 立位3分後の拡張期血圧  |
| st3_hr              | 立位3分後の脈拍        |
| concerta_time       | コンサータ服用時刻     |
| jardiance           | ジャディアンス服用有無 |
| metgluco_count      | メトグルコ服用回数     |
| dizziness           | 立ちくらみ             |
| drinking_prev_night | 前夜飲酒               |
| water_amount        | 水分量                 |
| back_pain           | 背部痛                 |
| ear_face_pain       | 耳痛・顔面痛           |
| memo                | 自由メモ               |

---

## GUI Requirements

tkinter を使用してください。

### Main Window

以下の要素を配置してください。

1. 入力フォーム
2. 保存ボタン
3. 選択行読み込みボタン
4. 更新ボタン
5. 削除ボタン
6. 全期間表示ボタン
7. 期間指定表示ボタン
8. CSV出力ボタン
9. グラフ表示ボタン
10. Hi-Level Sample 抽出ボタン
11. Low-Level Sample 抽出ボタン
12. マークポイント表示ボタン
13. Treeview による一覧表示

---

## Input Form

最初のバージョンでは、以下の入力項目を優先してください。

### Required / Important

- 記録日
- 起床直後 H / L / pulse
- 座位 H / L / pulse
- 排尿後 H / L / pulse
- コンサータ服用時刻
- ジャディアンス服用有無
- 立ちくらみ
- 前夜飲酒
- メモ

### Optional

- 立位1分後 H / L / pulse
- 立位3分後 H / L / pulse
- 体重
- 起床時刻
- 就寝時刻
- 睡眠時間
- 水分量
- 背部痛
- 耳痛・顔面痛
- メトグルコ服用回数

体重は未入力を許可してください。
未入力の場合は `NULL` として保存してください。

---

## Dropdown Values

以下の項目は Combobox を使ってください。

### jardiance

```text
有
無
未入力
```

### dizziness

```text
無
軽い
強い
未入力
```

### drinking_prev_night

```text
無
少量
多い
未入力
```

### water_amount

```text
少ない
普通
多い
未入力
```

### back_pain

```text
無
有
未入力
```

### ear_face_pain

```text
無
有
未入力
```

---

## Analysis Requirements

`analysis.py` に分析用関数を作成してください。

### Mark Points

以下の項目を計算してください。

| 見るポイント             | 計算内容   | 目的                             |
| ------------------------ | ---------- | -------------------------------- |
| 起床直後と排尿後座位の差 | wpH - auH  | 朝の体位変化・自律神経の切り替え |
| 起床直後と座位の差       | wpH - spH  | 起床直後から座位への変動         |
| 座位と立位1分後の差      | spH - st1H | 起立性低血圧っぽいか             |
| 座位と立位3分後の差      | spH - st3H | 起立性低血圧っぽいか             |
| コンサータ時刻との関係   | 今後拡張   | 服薬後に上がる傾向を見る         |
| 前夜飲酒との関係         | 今後拡張   | 翌朝の高低差を見る               |
| 睡眠・水分との関係       | 今後拡張   | 自律神経・脱水傾向を見る         |

### 判定の注意

医学的診断はしないでください。

表示例は以下のようにしてください。

```text
注意候補
確認推奨
通常範囲
データ不足
```

### 起立性低血圧の目安

座位から立位で、

- 収縮期血圧が 20mmHg 以上低下
- または拡張期血圧が 10mmHg 以上低下

した場合は、以下のように表示してください。

```text
起立性低血圧の可能性あり。医師に相談するための記録として保存してください。
```

ただし、診断とは書かないでください。

---

## High Level Sample

Hi-Level Sample 抽出では、以下の条件に該当する記録を抽出してください。

- 収縮期血圧が 140 以上
- または拡張期血圧が 90 以上
- またはメモに「背部痛」「胸痛」「息苦しい」などが含まれる

表示名は以下にしてください。

```text
Hi-Level Sample
```

---

## Low Level Sample

Low-Level Sample 抽出では、以下の条件に該当する記録を抽出してください。

- 収縮期血圧が 100 未満
- または座位から立位1分後で収縮期血圧が 20 以上低下
- または座位から立位3分後で収縮期血圧が 20 以上低下
- または立ちくらみが「強い」

表示名は以下にしてください。

```text
Low-Level Sample
```

---

## Graph Requirements

matplotlib を使用してください。

最初に作るグラフは以下です。

### 1. 朝の収縮期血圧グラフ

- 起床直後 H
- 座位 H
- 排尿後 H

### 2. 朝の拡張期血圧グラフ

- 起床直後 L
- 座位 L
- 排尿後 L

### 3. 脈拍グラフ

- 起床直後 pulse
- 座位 pulse
- 排尿後 pulse

### 4. 血圧差グラフ

- 起床直後 H - 排尿後 H
- 座位 H - 立位1分 H
- 座位 H - 立位3分 H

グラフタイトル、軸ラベルは日本語で表示してください。

---

## Export Requirements

CSV 出力機能を作成してください。

保存先は `exports/` フォルダです。
フォルダが存在しない場合は自動作成してください。

ファイル名例：

```text
bp_records_20260921.csv
```

期間指定がある場合：

```text
bp_records_20260901_20260921.csv
```

---

## Error Handling

以下の場合は、日本語のメッセージを表示してください。

- 日付が未入力
- 数値欄に数字以外が入力された
- DB保存に失敗した
- 更新対象が選択されていない
- 削除対象が選択されていない
- グラフ表示対象データが存在しない

---

## Coding Style

- 初心者が読めるように、関数名は分かりやすくしてください。
- 複雑な省略記法を避けてください。
- 重要な処理には日本語コメントを入れてください。
- 1つの関数が長くなりすぎないようにしてください。
- 可能なら type hints を付けてください。
- 例外処理を入れてください。

---

## Do Not

以下は禁止です。

- 医療診断を断定すること
- 「高血圧です」「起立性低血圧です」と確定表示すること
- ネットワーク通信を必須にすること
- Google Sheets API を最初から必須にすること
- 体重入力を必須にすること
- 保存済みデータを確認なしで削除すること
- 韓国語表示を入れること

---

## Version Plan

### Ver.0.1

- SQLite DB 作成
- GUI 入力フォーム
- 保存
- 一覧表示
- 選択行読み込み
- 更新
- 削除
- CSV出力

### Ver.0.2

- 期間指定表示
- グラフ表示

### Ver.0.3

- Hi-Level Sample 抽出
- Low-Level Sample 抽出
- マークポイント表示

### Ver.0.4

- 診察用レポート出力
- PDF出力またはHTML出力
- Googleスプレッドシート形式に近いCSV出力

---

## Medical Disclaimer Text for App

アプリ内のどこかに、以下の注意文を表示してください。

```text
このアプリは医療診断を行うものではありません。
血圧・脈拍・服薬・症状を記録し、医師に相談するための補助ツールです。
強い胸痛、背部痛、息苦しさ、冷や汗、意識が遠のく感じなどがある場合は、記録よりも受診を優先してください。
```

---

## First Task for Codex

まずは Ver.0.1 を作成してください。

### Ver.0.1 Requirements

- `main.py`
- `db.py`
- `analysis.py`
- SQLite DB 自動作成
- tkinter GUI
- 1日分の記録入力
- 保存
- 一覧表示
- 選択行読み込み
- 更新
- 削除
- CSV出力
- 体重は任意入力
- 日本語UI

グラフ機能、Hi-Level/Low-Level 抽出、マークポイント表示は Ver.0.2 以降で構いません。

---

## Future Expansion Plan

このセクションは、Ver.0.4 以降に追加したい機能をまとめたものです。  
Codex は、まず Ver.0.1〜Ver.0.3 の安定動作を優先してください。  
以下の機能は、既存機能が安定してから段階的に追加してください。

---

## Ver.0.5

### 記録項目の拡張

以下の項目を追加できるようにしてください。

- 食事メモ
- 塩分メモ
- カフェイン摂取
- 運動・自転車移動
- 外出の有無
- 入浴の有無
- 睡眠の質
- ストレス度
- PC作業時間
- 首・肩・顎の張り
- 食いしばり自覚
- 頭痛
- 背部痛の詳細
- めまい・ふらつきの詳細

### 目的

血圧変動のトリガー候補を、薬・飲酒・水分だけでなく、  
生活行動や体調変化からも探せるようにする。

### 注意

入力項目を増やしすぎると記録が続かなくなるため、  
すべて必須にはしないでください。  
基本は任意入力としてください。

---

## Ver.0.6

### トリガー分析機能

以下のような条件別集計を追加してください。

- 前夜飲酒あり / なし の朝血圧平均比較
- ジャディアンス服用あり / なし の血圧比較
- コンサータ服用時刻別の血圧比較
- 水分量別の血圧比較
- 睡眠時間別の血圧比較
- 立ちくらみあり / なし の血圧比較
- 背部痛あり / なし の血圧比較

### 表示例

```text
前夜飲酒ありの日：平均 135 / 88
前夜飲酒なしの日：平均 122 / 80

差分：収縮期 +13
判定：確認推奨
```

---

## Future Expansion Plan

このセクションは、Ver.0.4 以降に追加したい機能をまとめたものです。  
Codex は、まず Ver.0.1〜Ver.0.3 の安定動作を優先してください。  
以下の機能は、既存機能が安定してから段階的に追加してください。

---

## Ver.0.5

### 記録項目の拡張

以下の項目を追加できるようにしてください。

- 食事メモ
- 塩分メモ
- カフェイン摂取
- 運動・自転車移動
- 外出の有無
- 入浴の有無
- 睡眠の質
- ストレス度
- PC作業時間
- 首・肩・顎の張り
- 食いしばり自覚
- 頭痛
- 背部痛の詳細
- めまい・ふらつきの詳細

### 目的

血圧変動のトリガー候補を、薬・飲酒・水分だけでなく、  
生活行動や体調変化からも探せるようにする。

### 注意

入力項目を増やしすぎると記録が続かなくなるため、  
すべて必須にはしないでください。  
基本は任意入力としてください。

---

## Ver.0.6

### トリガー分析機能

以下のような条件別集計を追加してください。

- 前夜飲酒あり / なし の朝血圧平均比較
- ジャディアンス服用あり / なし の血圧比較
- コンサータ服用時刻別の血圧比較
- 水分量別の血圧比較
- 睡眠時間別の血圧比較
- 立ちくらみあり / なし の血圧比較
- 背部痛あり / なし の血圧比較

### 表示例

```text
前夜飲酒ありの日：平均 135 / 88
前夜飲酒なしの日：平均 122 / 80

差分：収縮期 +13
判定：確認推奨
```
---

