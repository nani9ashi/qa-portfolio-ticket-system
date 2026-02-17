# チケット管理アプリ（Web, Django + SQLite）

BtoB業務アプリで頻出する **ワークフロー（状態遷移）・ロール認可・入力検証・監査ログ（履歴）** を最小構成で揃えた、チケット管理アプリのMVP（Minimum Viable Product）です。

本アプリケーションは、E2E自動テストの検証対象（SUT: System Under Test）として開発されました。

---

## 1. 目的と範囲

### 目的
- QA成果物に落とし込みやすい題材として、業務アプリの品質リスクが出やすい領域を実装する
  - 認可（ロール×操作×フィールド）
  - 状態遷移（許可／禁止／運用制約）
  - 入力検証（必須、最大長、過去日、添付制限）
  - 監査ログ（誰がいつ何をしたか）

### 範囲
- ロール：Requester / Agent / Admin
- 画面：ログイン、チケット一覧、チケット詳細、チケット作成
- 機能：検索・ステータスフィルタ、コメント、履歴（監査ログ）、担当割当（Admin）、ステータス変更（Agent担当のみ/Admin）
- 添付：作成時のみ、1ファイル、拡張子／サイズ制限

---

## 2. 技術スタック
- Python 3.12
- Django 6.0.2
- SQLite（開発用・ファイルベースDB）
- Django標準認証（ログイン）

---

## 3. セットアップ（Windows / PowerShell）

本リポジトリはMonorepo構成です。ルートディレクトリで仮想環境を構築済みであることを前提とします。

### 3.1 DB初期化とデモデータ投入
```powershell
# ルートディレクトリから実行
cd app
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

起動後：
- ログイン：`http://127.0.0.1:8000/accounts/login/`
- 一覧：`http://127.0.0.1:8000/`

---

## 4. デモユーザー（seed_demo）

`python manage.py seed_demo` で以下を作成します。  
全ユーザーのパスワードは **`pass1234`** です。

- **Requester**（依頼者）: `requester1`, `requester2`
- **Agent**（担当者）: `agent1`, `agent2`
- **Admin**（管理者）: `admin1`

---

## 5. ロールと権限仕様

### Requester（依頼者）
- 自分のチケットのみ：作成・閲覧・コメント可
- ステータス変更／担当割当／期限変更：不可

### Agent（担当者）
- 全チケット閲覧可
- **担当チケットのみ**：ステータス変更可
- コメント：可
- 担当割当／期限変更：不可

### Admin（管理者）
- 全チケット閲覧・更新可
- 担当割当：可
- 期限設定／変更：可

---

## 6. ステータス遷移仕様

**許可ルート：**
- Open → In Progress / Pending
- In Progress → Resolved / Pending
- Pending → In Progress
- Resolved → Closed

**禁止ルート：**
- Open → Closed
- Closed →（いかなる遷移も）禁止

**運用制約：**
- ステータス変更は Agent（担当のみ）または Admin のみ
- **担当未割当のチケットは Agent がステータス変更できない**（Adminが割当後に運用）

---

## 7. 入力検証仕様
- **Title**: 必須、最大80文字
- **Body**: 必須、最大4000文字
- **Due date**: 任意、過去日不可（Adminのみ設定/変更）
- **Attachment**: 任意、1ファイル、拡張子制限（png/jpg/jpeg/pdf/txt）、最大5MB
- 添付は作成時のみ（差し替え／削除は不可）

---

## 8. 監査ログ（履歴）

チケット詳細画面で履歴を確認できます。  
MVPでは主に以下の操作を記録します。

- CREATED
- STATUS_CHANGED
- ASSIGNEE_CHANGED
- COMMENT_ADDED
- DUE_DATE_CHANGED

---

## 9. テスト用の意図的欠陥（Bug Switch）

本アプリには、QA検証の題材として **意図的欠陥を再現するスイッチ** を埋め込んでいます。

### INTENTIONAL_BUG_IDOR
- `True` の場合：閲覧認可が崩れ、Requesterが他人チケットを閲覧できる状態を再現します（IDOR想定）
- `False` の場合：通常の認可（Requesterは自分のチケットのみ）

設定ファイル（`config/settings.py`）：
```python
INTENTIONAL_BUG_IDOR = False
```

---

## 10. 関連リソース
- 🧪 **QA統合成果物**: [qa/README](../qa/README.md)
  - 本アプリを対象としたテスト計画書、テストケース、および欠陥レポートを管理しています。
- 🏠 **全体概要**: [root README](../README.md)
