# テスト環境定義 - チケット管理アプリ

- 文書ID：TE-TICKET-001
- 版：v1.4
- ステータス：Approved
- 最終更新日：2026-07-23
- 作成者：仁後慎太郎
- 対象：チケット管理アプリ（Web, Django + SQLite）
- 関連：
  - [テスト計画書](10_test_plan.md)
  - [テスト結果](../results/test_results.csv)
  - [テスト実行方針](50_test_execution_policy.md)

## 1. 目的

本書は **テスト環境（手動・自動・CI）とテストデータ（アカウント）の正本** である。10_plan §9 / 30_design §5・§6 / 50_policy §6 は本書を参照する。

## 2. 手動テスト実行環境 (Manual Testing)

- 実行形態：ローカル環境でのサーバー起動
- OS：Windows 10/11
- ブラウザ：
  - Google Chrome（主）
  - Microsoft Edge（副）
- 画面サイズ：PC表示（例：1366×768以上）
- ネットワーク：通常回線（特別な制御は行わない）

## 3. 自動テスト・CI環境 (Automated Testing)

自動テストは3層（単体 / API / E2E）で構成する（層の責務は [80_test_layer_strategy.md](80_test_layer_strategy.md) を参照）。本節は各層の実行環境を定義する。

### 3.1 単体テスト環境（pytest）
- フレームワーク：pytest + pytest-django（バージョン固定：`pytest==9.0.2` / `pytest-django==4.12.0`）
- 対象：`app/tickets/tests/`（`policy.py` の認可述語・状態遷移の純ロジック）
- 設定ファイル：`app/pytest.ini`（`DJANGO_SETTINGS_MODULE=config.settings`）
- 実行形態：`cd app && python -m pytest`。ブラウザ・サーバ起動は不要
- DB：pytest-django がテスト用 SQLite を自動生成・自動破棄する（開発用 `db.sqlite3` には触れない）

### 3.2 E2Eテスト環境（Playwright）
- フレームワーク：Playwright (Python) + pytest（バージョン固定：`pytest==9.0.2` / `pytest-playwright==0.7.2`）
- ブラウザ：Chromium (Headless / Headed モード切替可)
- 実行形態：CLI経由でのテストランナー実行（`cd qa/automation && python -m pytest`）
- 共通fixture：`qa/automation/conftest.py` に `login` / `base_url` / `evidence_dir` を集約。シナリオ追加時のボイラープレートを最小化。
- 接続先切替：`BASE_URL` 環境変数で指定可能（既定：`http://127.0.0.1:8000`）。CI／ローカル／別ポートを1コマンドで切替。
- 設定ファイル：`qa/automation/pytest.ini` で `testpaths=tests` を定義し、自動検索を有効化。

### 3.3 API/インテグレーションテスト環境（runn）
- ツール：runn（バージョン固定：`v1.9.2`。CI ではリリースバイナリを取得して使用）
- 対象：`qa/api/runn/**/*.yml`（10 runbook / 102 step）
- 実行形態：SUT をローカル起動した上で `runn run "qa/api/runn/**/*.yml"`
- 実行結果：`qa/api/runn_result.txt` に保存（生成物のため Git 追跡外）

### 3.4 CIパイプライン環境
- 実行基盤：GitHub Actions
- 実行トリガー：リポジトリへの `push` または Pull Request 作成時
- ジョブ構成：**3ジョブ並列**（Unit Test (pytest) ／ E2E Test (Playwright) ／ API Test (runn)）。実行時間はおおよそ 単体 十数秒・API 1分弱・E2E 1分強で、テストピラミッドの速度勾配が CI 上でも観察できる
- 各ジョブの共通プロセス：
  1. Python および依存関係のセットアップ（正本は ルート `requirements.txt`）
  2. （E2E/API のみ）Django マイグレーション・`seed_demo` 投入・テストサーバー起動
  3. テスト実行（E2E は Headless、API は runn バイナリ v1.9.2 固定）
  4. テスト結果・証跡を Artifacts としてアップロード
- マイグレーションドリフト検知：`makemigrations --check --dry-run` を CI で実行し、未捕捉のモデル変更を失敗として検出する

## 4. テストデータ（アカウント）

本テストで使用するアカウントは架空のものであり、個人情報を含まない。自動テスト・手動テスト共通で使用する。  
※ `seed_demo` によるデモユーザー作成手順は [../../SETUP.md §3](../../SETUP.md#3-db-初期化とデモデータ投入) を正本とし、本表はテスト観点での用途を補足する。

| 区分 | ユーザID | ロール | 用途 | 備考 |
| --- | --- | --- | --- | --- |
| Requester | requester1 | Requester | 自分チケット作成/参照/コメント | パスワードはローカル用の簡易値 |
| Requester | requester2 | Requester | 他人チケット（IDOR/認可検証用） |  |
| Agent | agent1 | Agent | 状態遷移/コメント（担当時） |  |
| Agent | agent2 | Agent | 非担当Agentの認可検証（R4：非担当403） |  |
| Admin | admin1 | Admin | 担当割当/期限設定/全権限 |  |

※ユーザID表記は `requester1` 等で統一する（CSV/証跡/欠陥ログも同様）。
※パスワードやトークン等の機密情報はリポジトリに含めない。
※単体テストはこの共有アカウントを使用せず、テスト内で都度ユーザーを生成する（フィクスチャ）。テスト間の独立性を保つため。

## 5. 証跡（Evidence）の扱い

### 5.1 手動テストの証跡
- 保存先：`../evidence/screenshots/`
- 容量が大きい証跡は、必要に応じて圧縮または別手段で共有し、実行記録の「証跡」列から参照できるようにする。

### 5.2 自動テストの証跡
- E2E 実行時のスクリーンショットは、テスト名ごとに `qa/automation/evidence/auto/<テスト名>/` へ自動保存される（`evidence_dir` fixture）。
- GitHub Actions実行時は、証跡と runn の実行結果を **Artifacts** としてパイプライン上に保存し、Webブラウザからダウンロード・閲覧可能とする。
- 単体テストは証跡を生成しない（アサーション結果そのものが記録であり、CI ログで追跡する）。

## 6. 意図的欠陥（検出・修正の題材）

アプリ側にはテスト用の意図的欠陥スイッチを用意している。  
手動・自動テスト時にON/OFFを切り替える場合は、テスト結果CSVの備考（または専用列）に状態を記録する。

- 例：`IDOR=ON` / `IDOR=OFF`
- ※自動テストにおいて脆弱性検知を実証する場合は、本フラグを有効化してテストをFailさせる手順を踏む（単体・API・E2E の3層が同一原因で同時に失敗することを確認できる）。

## 7. 既知の制約

- 本環境はポートフォリオ用途のため、負荷試験・本番相当構成の再現は対象外とする。
- DBはSQLiteを使用し、自動テスト実行時ごとにデータは初期化（クリーンアップ）される前提とする。
