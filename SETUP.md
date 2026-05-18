# SETUP — 手元での動作確認手順

本リポジトリは [CI Pipeline](.github/workflows/ci.yml) で **PR 作成時に4シナリオすべてを自動実行** しています（README 上部のバッジを参照）。手元で動かして確かめたい場合の手順を以下にまとめます。

## 0. 前提

- Python 3.12（CI と揃える推奨）
- Git
- OS：Windows / macOS / Linux のいずれか
- ブラウザ：Playwright が Chromium を自動取得します

## 1. クローンと仮想環境

```bash
git clone https://github.com/nani9ashi/qa-portfolio-ticket-system.git
cd qa-portfolio-ticket-system
python -m venv .venv
```

仮想環境の有効化（OS別）：

| OS | コマンド |
|---|---|
| Windows (PowerShell) | `.\.venv\Scripts\Activate.ps1` |
| macOS / Linux | `source .venv/bin/activate` |

> 以降の `pip install` や `playwright install` は、**仮想環境を有効化した状態** で実行してください。

## 2. 依存関係のインストール

```bash
pip install -r requirements.txt
playwright install chromium
```

> CI（Linux）では追加で `fonts-noto-cjk` を入れています。手元の OS で日本語スクショが豆腐化する場合は、お使いの OS のCJKフォントを別途インストールしてください（Windows/macOS は通常デフォルトで入っています）。

## 3. DB 初期化とデモデータ投入

```bash
cd app
python manage.py migrate
python manage.py seed_demo
```

本書は **`seed_demo` によるデモユーザー（共通パスワード：`pass1234`）の正本** です。app/README §4 はここを参照します。

| ロール | ユーザー名 |
|---|---|
| Requester | `requester1`, `requester2` |
| Agent | `agent1`, `agent2` |
| Admin | `admin1` |

## 4. アプリ起動とテスト実行（2ターミナル）

2 つのターミナルを開き、両方で仮想環境を有効化して以下を実行します。

| 手順 | **ターミナル1（サーバー起動）** | **ターミナル2（テスト実行）** |
|---|---|---|
| 1. ルートへ移動 | `cd ticket-management-system` | `cd ticket-management-system` |
| 2. 仮想環境を有効化 | OS別コマンド（§1 参照） | OS別コマンド（§1 参照） |
| 3. 実行 | `cd app`<br>`python manage.py runserver` | `cd qa/automation`<br>`python -m pytest --headed` |

> ターミナル2 は、ターミナル1 で `Starting development server at http://127.0.0.1:8000/` が表示されてから起動してください。

## 5. テスト実行オプション

```bash
# qa/automation ディレクトリで実行（pytest.ini が tests/ を自動探索）
cd qa/automation

# 全シナリオ（headlessモード、CIと同じ）
python -m pytest

# ブラウザ表示あり
python -m pytest --headed

# スローモーション（操作が見やすい）
python -m pytest --headed --slowmo 500

# 個別シナリオ（例：IDOR回帰のみ）
python -m pytest tests/test_scenario_02_idor.py --headed
```

接続先を変えたい場合：

```bash
BASE_URL=http://localhost:9000 python -m pytest
```

> `BASE_URL` 環境変数で切替可能。既定は `http://127.0.0.1:8000`。

## 6. アクセス先（手動確認）

サーバー起動後、ブラウザで以下にアクセスできます：

- ログイン画面：`http://127.0.0.1:8000/accounts/login/`
- チケット一覧：`http://127.0.0.1:8000/`

## 7. CI との関係

- 本セットアップは **手元での確認用** です。
- 通常は GitHub Actions が `push` / `pull_request` 時に同等のセットアップを自動実行します（[ci.yml](.github/workflows/ci.yml) 参照）。
- CI 結果（4シナリオ Pass / スクショ証跡）は Actions タブの Artifacts から取得できます。
