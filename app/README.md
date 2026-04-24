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
- **Language**: Python 3.12
- **Framework**: Django 6.0
- **Database**: SQLite（開発用・ファイルベースDB）
- **Auth**: Django標準認証（セッションベース）

## 3. セットアップ

本リポジトリはMonorepo構成です。ルートディレクトリで仮想環境（`venv`）を構築済みであることを前提とします。

### 3.1 DB初期化とデモデータ投入
```powershell
# ルートディレクトリから app フォルダへ移動
cd app

# マイグレーションとデモデータの投入
python manage.py migrate
python manage.py seed_demo

# サーバー起動
python manage.py runserver
```

起動後のアクセス先：
- ログイン画面：`http://127.0.0.1:8000/accounts/login/`
- チケット一覧：`http://127.0.0.1:8000/`

## 4. デモユーザー（seed_demo）

`python manage.py seed_demo` コマンドで以下のテスト用ユーザーが作成されます。  
全ユーザーの共通パスワード：`pass1234`

| ロール | ユーザー名（ログインID） |
| --- | --- |
| Requester（依頼者） | `requester1`, `requester2` |
| Agent（担当者） | `agent1`, `agent2` |
| Admin（管理者） | `admin1` |

## 5. ロールと権限仕様（RBAC）

各ロールの権限マトリクスは以下の通りです。

| 操作 | Requester（依頼者） | Agent（担当者） | Admin（管理者） |
| --- | --- | --- | --- |
| 閲覧 | 自分のチケットのみ | 全て | 全て |
| 作成 | ○ | ○ | ○ |
| コメント | ○ | ○ | ○ |
| ステータス変更 | × | 担当チケットのみ ○ | ○ |
| 担当割当 | × | × | ○ |
| 期限変更 | × | × | ○ |

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

本アプリには、QA検証（探索的テストや自動テストのフェイル確認）の題材として、**意図的欠陥を再現するスイッチ**を実装しています。

### INTENTIONAL_BUG_IDOR
認可制御の不備（IDOR: Insecure Direct Object Reference）をシミュレートします。

- **True の場合**: 閲覧認可が崩れ、RequesterがURLを直接指定するなどで「他人のチケットを閲覧できる」脆弱な状態を再現
- **False の場合**: 正常な認可（Requesterは自分のチケットのみ閲覧可能）

設定箇所（`config/settings.py`）：
```python
# 脆弱性テストを行う場合は True に変更してください
INTENTIONAL_BUG_IDOR = False
```

## 10. 関連リソース
- **QA統合成果物**: [qa/README](../qa/README.md)
  - 本アプリを対象としたテスト計画書、テストケース、および欠陥レポートを管理しています。
- **全体概要**: [root README](../README.md)
  - ポートフォリオ全体の概要を記述しています。
