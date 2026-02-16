# プロジェクト概要 - チケット管理アプリ

- 文書ID：OV-TICKET-001
- 版：v0.3
- ステータス：Draft
- 最終更新日：2026-01-19
- 作成者：仁後慎太郎
- 対象：チケット管理アプリ（Web, Django + SQLite）
- 関連：
  - 要件：[`../requirements/requirements.csv`](../requirements/requirements.csv)
  - テストケース：[`../testcases/testcases.csv`](../testcases/testcases.csv)
  - テスト結果：[`../results/test_results.csv`](../results/test_results.csv)
  - 欠陥ログ：[`../defects/defect_log.csv`](../defects/defect_log.csv)

---

## 1. 目的

チケット管理アプリ（BtoB想定）を題材に、QA成果物（テスト計画／テスト条件／テスト設計／テストケース／テスト結果／欠陥ログ／完了レポート）を作成し、GitHubで管理したポートフォリオとして提示する。

本リポジトリは、業務アプリで重要になりやすい以下の品質リスクを中心に扱う。

- 認可（ロール×操作×フィールド）
- 状態遷移（許可／禁止／運用制約）
- 入力検証（バリデーション、制約、エラーハンドリング）
- データ整合性（監査ログ含む）

---

## 2. MVP要件

MVP要件の正本は [`../requirements/requirements.csv`](../requirements/requirements.csv) とする。
本章は、テスト観点の理解を助けるための要約である。

### 2.1 ロールと権限
- Requester（依頼者）
  - 自分のチケットのみ：作成・閲覧・コメント可
  - 更新（ステータス／担当／期限／添付の変更）は不可
- Agent（担当者）
  - 全チケット閲覧可
  - **担当チケットのみ**：ステータス変更・コメント可
  - 担当割当／期限変更は不可
- Admin（管理者）
  - 全チケット閲覧・更新可
  - 担当割当、期限設定／変更可

### 2.2 共通ルール
- ログイン必須
- 主要操作は監査ログ（履歴）として残す
  - 作成／更新／ステータス変更／担当割当／期限変更／コメント追加 等
- 添付は作成時のみ
  - 差し替え／削除不可
  - 1ファイル
  - 拡張子・サイズ制限あり（詳細は要件CSVを正とする）

### 2.3 状態遷移
許可：
- Open → In Progress / Pending
- In Progress → Resolved / Pending
- Pending → In Progress
- Resolved → Closed

禁止：
- Open → Closed
- Closed →（いかなる遷移も）禁止

運用固定：
- ステータス変更は Agent（担当のみ）または Admin のみ
- 担当未割当のチケットは Agent がステータス変更できない（Adminが割当してから）

---

## 3. 成果物の構成

成果物は GitHub 上のファイルを正本として管理し、Notion には閲覧性向上のためのミラーを掲載する。  
Notion は随時更新するが、更新タイミングにより差分が出る可能性があり、その場合は **GitHub を正** とする。

### 3.1 ドキュメント
- テスト計画書：[`docs/10_test_plan.md`](docs/10_test_plan.md)
- テスト条件：[`docs/20_test_conditions.md`](docs/20_test_conditions.md)
- テスト設計：[`docs/30_test_design.md`](docs/30_test_design.md)
- テスト環境定義：[`docs/40_test_environment.md`](docs/40_test_environment.md)
- テスト実行方針：[`docs/50_test_execution_policy.md`](docs/50_test_execution_policy.md)
- テスト完了レポート：[`docs/60_test_completion_report.md`](docs/60_test_completion_report.md)
- 要件とテストのトレーサビリティ：[`docs/70_requirements_test_traceability.md`](docs/70_requirements_test_traceability.md)

### 3.2 CSV
- テストケース：[`testcases/testcases.csv`](testcases/testcases.csv)  
  ※実行状況は含めず、設計情報に集中しています。
- テスト結果：[`results/test_results.csv`](results/test_results.csv)  
  ※1実行=1行で追記します。
- 欠陥ログ：[`defects/defect_log.csv`](defects/defect_log.csv)  
  ※1欠陥=1行で管理します。

### 3.3 証跡
- スクリーンショット：[`evidence/screenshots/`](evidence/screenshots/)
- 動画：[`evidence/videos/`](evidence/videos/)
- ログ：[`evidence/logs/`](evidence/logs/)

---

## 4. リポジトリの見方

1. 本文書（`00_project_overview.md`）で全体像を把握する
2. `../requirements/requirements.csv` で要件（テストベース）を確認する
3. `10_test_plan.md` で方針・対象範囲を確認する
4. `20_test_conditions.md` → `../testcases/testcases.csv` の順に、条件→ケース展開を確認する
5. `../results/test_results.csv` と `../defects/defect_log.csv` で、実行結果と欠陥管理を確認する
6. `60_test_completion_report.md` で、結果のまとめ（残存リスク／教訓／次アクション）を確認する

