# チケット管理アプリ（Web, Django + SQLite）

BtoB業務アプリで頻出する **ワークフロー（状態遷移）・ロール認可・入力検証・監査ログ（履歴）** を最小構成で揃えた、チケット管理アプリのMVP（Minimum Viable Product）です。

本アプリケーションは、E2E自動テストの検証対象（SUT: System Under Test）として開発されました。

## 1. 目的と範囲

### 目的
QA成果物に落とし込みやすい題材として、業務アプリの品質リスクが出やすい領域を意図的に実装しています。

- **認可**: ロール × 操作 × フィールドの組み合わせ
- **状態遷移**: 許可ルート／禁止ルート／運用制約
- **入力検証**: 必須、最大長、過去日制限、添付ファイル制限
- **監査ログ**: 誰が・いつ・何をしたかのトラッキング

### 範囲
- **画面**: ログイン、チケット一覧、チケット詳細、チケット作成
- **機能**: 検索・ステータスフィルタ、コメント、履歴（監査ログ）、担当割当、ステータス変更
- **制限**: 添付ファイルは作成時のみ（1ファイル、拡張子／サイズ制限あり）

## 2. 技術スタック

技術スタックの正本は [root README §技術スタック](../README.md#技術スタック)。本アプリ固有の選定は **Database: SQLite**（開発用・ファイルベースDB）、**Auth: Django 標準認証**（セッションベース）。

## 3. セットアップ

セットアップ手順は **[../SETUP.md](../SETUP.md)** に集約しています（クローン → 仮想環境 → 依存インストール → DB初期化 → サーバー起動 → テスト実行）。

起動後のアクセス先：
- ログイン画面：`http://127.0.0.1:8000/accounts/login/`
- チケット一覧：`http://127.0.0.1:8000/`

## 4. デモユーザー（seed_demo）

`python manage.py seed_demo` で作成されるテスト用ユーザー（共通パスワード `pass1234`）の一覧は [../SETUP.md §3](../SETUP.md#3-db-初期化とデモデータ投入) を参照。

## 5. ロールと権限仕様（RBAC）

各ロールの権限マトリクスは以下の通りです。

| 操作 | Requester（依頼者） | Agent（担当者） | Admin（管理者） |
| --- | --- | --- | --- |
| 閲覧 | 自分のチケットのみ | 全て | 全て |
| 作成 | ○（RQ-012, Must） | ×（RQ-013, Must） | ×（RQ-014 Should、設計判断として B 確定） |
| コメント | ○ | ○ | ○ |
| ステータス変更 | × | 担当チケットのみ ○ | ○ |
| 担当割当 | × | × | ○ |
| 期限変更 | × | × | ○ |

> **「作成」のロール設計**：Agent（RQ-013, Must）と Admin（RQ-014, Should）はいずれも作成不可。**起票責務を Requester に集約する設計判断**（責務分離・起票の真正性確保）。RQ-014 を B 確定（対象外）とした経緯・代理起票案の検討は [qa/docs/70 §8](../qa/docs/70_requirements_test_traceability.md#8-backlog未カバー一部の解消候補) を参照。

## 6. ステータス遷移仕様（State Machine）

###　許可ルート
- Open → In Progress / Pending
- In Progress → Resolved / Pending
- Pending → In Progress
- Resolved → Closed

### 禁止ルート
- Open → Closed（直接のクローズ不可）
- Closed → その他すべて（完了後の変更不可）

### 運用制約
- ステータス変更は **Agent（自分の担当分のみ）** または **Admin** のみ可能
- 担当未割当のチケットは **Agent** がステータス変更できない（**Adminが割当後に操作可能**）

## 7. 入力検証仕様（Validation）
- **Title**: 必須、最大80文字
- **Body**: 必須、最大4000文字
- **Due date**: 任意、過去日不可（Adminのみ設定/変更）
- **Attachment**: 任意、1ファイル、拡張子制限（png/jpg/jpeg/pdf/txt）、最大5MB
- 添付は作成時のみ（差し替え／削除は不可）

## 8. 監査ログ（履歴）

チケット詳細画面で履歴を確認できます。  
MVPでは主に以下の操作を記録します。

- CREATED（起票）
- STATUS_CHANGED（ステータス変更）
- ASSIGNEE_CHANGED（担当者変更）
- COMMENT_ADDED（コメント追加）
- DUE_DATE_CHANGED（期限変更）

## 9. テスト用の意図的欠陥（Bug Switch）

QA検証（自動テストのフェイル実演）の題材として、`config/settings.py` に **`INTENTIONAL_BUG_IDOR`** スイッチを実装。

- **True**：Requester が他人チケットを閲覧可能になる脆弱状態（IDOR: Insecure Direct Object Reference）を再現
- **False（既定）**：正常な認可（Requester は自分のチケットのみ閲覧可）

QA 運用での扱い（テスト時の ON/OFF 記録ルール、自動化での Fail 実演手順）は [qa/docs/40_test_environment.md §6](../qa/docs/40_test_environment.md#6-意図的欠陥検出修正の題材) と [qa/docs/90_automated_test_report.md §4](../qa/docs/90_automated_test_report.md#4-検出能力の実演手順idor回帰) を参照。

## 10. 関連リソース
- **QA統合成果物**: [qa/README](../qa/README.md)
  - 本アプリを対象としたテスト計画書、テストケース、および欠陥レポートを管理しています。
- **全体概要**: [root README](../README.md)
  - ポートフォリオ全体の概要を記述しています。
