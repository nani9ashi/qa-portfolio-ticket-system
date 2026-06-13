# BtoB チケット管理システム：QA技術ポートフォリオ
[![CI Pipeline](https://github.com/nani9ashi/qa-portfolio-ticket-system/actions/workflows/ci.yml/badge.svg)](https://github.com/nani9ashi/qa-portfolio-ticket-system/actions/workflows/ci.yml)

## このポートフォリオの位置付け

本リポジトリは、QA エンジニアとして取り組んでいるポートフォリオシリーズの一つです。3 作は「品質保証で何を担うか」を段階的に広げており、**学習の深化の軌跡**としてご覧いただけます。

- **本リポジトリ** — QA 技術・基礎編。BtoB チケット管理システムを対象に、CI/CD・E2E 自動化・JSTQB 準拠ドキュメントで品質を作りこむ。
- **[AI学習レコメンド機能](https://github.com/nani9ashi/qa-portfolio-ai-recommender)** — QA 戦略・AI 編。確率的に揺らぐ生成 AI プロダクトを対象に、LLM-as-a-judge を含む複数層のテストで品質を設計する。
- **[既存の物体検出モデル](https://github.com/nani9ashi/qa-portfolio-object-detection)** — QA 評価・判断編。自分で作っていない調達候補モデルを外から評価し、固定した基準に対して導入可否を判断し品質を守る。

## プロジェクト概要

BtoB業務を想定した **複雑な RBAC と状態遷移を持つチケット管理アプリ** を対象に、JSTQB 準拠のテストプロセスと E2E 自動化（CI 品質ゲート）を一人称で完遂した統合ポートフォリオです。SUT の詳細は [app/README](./app/README.md) を参照。

## 技術スタック

本ポートフォリオの技術スタックの正本です。app/README §2 と qa/README はここを参照します。

| カテゴリ | 技術・ツール | 用途 |
| --- | --- | --- |
| **Language** | Python 3.12 | アプリケーションおよびテストコード記述 |
| **Framework** | Django 6.0 | Webアプリケーション構築 (MVP) |
| **API Layer (テスト容易性)** | Django REST Framework | runn 用の薄い JSON API（Token 認証・CSRF レス） |
| **Test Automation** | Playwright | E2Eテスト自動化、スクリーンショット取得 |
| **API/Integration Test** | runn (k1LoW) ※v1.9.2 固定 | 認可・状態遷移・入力検証の組合せ網羅（高速・決定的） |
| **Test Runner** | pytest | テスト実行管理 |
| **CI** | GitHub Actions | E2E（Playwright）と API（runn）を毎 push 自動実行・証跡保存 |
| **Environment** | venv / pip | 仮想環境およびパッケージ管理 |

## テスト対象システム (SUT: System Under Test)

ロール認可（[§5](./app/README.md#5-ロールと権限仕様rbac)）／状態遷移（[§6](./app/README.md#6-ステータス遷移仕様state-machine)）／意図的欠陥スイッチ（[§9](./app/README.md#9-テスト用の意図的欠陥bug-switch)）を備えた SUT。詳細は [app/README](./app/README.md)。

## ディレクトリ構成 (Monorepo)
本リポジトリは、開発（Dev）と品質保証（QA）を統合管理しています。

```text
root/
├── .github/workflows/  # CI設定 (GitHub Actionsによる自動テスト実行)
├── app/                # アプリケーション本体 (Django)
└── qa/                 # QA統合成果物 (JSTQBプロセス準拠)
```

## 主要ドキュメントへのリンク
- **アプリケーション仕様**: [app/README](./app/README.md)  
  - ロール権限、状態遷移、入力検証、意図的欠陥スイッチの解説
- **テスト概要・自動化方針**: [qa/README](./qa/README.md)  
  - テスト計画から完了報告までの一連のQAプロセス資料、および自動テストの実装詳細

## QA戦略: テストピラミッドに基づく3層構成 (Layered Strategy)

「**人間が深く見るべき領域**」「**組合せを高速・決定的に網羅すべき領域**」「**端から端まで繋がることを示す領域**」を分離し、各ロジックを最適な層で検証します。**なぜその層なのか**の判断は [テスト層戦略（80）](./qa/docs/80_test_layer_strategy.md) に明文化しています。

| 層 | 役割 | 対象 | 規模 | 成果物 |
| :--- | :--- | :--- | :--- | :--- |
| **手動テスト** | 仕様の深掘り・探索的・ユーザビリティ | 複雑な業務ロジック・異常系 | **TC 46件** | [JSTQB準拠ドキュメント](./qa/README.md) |
| **API/インテグレーション（runn）** | 認可(RBAC/IDOR)・状態遷移・入力検証の**組合せ網羅** | 期待値が一意に決まる決定的ロジック | **10 runbook / 102 step** | [runn runbook](./qa/api/) |
| **E2E（Playwright）** | 代表導線＋認可スモーク＋UI抑止＋実欠陥回帰 | フルスタックの結線 | **4シナリオ** | [Playwrightコード](./qa/automation/tests/) |

> **本拡張の核**：RBAC × 状態遷移という組合せ爆発を E2E から **API 層へ押し下げ**、E2E を代表シナリオに集約しました（before/after と判断根拠は [80](./qa/docs/80_test_layer_strategy.md)）。API 層は**入力に対し期待レスポンスが一意に定まる「決定的な世界」だから成立**します。**この「期待値を厳密に書き下せること自体」が、次作 ②（確率的に揺らぐ生成 AI プロダクト＝期待値表が書けない世界）との対比点** になります。

---

## 主な取り組み (Highlights)

### 1. JSTQB準拠のテストプロセス（手動）
Vモデルを意識し、要求分析から完了報告までを一貫してドキュメント化しています。
- **テスト技法**: 同値分割法、境界値分析を用いた効率的なケース設計。
- **欠陥管理**: バグの発見から修正確認までをレポート化し、開発側へのフィードバックを実施。

### 2. テスト自動化：API層(runn)＋E2E(Playwright)
QAリスク観点（IDOR／境界値／RBAC／状態遷移）の**組合せ網羅**は **runn の API/インテグレーション層（10 runbook / 102 step）** で高速・決定的に検証し、E2E は代表シナリオに集約しています（層の判断は [80](./qa/docs/80_test_layer_strategy.md)）。
- **E2E シナリオ構成（再配分後）**: ハッピーパス（Auto-01）／IDOR回帰スモーク（Auto-02）／非担当AgentのUI抑止（Auto-04）／期限過去日の graceful 拒否（Auto-05、DEFECT-003回帰）。組合せ網羅（境界値・認可マトリクス・状態遷移）は runn 層へ移設。詳細は [60_test_completion_report.md §11](./qa/docs/60_test_completion_report.md#11-付記テスト自動化の実施結果-automated-test-summary)。
- **堅牢な実装 (Robust Automation)**: `name`属性などの不変属性を用いたロケータ戦略。共通fixture（`qa/automation/conftest.py`）でログイン・BASE_URL・証跡保存を集約。
- **Framework**: Playwright + pytest を使用。`BASE_URL` 環境変数で接続先切替可。
- **CI**: GitHub Actionsにより、PR作成時に4シナリオすべてを自動実行。

#### 自動テストが捕捉した代表的な挙動

以下は CI Artifacts から取得した実際のスクリーンショットです。

**Auto-03 — DEFECT-002 修正後の本文バリデーション**

![Auto-03: 本文4001文字のサーバ側拒否](./qa/docs/images/auto-03_body_validation_error.png)

本文4001文字での作成試行に対し、`Ensure this value has at most 4000 characters (it has 4001).` を表示して拒否。本シナリオの実装中に **[DEFECT-002](./qa/defects/reports/DEFECT-002.md)（body max_length 未実装）** を検出・修正・回帰確認した。

> 本拡張で本境界値検証は runn `validation/title_body_boundary.yml` の **4点境界（空/1/最大/最大+1）** へ移設し、Auto-03 自体は削除した（上図は移設前の E2E 証跡）。

**Auto-04 — 非担当Agentの認可UI抑止**

![Auto-04: 非担当AgentはステータスUIを操作できない](./qa/docs/images/auto-04_agent_no_status_ui.png)

agent2 が非担当チケット（agent1割当）を開くと、Status Transition は「Not allowed to change status.」のみで `<select>` が描画されない。「**見えるが操作できない**」というRBACの正常な挙動を確認。

### 3. シフトレフトを意識した構成
開発コード（`app`）とテストコード（`qa`）を同一リポジトリで管理することで、開発サイクルの中に品質保証プロセスを組み込んでいます。

### 4. テストピラミッド最適化（API/インテグレーション層の新設）
RBAC（権限マトリクス）と状態遷移という「組合せが爆発するロジック」を、遅く脆い E2E から **runn の API 層へ押し下げ**ました。
- **薄い API は QA 判断**：テスト容易性のため最小限の JSON API（DRF・Token 認証）を追加。認可ルールは HTML ビューと [policy.py](./app/tickets/policy.py) を**共有（単一ソース）**し、`INTENTIONAL_BUG_IDOR` を立てると **API の IDOR テストと E2E(Auto-02) が同時に・同一原因で失敗**します（テストが本物を見ている担保）。
- **下層が上層の不具合を炙り出した**：API の期待値（過去日 → 400）を厳密に書き下す過程で、HTML の期限変更が過去日で **500 になる実バグ（[DEFECT-003](./qa/defects/reports/DEFECT-003.md)）** を発見し、起票 → 修正 → 回帰まで完了（DEFECT-001/002 に続く3例目）。
- 判断の全文は [テスト層戦略（80）](./qa/docs/80_test_layer_strategy.md)。

## 本ポートフォリオの範囲

テスト計画における「説明責任」を意識し、**意図的にスコープ外とした項目** を以下に明示します。やらない理由を残すこと自体も品質活動の一部だと考えています。

- **単体テスト（Unit Test）**：純粋関数単位（`models.py` 等）の単体テストは引き続き最小限です。ただし本拡張で認可ロジックを [policy.py](./app/tickets/policy.py) へ分離したため「ロジックが画面側に密結合」という従来の前提は緩和され、API/インテグレーション層で同ロジックを実質的に検証できるようになりました。純粋関数単位の `pytest` は引き続き Backlog です。
- **コンシューマ駆動契約テスト（CDC / Pact）**：**未実装**。単一サービスのため不要ですが、将来サービスが分割・独立デプロイされた場合に「API 契約を提供側／消費側で独立に守る」問いとして [テスト層戦略 §8](./qa/docs/80_test_layer_strategy.md) に記録しています（連作の主問題とは別方向の宿題）。
- **API 層の添付（attachment）境界**：拡張子・サイズの境界は組合せ価値が薄いため API テストの対象外とし、E2E／手動（TC-038/039）に残しています。
- **専門的な脆弱性診断（侵入テスト等）**：今回の QA 活動の対象外。簡易的な脆弱性のチェックを、意図的欠陥（IDOR）の起票→修正→回帰のフローで表現しています。

未カバー要件の扱いについては、[要件とテストのトレーサビリティ](./qa/docs/70_requirements_test_traceability.md) で A（追加してカバー）／ B（スコープ外）／ C（要件を修正・明確化）に分類して管理しています。

## 動作確認

CIで `push` / `pull_request` 時に4シナリオを自動実行（上部バッジ参照）。手元で動かす場合の手順は **[SETUP.md](./SETUP.md)** に集約しています。

## 作者

**仁後慎太郎**

「現場で本当に使えるプロダクトをどう作るか」に関心を持って学習を続けている社会人です。JSTQB Foundation Level 保有。塾講師や警備員としての経験と、哲学を専攻したバックグラウンドを持ち、**ユーザーや現場目線で仮説を立て、関係者と対話しながら品質を作り込む**スタイルを模索しています。正確性や信頼性が求められる BtoB 領域においても、観察力と論理性で価値を生み出していきたいと考えています。

## ライセンス
本プロジェクトは MITライセンス に基づいて公開されています。利用条件については [LICENSE](LICENSE) ファイルをご参照ください。