# Ticket Management System with QA Automation
[![CI/CD Pipeline](https://github.com/nani9ashi/ticket-management-system/actions/workflows/ci.yml/badge.svg)](https://github.com/nani9ashi/ticket-management-system/actions/workflows/ci.yml)

## 📌 プロジェクト概要
QAエンジニアとしてのスキルを示すための、チケット管理システム（Django）およびE2E自動テスト（Playwright）の統合ポートフォリオです。  
「開発（Dev）」から「品質保証（QA）」、そして「CI/CDパイプライン」までの一連の流れを、**すべてコードベースで構築・自動化**しています。

## 🛠 技術スタック
| カテゴリ | 技術・ツール | 用途 |
| --- | --- | --- |
| **Language** | Python 3.12 | アプリケーションおよびテストコード記述 |
| **Framework** | Django 6.0 | Webアプリケーション構築 (MVP) |
| **Test Automation** | Playwright | E2Eテスト自動化、スクリーンショット取得 |
| **Test Runner** | pytest | テスト実行管理 |
| **CI/CD** | GitHub Actions | テスト実行・デプロイプロセスの自動化 |
| **Environment** | venv / pip | 仮想環境およびパッケージ管理 |

## 📂 ディレクトリ構成 (Monorepo)
本リポジトリは、開発（Dev）と品質保証（QA）を統合管理しています。

```text
root/
├── .github/workflows/  # CI/CD設定 (GitHub Actionsによる自動テスト実行)
├── app/                # 📦 アプリケーション本体 (Django)
└── qa/                 # 🧪 QA統合成果物 (JSTQBプロセス準拠)
```

## 🔗 主要ドキュメントへのリンク
- 📦 **アプリケーション仕様**: [app/README](./app/README.md)  
  - ロール権限、状態遷移、入力検証、意図的欠陥スイッチの解説
- 🧪 **QAテスト計画・自動化方針**: [qa/README](./qa/README.md)  
  - テスト計画から完了報告までの一連のQAプロセス資料、および自動テストの実装詳細

## ⚖️ QA戦略: 手動と自動のハイブリッド構成 (Hybrid Strategy)

本プロジェクトでは、**「人間が深く見るべき領域」**と**「機械が繰り返すべき領域」**を明確に分離し、最大の品質効率を追求しています。

| 特性 | 🖐️ 手動テスト (Manual Testing) | 🤖 自動テスト (Automated Testing) |
| :--- | :--- | :--- |
| **目的** | 仕様の深掘り、探索的テスト、ユーザビリティ確認 | 回帰テスト（リグレッション）、CI品質ゲート |
| **対象** | 複雑なビジネスロジック、エッジケース、異常系 | 正常系（Happy Path）、基本的な権限確認 |
| **成果物** | [JSTQB準拠ドキュメント一式](/qa/docs/00_project_overview.md)  | [Playwrightコード](/qa/automation/tests/test_scenario_01.py) |
| **規模** | **テストケース数: 44件**（網羅性を重視） | **シナリオ数: 1件**（実行速度を重視） |

---

## 🚀 主な取り組み (Highlights)

### 1. JSTQB準拠のテストプロセス（手動）
Vモデルを意識し、要求分析から完了報告までを一貫してドキュメント化しています。
- **テスト技法**: 同値分割法、境界値分析を用いた効率的なケース設計。
- **欠陥管理**: バグの発見から修正確認までをレポート化し、開発側へのフィードバックを実施。
- ▶ **詳細**: `qa/docs/`および [テストケース](/qa/testcases/testcases.csv)

### 2. E2Eテストの完全自動化（自動）
手動テストで安定稼働を確認した「クリティカルパス」をコード化し、リグレッションを自動検知します。
- **Framework**: Playwright + pytest
- **CI/CD**: GitHub Actionsにより、PR作成時に自動実行。
- ▶ **詳細**: [`qa/README.md`](./qa/README.md)

### 3. "Shift Left" を意識した構成
開発コード（`app`）とテストコード（`qa`）を同一リポジトリで管理することで、開発サイクルの中に品質保証プロセスを組み込んでいます。

## 💻 動作確認方法 (Local)
このリポジトリをクローンして、手元で動作させる手順です。

```bash
# 1. リポジトリのクローン
git clone https://github.com/<YOUR_ID>/ticket-management-system.git
cd ticket-management-system

# 2. 仮想環境の作成と有効化
python -m venv .venv

# Windows:
.\.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

# 3. 依存関係のインストール
pip install -r requirements.txt
playwright install chromium

# 4. サーバー起動とテスト実行

# (ターミナル1)
cd app
python manage.py migrate
python manage.py runserver

# (ターミナル2)
cd ../qa
python -m pytest automation/tests/ --headed
```

## 📝 ライセンス
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
