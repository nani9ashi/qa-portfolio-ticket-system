# QAポートフォリオ：チケット管理アプリ

[チケット管理アプリ](../app/README.md) を対象とした、品質保証（QA）の統合成果物です。  
本ディレクトリ（`qa/`）には、**テスト計画・設計・実行・欠陥管理**、および **E2E自動化（Playwright/pytest）** の全工程を集約しています。

## QA資材の構成

```text
qa/
├── docs/                # テストドキュメント (JSTQB準拠)
│   ├── 00_project_overview.md       # プロジェクト概要
│   ├── 10_test_plan.md              # テスト計画書
│   ├── 20_test_conditions.md        # テスト条件
│   ├── 30_test_design.md            # テスト設計書
│   └── ...                          # テスト完了レポート、トレーサビリティ等
├── automation/          # テスト自動化 (Playwright/pytest)
├── requirements/        # 要求仕様 (CSV形式)
├── testcases/           # テストケース定義
├── results/             # テスト実行結果
├── defects/             # 欠陥管理 (ログおよび詳細レポート)
└── evidence/            # 実行証跡 (スクショ・動画・ログ)
```

## 主要ドキュメント・リンク

### テスト計画・設計ドキュメント一覧
- [プロジェクト概要](./docs/00_project_overview.md)
- [テスト計画書](./docs/10_test_plan.md)
- [テスト条件](./docs/20_test_conditions.md)
- [テスト設計](./docs/30_test_design.md)

### テストケース・実行結果
- [テストケース](./testcases/testcases.csv)
- [テスト結果](./results/test_results.csv)

### 要件トレーサビリティ
- [要求仕様](./requirements/requirements.csv)
- [要件とテストのトレーサビリティ](./docs/70_requirements_test_traceability.md)
### 欠陥レポート
- [DEFECT-001（IDOR：依頼者が他人チケット詳細を閲覧できた）](./defects/reports/DEFECT-001.md)
- [DEFECT-002（body max_length が実装で enforce されていなかった／自動化Auto-03が検出）](./defects/reports/DEFECT-002.md)
- [欠陥ログ](./defects/defect_log.csv)

### プロジェクトトップ（全体概要）
- [root README](../README.md)

## 🛠 QAプロセスと取り組み

本プロジェクトでは、以下の品質保証活動を実践しています。

### 1. 要件トレーサビリティの確保
[要求仕様](./requirements/requirements.csv)から[テストケース](./testcases/testcases.csv)への紐付けを行い、テストカバレッジを可視化しています。

### 2. テスト自動化（Shift Left）
Playwright を用いたE2E自動テストを構築し、GitHub Actions によるCIに組み込む前提で設計しています。

### 3. 欠陥管理の徹底
検出されたバグは `defects/` 内で形式化して管理し、原因分析と再テストの結果までを記録します。

## テスト自動化（Test Automation Strategy）

本プロジェクトでは、品質保証の効率化と早期バグ発見（Shift Left）のため、E2E自動テストを戦略的に導入しています。現状 **4シナリオ** を運用中で、ハッピーパス／セキュリティ／バリデーション／認可 の4観点に分散させています。

### 自動化の狙い
- **品質ゲートの構築**: GitHub Actionsと連携し、テストをパスしないコードのマージを防止。
- **クロスブラウザ/ロールテスト**: 複数の権限（Admin/Agent/Requester）を跨ぐ複雑な認可ロジックを自動で検証。
- **エビデンスの自動取得**: 失敗時のスクリーンショット保存により、バグ再現の手間を大幅に削減。

### 自動化シナリオ一覧（4本）
- **Auto-01**：Requester による作成→確認のハッピーパス（TC-032 & TC-001）
- **Auto-02**：IDOR回帰（TC-002 / DEFECT-001 由来、`INTENTIONAL_BUG_IDOR` 切替で失敗実演可）
- **Auto-03**：本文4001文字のサーバ側拒否（TC-046）
- **Auto-04**：非担当 Agent のステータス変更UI抑止（TC-007 のUI側面）

詳細は [60_test_completion_report.md §11](./docs/60_test_completion_report.md#11-付記テスト自動化の実施結果-automated-test-summary) を参照してください。

### 技術スタック
- **Framework**: Playwright (Python)
- **Test Runner**: pytest（共通 fixture は `automation/conftest.py` に集約）
- **CI/CD**: GitHub Actions
---

## 自動テストの実行方法

ルートディレクトリで仮想環境を有効化した状態で、以下のコマンドを実行してください。

```powershell
# qa/automation ディレクトリへ移動（pytest.ini が自動探索する）
cd qa/automation

# 全シナリオ実行（ブラウザ表示あり）
python -m pytest --headed

# 個別シナリオ実行（例：IDOR回帰のみ）
python -m pytest tests/test_scenario_02_idor.py --headed
```

`BASE_URL` 環境変数で接続先を切り替えられます（既定：`http://127.0.0.1:8000`）。
