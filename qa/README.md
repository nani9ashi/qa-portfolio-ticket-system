# QAポートフォリオ：チケット管理アプリ

[チケット管理アプリ](../app/README.md) を対象とした、品質保証（QA）の統合成果物です。  
本ディレクトリ（`qa/`）には、**テスト計画・設計・実行・欠陥管理**、および **E2E自動化（Playwright/pytest）** の全工程を集約しています。

## 📂 QA資材の構成

```text
qa/
├── docs/                # 📄 テストドキュメント (JSTQB準拠)
│   ├── 00_project_overview.md       # プロジェクト概要
│   ├── 10_test_plan.md              # テスト計画書
│   ├── 20_test_conditions.md        # テスト条件
│   ├── 30_test_design.md            # テスト設計書
│   └── ...                          # テスト完了レポート、トレーサビリティ等
├── automation/          # 🤖 テスト自動化 (Playwright/pytest)
├── requirements/        # 📋 要求仕様 (CSV形式)
├── testcases/           # 📝 テストケース定義
├── results/             # ✅ テスト実行結果
├── defects/             # 🐛 欠陥管理 (ログおよび詳細レポート)
└── evidence/            # 📸 実行証跡 (スクショ・動画・ログ)
```

## 🔗 主要ドキュメント・リンク

### 📂 テスト計画・設計ドキュメント一覧
- [プロジェクト概要](./docs/00_project_overview.md)
- [テスト計画書](./docs/10_test_plan.md)
- [テスト条件](./docs/20_test_conditions.md)
- [テスト設計](./docs/30_test_design.md)

### 📊 テストケース・実行結果
- [テストケース](./testcases/testcases.csv)
- [テスト結果](./results/test_results.csv)

### 🧩 要件トレーサビリティ
- [要求仕様](./requirements/requirements.csv)
- [要件とテストのトレーサビリティ](./docs/70_requirements_test_traceability.md)
### 🐛 欠陥レポート
- [欠陥レポート（例：defects/reports/DEFECT-001.md）](./defects/reports/DEFECT-001.md)
- [欠陥ログ](./defects/defect_log.csv)

### 🏠 プロジェクトトップ（全体概要）
- [root README](../README.md)

## 🛠 QAプロセスと取り組み

本プロジェクトでは、以下の品質保証活動を実践しています。

### 1. 要件トレーサビリティの確保
[要求仕様](./requirements/requirements.csv)から[テストケース](./testcases/testcases.csv)への紐付けを行い、テストカバレッジを可視化しています。

### 2. テスト自動化（Shift Left）
Playwright を用いたE2E自動テストを構築し、GitHub Actions によるCIに組み込む前提で設計しています。

### 3. 欠陥管理の徹底
検出されたバグは `defects/` 内で形式化して管理し、原因分析と再テストの結果までを記録します。

## 🤖 テスト自動化（Test Automation Strategy）

本プロジェクトでは、品質保証の効率化と早期バグ発見（Shift Left）のため、E2E自動テストを戦略的に導入しています。

### 自動化の狙い
- **品質ゲートの構築**: GitHub Actionsと連携し、テストをパスしないコードのマージを防止。
- **クロスブラウザ/ロールテスト**: 複数の権限（Admin/Agent/Requester）を跨ぐ複雑な認可ロジックを自動で検証。
- **エビデンスの自動取得**: 失敗時のスクリーンショット保存により、バグ再現の手間を大幅に削減。

### 技術スタック
- **Framework**: Playwright (Python)
- **Test Runner**: pytest
- **CI/CD**: GitHub Actions
---

## 🚀 自動テストの実行方法

ルートディレクトリで仮想環境を有効化した状態で、以下のコマンドを実行してください。

```powershell
# qaディレクトリへ移動
cd qa

# 全テスト実行（ブラウザ表示あり）
python -m pytest automation/tests/ --headed
```
