# Ticket Management System with QA Automation
[![CI/CD Pipeline](https://github.com/nani9ashi/ticket-management-system/actions/workflows/ci.yml/badge.svg)](https://github.com/nani9ashi/ticket-management-system/actions/workflows/ci.yml)

## プロジェクト概要
本リポジトリは、BtoB向けチケット管理システムの開発から、JSTQB準拠の品質保証（QA）プロセス、およびCI/CDパイプライン構築までを一人称で完遂した統合ポートフォリオです。

単なる動作確認にとどまらず、**「複雑な権限管理」や「状態遷移制約」を持つ実務的なシステム**を対象に、"Shift Left（テストの前倒し）"の思想に基づいた自動化・仕組み化をコードベースで実現しています。

## 技術スタック
| カテゴリ | 技術・ツール | 用途 |
| --- | --- | --- |
| **Language** | Python 3.12 | アプリケーションおよびテストコード記述 |
| **Framework** | Django 6.0 | Webアプリケーション構築 (MVP) |
| **Test Automation** | Playwright | E2Eテスト自動化、スクリーンショット取得 |
| **Test Runner** | pytest | テスト実行管理 |
| **CI/CD** | GitHub Actions | テスト実行・デプロイプロセスの自動化 |
| **Environment** | venv / pip | 仮想環境およびパッケージ管理 |

## テスト対象システム (SUT: System Under Test)
QAの実践性を高めるため、単なるCRUDアプリではなく、BtoB業務を想定した複雑なビジネスロジックを実装しています。

* **複雑な権限管理 (RBAC)**: 依頼者（Requester）、担当者（Agent）、管理者（Admin）による厳密なアクセス制御。
* **状態遷移制約 (State Machine)**: 「ClosedからOpenへの戻し禁止」など、業務フローに基づいた遷移ルール。
* **意図的欠陥 (Bug Injection)**: `INTENTIONAL_BUG_IDOR` フラグにより権限越えの脆弱性を意図的に発生させ、テストによるバグ検出能力を実証可能。

## ディレクトリ構成 (Monorepo)
本リポジトリは、開発（Dev）と品質保証（QA）を統合管理しています。

```text
root/
├── .github/workflows/  # CI/CD設定 (GitHub Actionsによる自動テスト実行)
├── app/                # アプリケーション本体 (Django)
└── qa/                 # QA統合成果物 (JSTQBプロセス準拠)
```

## 主要ドキュメントへのリンク
- **アプリケーション仕様**: [app/README](./app/README.md)  
  - ロール権限、状態遷移、入力検証、意図的欠陥スイッチの解説
- **テスト概要・自動化方針**: [qa/README](./qa/README.md)  
  - テスト計画から完了報告までの一連のQAプロセス資料、および自動テストの実装詳細

## QA戦略: 手動と自動のハイブリッド構成 (Hybrid Strategy)

本プロジェクトでは、**「人間が深く見るべき領域」**と**「機械が繰り返すべき領域」**を明確に分離し、最大の品質効率を追求しています。

| 特性 | 手動テスト (Manual Testing) | 自動テスト (Automated Testing) |
| :--- | :--- | :--- |
| **目的** | 仕様の深掘り、探索的テスト、ユーザビリティ確認 | 回帰テスト（リグレッション）、CI品質ゲート |
| **対象** | 複雑なビジネスロジック、エッジケース、異常系 | 正常系（Happy Path）、基本的な権限確認 |
| **成果物** | [JSTQB準拠ドキュメント一式](/qa/docs/00_project_overview.md)  | [Playwrightコード](/qa/automation/tests/test_scenario_01.py) |
| **規模** | **テストケース数: 44件**（網羅性を重視） | **シナリオ数: 1件**（実行速度を重視） |

---

## 主な取り組み (Highlights)

### 1. JSTQB準拠のテストプロセス（手動）
Vモデルを意識し、要求分析から完了報告までを一貫してドキュメント化しています。
- **テスト技法**: 同値分割法、境界値分析を用いた効率的なケース設計。
- **欠陥管理**: バグの発見から修正確認までをレポート化し、開発側へのフィードバックを実施。

### 2. E2Eテストの完全自動化（自動）
手動テストで安定稼働を確認した「クリティカルパス」をコード化し、リグレッションを自動検知します。
- **堅牢な実装 (Robust Automation)**: `name`属性などの不変属性を用いたロケータ戦略に基づく保守性の高いテスト実装。
- **Framework**: Playwright + pytest を使用。
- **CI/CD**: GitHub Actionsにより、PR作成時に自動実行。

### 3. "Shift Left" を意識した構成
開発コード（`app`）とテストコード（`qa`）を同一リポジトリで管理することで、開発サイクルの中に品質保証プロセスを組み込んでいます。

## 動作確認方法 (Local)

このリポジトリをクローンして、手元で動作させる手順です。  
※本手順では、アプリの実行とテストの実行にそれぞれ仮想環境（venv）の有効化が必要です。

### 1. 共通準備 (Setup)

まず、ベースとなる環境を構築します。

```bash
# クローンと移動
git clone https://github.com/<YOUR_ID>/ticket-management-system.git
cd ticket-management-system

# 仮想環境の作成
python -m venv .venv
```

#### 仮想環境の有効化（OS別）
> ※ 以降の `pip install` や `playwright install` は、仮想環境を有効化した状態で実行してください。

**Windows (PowerShell)**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

#### 依存関係のインストール
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. アプリとテストの実行

**必ず「2つのターミナル」を使用し、両方で仮想環境を有効にしてください。**

| 手順 | **ターミナル1（サーバー起動）** | **ターミナル2（テスト実行）** |
| --- | --- | --- |
| 1. ルートへ移動 | `cd ticket-management-system` | `cd ticket-management-system` |
| 2. 仮想環境を有効化 | Windows: `.\.venv\Scripts\Activate.ps1`<br>mac/Linux: `source .venv/bin/activate` | Windows: `.\.venv\Scripts\Activate.ps1`<br>mac/Linux: `source .venv/bin/activate` |
| 3. 実行 | `cd app`<br>`python manage.py migrate`<br>`python manage.py runserver` | `cd qa`<br>`python -m pytest automation/tests/ --headed --slowmo 1000` |

> **Note**: ターミナル2を実行する前に、ターミナル1でサーバーが正常に起動していることを確認してください。  
> 例：`Starting development server at http://127.0.0.1:8000/`

## ライセンス
本プロジェクトは MITライセンス に基づいて公開されています。利用条件については [LICENSE](LICENSE) ファイルをご参照ください。