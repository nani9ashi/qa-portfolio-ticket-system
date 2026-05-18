# テスト環境定義 - チケット管理アプリ

- 文書ID：TE-TICKET-001
- 版：v1.3
- ステータス：Approved
- 最終更新日：2026-05-10
- 作成者：仁後慎太郎
- 対象：チケット管理アプリ（Web, Django + SQLite）
- 関連：
  - [テスト計画書](10_test_plan.md)
  - [テスト結果](../results/test_results.csv)
  - [テスト実行方針](50_test_execution_policy.md)

## 1. 目的

本書は **テスト環境（手動・自動・CI）とテストデータ（アカウント）の正本** である。10_plan §9 / 30_design §6・§7 / 50_policy §6 は本書を参照する。

## 2. 手動テスト実行環境 (Manual Testing)

- 実行形態：ローカル環境でのサーバー起動
- OS：Windows 10/11
- ブラウザ：
  - Google Chrome（主）
  - Microsoft Edge（副）
- 画面サイズ：PC表示（例：1366×768以上）
- ネットワーク：通常回線（特別な制御は行わない）

## 3. 自動テスト・CI環境 (Automated Testing)

PlaywrightおよびGitHub Actionsを用いたE2Eテストの実行環境を定義する。

### 3.1 ローカル自動テスト環境
- フレームワーク：Playwright (Python) + pytest（バージョン固定：`pytest==9.0.2` / `pytest-playwright==0.7.2`）
- ブラウザ：Chromium (Headless / Headed モード切替可)
- 実行形態：CLI経由でのテストランナー実行（`cd qa/automation && python -m pytest`）
- 共通fixture：`qa/automation/conftest.py` に `login` / `base_url` / `evidence_dir` を集約。シナリオ追加時のボイラープレートを最小化。
- 接続先切替：`BASE_URL` 環境変数で指定可能（既定：`http://127.0.0.1:8000`）。CI／ローカル／別ポートを1コマンドで切替。
- 設定ファイル：`qa/automation/pytest.ini` で `testpaths=tests` を定義し、自動検索を有効化。

### 3.2 CIパイプライン環境
- 実行基盤：GitHub Actions (`ubuntu-latest` ランナー)
- 実行トリガー：リポジトリへの `push` または Pull Request 作成時
- 実行プロセス：
  1. Pythonおよび依存関係のセットアップ
  2. Djangoマイグレーションとテストサーバー起動
  3. PlaywrightによるE2Eテスト実行（Headlessモード）
  4. テスト結果・証跡のアップロード

## 4. テストデータ（アカウント）

本テストで使用するアカウントは架空のものであり、個人情報を含まない。自動テスト・手動テスト共通で使用する。  
※ `seed_demo` によるデモユーザー作成手順は [../../SETUP.md §3](../../SETUP.md#3-db-初期化とデモデータ投入) を正本とし、本表はテスト観点での用途を補足する。

| 区分 | ユーザID | ロール | 用途 | 備考 |
| --- | --- | --- | --- | --- |
| Requester | requester1 | Requester | 自分チケット作成/参照/コメント | パスワードはローカル用の簡易値 |
| Requester | requester2 | Requester | 他人チケット（IDOR/認可検証用） |  |
| Agent | agent1 | Agent | 状態遷移/コメント（担当時） |  |
| Admin | admin1 | Admin | 担当割当/期限設定/全権限 |  |

※ユーザID表記は `requester1` 等で統一する（CSV/証跡/欠陥ログも同様）。
※パスワードやトークン等の機密情報はリポジトリに含めない。

## 5. 証跡（Evidence）の扱い

### 5.1 手動テストの証跡
- 保存先：`../evidence/screenshots/`
- 容量が大きい証跡は、必要に応じて圧縮または別手段で共有し、実行記録の「証跡」列から参照できるようにする。

### 5.2 自動テストの証跡
- Playwright実行時に生成されるレポート（HTML形式）や、Fail時のスクリーンショット・トレースファイルは自動で保存される。
- GitHub Actions実行時は、これらのレポートを **Artifacts** としてパイプライン上に保存し、Webブラウザからダウンロード・閲覧可能とする。

## 6. 意図的欠陥（検出・修正の題材）

アプリ側にはテスト用の意図的欠陥スイッチを用意している。  
手動・自動テスト時にON/OFFを切り替える場合は、テスト結果CSVの備考（または専用列）に状態を記録する。

- 例：`IDOR=ON` / `IDOR=OFF`
- ※自動テストにおいて脆弱性検知を実証する場合は、本フラグを有効化してテストをFailさせる手順を踏む。

## 7. 既知の制約

- 本環境はポートフォリオ用途のため、負荷試験・本番相当構成の再現は対象外とする。
- DBはSQLiteを使用し、自動テスト実行時ごとにデータは初期化（クリーンアップ）される前提とする。