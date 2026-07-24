# SETUP — 手元での動作確認手順

本リポジトリは [CI Pipeline](.github/workflows/ci.yml) で **毎 push / PR に 単体（pytest・53件）／API（runn・10 runbook）／E2E（Playwright・4シナリオ）の3ジョブを並列自動実行** しています（README 上部のバッジを参照）。手元で動かして確かめたい場合の手順を以下にまとめます。

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

## 3.5 単体テストの実行（最速・サーバ不要）

セットアップの確認を兼ねて、まず単体テストを実行できます。サーバー起動もブラウザも不要です。

```bash
cd app
python -m pytest
# 53 passed（ローカル実測 約0.2〜0.3秒）
```

対象は `app/tickets/tests/`（認可述語・状態遷移の純ロジック）。設定は `app/pytest.ini`、テスト用 DB は pytest-django が自動生成・自動破棄します（開発用 `db.sqlite3` には触れません）。

## 4. アプリ起動とE2Eテスト実行（2ターミナル）

2 つのターミナルを開き、両方で仮想環境を有効化して以下を実行します。

| 手順 | **ターミナル1（サーバー起動）** | **ターミナル2（テスト実行）** |
|---|---|---|
| 1. ルートへ移動 | `cd qa-portfolio-ticket-system` | `cd qa-portfolio-ticket-system` |
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
# macOS / Linux
BASE_URL=http://localhost:9000 python -m pytest

# Windows (PowerShell)
$env:BASE_URL = "http://localhost:9000"; python -m pytest
```

> `BASE_URL` 環境変数で切替可能。既定は `http://127.0.0.1:8000`。

## 5.5 API テスト（runn）の実行

API/インテグレーション層は [runn](https://github.com/k1LoW/runn) で実行します。**再現性のため runn は v1.9.2 に固定**（CI と一致）。

```bash
# 1) runn を取得（バージョン固定）
#   Linux:   runn_v1.9.2_linux_amd64.tar.gz
#   macOS:   runn_v1.9.2_darwin_amd64.tar.gz
#   Windows: runn_v1.9.2_windows_amd64.tar.gz（展開物は runn.exe）
curl -sL https://github.com/k1LoW/runn/releases/download/v1.9.2/runn_v1.9.2_linux_amd64.tar.gz | tar xz runn

# 2) アプリ＋DB を起動（§3-§4 と同じ。別ターミナルで）
cd app && python manage.py migrate && python manage.py seed_demo && python manage.py runserver 127.0.0.1:8000

# 3) プロジェクトルートから runbook を実行
./runn run "qa/api/runn/**/*.yml" --verbose
```

- 各 runbook は自前でトークン取得＋データ生成するため、`seed_demo` の既知ユーザーのみに依存します（実行順・既存データに非依存）。
- 接続先は各 runbook の `runners.req`（`http://127.0.0.1:8000`、CI と一致）。
- 構成・期待値の詳細は [qa/api/README](qa/api/README.md)、層の判断は [80 テスト層戦略](qa/docs/80_test_layer_strategy.md)。

### 単一ソースの確認（IDOR 失敗実演）

`app/config/settings.py` の `INTENTIONAL_BUG_IDOR=True` にして再起動すると、単体の IDOR テスト・runn の `rbac_idor/idor.yml`・E2E の Auto-02 が **同一原因で同時に失敗** します（3層が同じ `policy.can_view` を共有しているため）。確認後は必ず `False` に戻してください。

## 6. アクセス先（手動確認）

サーバー起動後、ブラウザで以下にアクセスできます：

- ログイン画面：`http://127.0.0.1:8000/accounts/login/`
- チケット一覧：`http://127.0.0.1:8000/`

## 7. CI との関係

- 本セットアップは **手元での確認用** です。
- 通常は GitHub Actions が `push` / `pull_request` 時に同等のセットアップを自動実行します（[ci.yml](.github/workflows/ci.yml) 参照）。
- CI 結果（単体 53件＋runn 10 runbook＋E2E 4シナリオの Pass／スクショ・runn 出力の証跡）は Actions タブの Artifacts から取得できます（単体の結果はジョブログで確認）。
