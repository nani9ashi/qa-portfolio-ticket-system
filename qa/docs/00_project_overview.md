# プロジェクト概要 - チケット管理アプリ

- 文書ID：OV-TICKET-001
- 版：v1.0
- ステータス：Approved
- 最終更新日：2026-02-17
- 作成者：仁後慎太郎
- 対象：チケット管理アプリ（Web, Django + SQLite）
- 関連：
  - 要件仕様：[`../requirements/requirements.csv`](../requirements/requirements.csv)
  - テストケース：[`../testcases/testcases.csv`](../testcases/testcases.csv)
  - テスト結果：[`../results/test_results.csv`](../results/test_results.csv)
  - 欠陥ログ：[`../defects/defect_log.csv`](../defects/defect_log.csv)

## 1. 目的

本ドキュメントの目的はQA成果物を一覧で示し、全体を概観できるようにすることである。

## 2. 成果物の構成

### 2.1 ドキュメント
- テスト計画書：[docs/10_test_plan.md](10_test_plan.md)
- テスト条件：[docs/20_test_conditions.md](20_test_conditions.md)
- テスト設計：[docs/30_test_design.md](30_test_design.md)
- テスト環境定義：[docs/40_test_environment.md](40_test_environment.md)
- テスト実行方針：[docs/50_test_execution_policy.md](50_test_execution_policy.md)
- テスト完了レポート：[docs/60_test_completion_report.md](60_test_completion_report.md)
- 要件とテストのトレーサビリティ：[docs/70_requirements_test_traceability.md](70_requirements_test_traceability.md)

### 2.2 CSV
- テストケース：[testcases/testcases.csv](../testcases/testcases.csv)  
  ※実行状況は含めず、設計情報に集中しています。
- テスト結果：[results/test_results.csv](../results/test_results.csv)  
  ※1実行=1行で追記します。
- 欠陥ログ：[defects/defect_log.csv](../defects/defect_log.csv)  
  ※1欠陥=1行で管理します。

### 2.3 証跡
- スクリーンショット：[evidence/screenshots/](../evidence/screenshots/)
- 自動化ログ：[evidence/auto/](../evidence/auto/)

## 3. リポジトリの見方

1. [本文書](00_project_overview.md)で全体像を把握する
2. [要件仕様](../requirements/requirements.csv) で要件（テストベース）を確認する
3. [テスト計画書](10_test_plan.md) で方針・対象範囲を確認する
4. [テスト条件](20_test_conditions.md) と [テストケース](../testcases/testcases.csv)   で、条件のケース展開を確認する
5. [テスト結果](../results/test_results.csv) と [欠陥ログ](../defects/defect_log.csv) で、実行結果と欠陥管理を確認する
6. [テスト完了レポート](60_test_completion_report.md)で、結果のまとめ（残存リスク／教訓／次アクション）を確認する