# QAポートフォリオ：チケット管理アプリ

[チケット管理アプリ](../app/README.md) を対象とした、品質保証（QA）の統合成果物です。  
本ディレクトリ（`qa/`）には、**テスト計画・設計・実行・欠陥管理**、および **API（runn）／E2E（Playwright）自動化** の全工程を集約しています（単体テスト層は SUT 側 [app/tickets/tests/](../app/tickets/tests/) に配置）。

## QA資材の構成

```text
qa/
├── docs/                # テストドキュメント (JSTQB準拠：10計画→…→80テスト層戦略→90自動テスト実施結果。deliverables/ に Word/Excel 実務形式版)
├── api/                 # API/インテグレーションテスト (runn、10 runbook / 102 step)
├── automation/          # E2E自動化 (Playwright/pytest、4シナリオ)
├── requirements/        # 要求仕様 (CSV形式)
├── testcases/           # テストケース定義 (CSV)
├── results/             # テスト実行結果 (CSV、1実行=1行で追記)
├── defects/             # 欠陥管理 (ログCSV + 詳細レポート)
└── evidence/            # 実行証跡 (スクショ・動画・ログ)
```

## 主要ドキュメント・リンク

### テスト計画〜完了レポート
- [10 テスト計画書](./docs/10_test_plan.md)
- [20 テスト条件](./docs/20_test_conditions.md)
- [30 テスト設計](./docs/30_test_design.md)
- [40 テスト環境定義](./docs/40_test_environment.md)
- [50 テスト実行方針](./docs/50_test_execution_policy.md)
- [60 テスト完了レポート](./docs/60_test_completion_report.md)
- [70 要件とテストのトレーサビリティ](./docs/70_requirements_test_traceability.md)
- [80 テスト層戦略（テストピラミッド最適化）](./docs/80_test_layer_strategy.md)
- [90 自動テスト実施レポート](./docs/90_automated_test_report.md)
- [API テスト層 README（runn）](./api/README.md)
- 実運用ドキュメント（Word/Excel 形式の見本）：[テスト設計書.docx](./docs/deliverables/テスト設計書.docx)／[テストケース一覧.xlsx](./docs/deliverables/テストケース一覧.xlsx)／[デシジョンテーブル.xlsx](./docs/deliverables/デシジョンテーブル.xlsx)

### CSV・証跡
- [要求仕様](./requirements/requirements.csv)
- [テストケース](./testcases/testcases.csv) ※設計情報のみ、実行列は持たない
- [テスト結果](./results/test_results.csv) ※1実行=1行で追記
- [欠陥ログ](./defects/defect_log.csv) ※1欠陥=1行
- [スクリーンショット証跡](./evidence/screenshots/)
- [自動化ログ](./automation/evidence/auto/)

### 欠陥レポート
- [DEFECT-001（IDOR：依頼者が他人チケット詳細を閲覧できた）](./defects/reports/DEFECT-001.md)
- [DEFECT-002（body max_length 未実装／自動化Auto-03 が検出）](./defects/reports/DEFECT-002.md)
- [DEFECT-003（期限の過去日で500／runn API 層の期待値設計が検出）](./defects/reports/DEFECT-003.md)

### プロジェクトトップ
- [root README](../README.md)

## このディレクトリの読み方

1. [要求仕様](./requirements/requirements.csv) でテストベースを確認
2. [10 テスト計画書](./docs/10_test_plan.md) で方針・スコープ・リスクを把握
3. [20 テスト条件](./docs/20_test_conditions.md) と [テストケース](./testcases/testcases.csv) でケース展開を確認
4. [テスト結果](./results/test_results.csv) と [欠陥ログ](./defects/defect_log.csv) で実行結果と欠陥管理を確認
5. [60 テスト完了レポート](./docs/60_test_completion_report.md) で残存リスク・教訓・次アクションを確認

## テスト自動化（Test Automation）

自動テストは **3層**（単体／API／E2E）で運用しています。数字や配分の根拠は繰り返さず、[80 テスト層戦略](./docs/80_test_layer_strategy.md)（配分の根拠）と [90 自動テスト実施結果レポート](./docs/90_automated_test_report.md)（実施結果）を正本とします。

### 単体層（pytest）
`policy.py` の認可述語・状態遷移の純ロジックを検証します。テストコードは SUT 側 [app/tickets/tests/](../app/tickets/tests/)、実行は `cd app && python -m pytest`（[SETUP §3.5](../SETUP.md)）。

### API/インテグレーション層（runn）
認可（RBAC/IDOR）・状態遷移・入力検証の **組合せ網羅** を高速・決定的に検証します。実行手順・runbook 構成は [qa/api/README](./api/README.md)。

### E2E 層（Playwright・代表シナリオ）
- **Auto-01**：Requester による作成→確認のハッピーパス（TC-032 & TC-001）
- **Auto-02**：IDOR回帰スモーク（TC-002 / DEFECT-001 由来、`INTENTIONAL_BUG_IDOR` 切替で単体/API/E2E の3層同時失敗を実演可）
- **Auto-04**：非担当 Agent のステータス変更UI抑止（TC-007 のUI側面。サーバ側認可は runn へ移設）
- **Auto-05**：期限の過去日で 500 にならず graceful 拒否（DEFECT-003 回帰）
- ※旧 Auto-03（本文境界）は runn `validation/` へ移設し削除。

実装上の工夫・検出効果（DEFECT-002/003 を自動化が検出した事例を含む）は [自動テスト実施結果レポート（90）](./docs/90_automated_test_report.md) を参照。

### 技術スタック
- **API Test**: runn (k1LoW) ※v1.9.2 固定 ／ 薄い JSON API は Django REST Framework（Token 認証）
- **E2E Framework**: Playwright (Python) ／ **Runner**: pytest（共通 fixture は `automation/conftest.py` に集約）
- **CI**: GitHub Actions（単体／API／E2E の3ジョブを毎 push 並列実行）

## 自動テストの実行方法

セットアップ手順とテスト実行コマンド（個別シナリオ実行・`--headed`・`BASE_URL` 切替など）は **[../SETUP.md](../SETUP.md)** に集約しています。
