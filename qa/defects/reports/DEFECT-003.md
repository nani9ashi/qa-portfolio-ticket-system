# DEFECT-003 期限変更で過去日入力時に 500 エラー（full_clean の例外が未処理）

## 1. 基本情報
- 状態：検証済
- 重要度：Medium
- 優先度：Medium
- 発見日：2026-06-13
- 発見者：仁後慎太郎
- 検出環境：Win11/Chrome（ローカル）
- 検出ビルド：app-v0.5-pre（runn API/インテグレーションテスト層の追加時）
- 関連テストケース：TC-036（due_date 過去日不可）／ Auto-05（HTML 回帰として自動化）／ API-C2（runn `validation/due_date.yml` の API 期待値）
- 関連要件：RQ-006（due_date は任意で過去日不可）
- 証跡：
  - [Auto-05 修正後のスクリーンショット](../../automation/evidence/auto/test_past_due_date_is_rejected_gracefully[chromium]/due_past_error.png)
- 備考：runn API 層の **期待値設計（過去日 → 400）** を書き下す過程で発見。手動 TC-036／既存 E2E では検出されていなかった。

## 2. 概要
Admin が詳細画面の「Due date」フォームから **過去日**（または不正な日付）を送信すると、サーバー側で `ValidationError` が捕捉されず **HTTP 500（未処理例外）** になる。作成画面（`ticket_create`）では同等の検証を `try/except` で囲み graceful にエラー表示しているのに対し、期限変更（`ticket_change_due_date`）では囲んでいない、という **実装の非対称性** に起因する。

## 3. 前提（テストデータ）
- admin1 でログイン可能
- 任意のチケット詳細（例：`/tickets/2/`）の「Due date (Admin only)」フォームが表示できる

## 4. 再現手順
1. admin1 でログインする
2. 任意のチケット詳細画面を開く
3. 「Due date (Admin only)」に **過去日**（例：`2000-01-01`）を入力する
4. 「Save」ボタンをクリックする

## 5. 期待結果 / 実際結果 / 影響範囲
- **期待**：詳細画面に留まり、エラーメッセージ（"Due date cannot be in the past."）が表示され、期限は更新されない。
- **実際（修正前）**：`Ticket.clean()` が送出する `ValidationError` が `views.ticket_change_due_date` で捕捉されず、HTTP 500（DEBUG 時はスタックトレース画面）になる。
- **影響範囲**：RQ-006（Must 要件）の異常系 UX を満たさない。検証ルール自体は `Ticket.clean()`（モデル層）に正しく存在するが、**HTML プレゼンテーション層が拒否を握り潰して 500 にしている**。本番（`DEBUG=False`）では汎用 500 となりデータ破損はないが、堅牢性・ユーザビリティの欠陥。

## 6. 原因と修正方針
- **（確認済）原因①（過去日）**：`app/tickets/views.py` の `ticket_change_due_date` で `ticket.full_clean()` を `try/except` の外で呼んでいる。一方 `ticket_create` は `full_clean()` を `try/except` で囲み、失敗時に作成画面を error 付きで再描画している。同じ検証なのに後者だけ未処理という非対称が原因。
- **（回帰検証中に追加発見）原因②（不正フォーマット）**：`not-a-date` のような不正値では `clean_fields()` がコーシングに失敗して `due_date` が文字列のまま残り、続く `Ticket.clean()` の `str < date` 比較で **`TypeError`（＝`ValidationError` ではない）** が送出される。これは view 側の `except ValidationError` でも捕捉できず、過去日対応だけでは依然 500 になることを発見した（HTML/API 両層に存在）。
- **層別テストの観点**：検証 **ルール** はモデル層（`Ticket.clean()`）に一元化されており正しい。新設した runn API 層は同じルールに対し意味的に正しい **400** を期待値として書き下す。この「層ごとに期待値を厳密に書く」過程で、HTML 層だけが同じルールを 500 に取りこぼしていることが顕在化した。

## 7. 修正内容
- 修正ビルド：app-v0.5
- 修正概要（2点）：
  1. **view**：`ticket_change_due_date` の `full_clean()` を `try/except ValidationError` で囲み、失敗時は作成画面と同様に詳細画面を `error` 付きで再描画（HTTP 200）。テンプレート `tickets/detail.html` にエラー表示スロットを追加し、詳細コンテキストは `_detail_context()` に集約して `ticket_detail` と共有。
  2. **model**：`Ticket.clean()` を `isinstance(self.due_date, date)` でガードし、未コード化値での `TypeError` を防止（不正フォーマットは `clean_fields()` の `ValidationError` として正しく集約され、view/API ともに graceful になる）。これにより原因①②の両方を解消。
- API 側：`api.TicketDueView` は当初から `ValidationError` を捕捉して **400** を返す設計。model のガード追加で不正フォーマットも `ValidationError` 化され、API も 500 ではなく 400 になる（期待値は一意）。
- 既存データへの影響：なし（メソッドのみ変更／フィールド不変のためマイグレーション不要）。

## 8. リテスト・回帰結果
- HTML 回帰：**Auto-05**（admin が過去日を送信 → 500 ではなく詳細画面でエラー表示）を追加し Pass。
- API 回帰：runn `validation/due_date.yml`（過去日/不正値 → 400、未来日/空 → 200）が Pass。
- 全体回帰：再配分後の E2E（Auto-01/02/04/05）一括実行 → Pass。runn 10/10 runbook Pass。

## 9. 状態遷移
新規（runn API 層の期待値設計が検出） → 修正済（コミット：`app/tickets/views.py`, `app/tickets/templates/tickets/detail.html`） → 検証済（Auto-05 / runn due 系で確認）

## 10. 教訓
- **下層（API）で期待値を一意に書き下す作業そのものが、上層（HTML）の取りこぼしを炙り出すレビュー機会になった。** これはテストピラミッド最適化の副次的価値であり、「同じルールを別の層・別の表現（400 と graceful 200）で検証する」ことの実利を示す事例。
- **同種の処理（`full_clean()` による検証）は全経路で同じ防御（try/except）を施す**べき。create にあって due になかった非対称は、レビュー時のチェックリスト項目にすべき落とし穴。
