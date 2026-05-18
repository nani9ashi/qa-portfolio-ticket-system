# QAポートフォリオ：チケット管理アプリ

[チケット管理アプリ](../app/README.md) を対象とした、品質保証（QA）の統合成果物です。  
本ディレクトリ（`qa/`）には、**テスト計画・設計・実行・欠陥管理**、および **E2E自動化（Playwright/pytest）** の全工程を集約しています。

## QA資材の構成

```text
qa/
├── docs/                # テストドキュメント (JSTQB準拠：10計画→20条件→30設計→40環境→50実行→60完了→70トレーサビリティ)
├── automation/          # テスト自動化 (Playwright/pytest、4シナリオ)
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

### CSV・証跡
- [要求仕様](./requirements/requirements.csv)
- [テストケース](./testcases/testcases.csv) ※設計情報のみ、実行列は持たない
- [テスト結果](./results/test_results.csv) ※1実行=1行で追記
- [欠陥ログ](./defects/defect_log.csv) ※1欠陥=1行
- [スクリーンショット証跡](./evidence/screenshots/)
- [自動化ログ](./evidence/auto/)

### 欠陥レポート
- [DEFECT-001（IDOR：依頼者が他人チケット詳細を閲覧できた）](./defects/reports/DEFECT-001.md)
- [DEFECT-002（body max_length 未実装／自動化Auto-03 が検出）](./defects/reports/DEFECT-002.md)

### プロジェクトトップ
- [root README](../README.md)

## このディレクトリの読み方

1. [要求仕様](./requirements/requirements.csv) でテストベースを確認
2. [10 テスト計画書](./docs/10_test_plan.md) で方針・スコープ・リスクを把握
3. [20 テスト条件](./docs/20_test_conditions.md) と [テストケース](./testcases/testcases.csv) でケース展開を確認
4. [テスト結果](./results/test_results.csv) と [欠陥ログ](./defects/defect_log.csv) で実行結果と欠陥管理を確認
5. [60 テスト完了レポート](./docs/60_test_completion_report.md) で残存リスク・教訓・次アクションを確認

## テスト自動化（Test Automation）

E2E自動テスト 4シナリオを **セキュリティ／バリデーション／認可／ハッピーパス** の4観点に分散して運用しています。実装上の工夫・検出効果（DEFECT-002 を自動化が検出した事例を含む）は [60 テスト完了レポート §11](./docs/60_test_completion_report.md#11-付記テスト自動化の実施結果-automated-test-summary) を参照。

### 自動化シナリオ一覧
- **Auto-01**：Requester による作成→確認のハッピーパス（TC-032 & TC-001）
- **Auto-02**：IDOR回帰（TC-002 / DEFECT-001 由来、`INTENTIONAL_BUG_IDOR` 切替で失敗実演可）
- **Auto-03**：本文4001文字のサーバ側拒否（TC-046）
- **Auto-04**：非担当 Agent のステータス変更UI抑止（TC-007 のUI側面）

### 技術スタック
- **Framework**: Playwright (Python)
- **Test Runner**: pytest（共通 fixture は `automation/conftest.py` に集約）
- **CI**: GitHub Actions

## 自動テストの実行方法

セットアップ手順とテスト実行コマンド（個別シナリオ実行・`--headed`・`BASE_URL` 切替など）は **[../SETUP.md](../SETUP.md)** に集約しています。
