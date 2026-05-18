# DEFECT-002 本文（body）の最大長制約が実装で enforce されていない

## 1. 基本情報
- 状態：検証済
- 重要度：High
- 優先度：High
- 発見日：2026-05-10
- 発見者：仁後慎太郎
- 検出環境：Win11/Chrome（ローカル）
- 検出ビルド：app-v0.4-pre（Auto-03 自動化シナリオ追加時）
- 関連テストケース：TC-046（Auto-03 として自動化）
- 関連要件：RQ-004（チケットのbodyは必須かつ最大4000文字）
- 証跡：
  - [Auto-03 修正後のスクリーンショット](../../automation/evidence/auto/test_body_exceeding_max_length_is_rejected[chromium]/body_validation_error.png)
- 備考：自動化シナリオ作成中に発見。手動テスト（TC-046）では未実施だったため検出されていなかった。

## 2. 概要
Requester が新規チケット作成時に、body フィールドへ4001文字（max_length=4000 超過）を入力しても、サーバー側でバリデーションエラーが発生せず、チケットが正常に作成されてしまう。

## 3. 前提（テストデータ）
- requester1 でログイン可能
- `/tickets/new/` の新規作成画面が表示できる

## 4. 再現手順
1. requester1 でログインする
2. `/tickets/new/` を開く
3. title に任意の有効値を入力
4. body に 4001 文字（例：`"x" * 4001`）を入力
5. 「Create」ボタンをクリックする

## 5. 期待結果 / 実際結果 / 影響範囲
- **期待**：作成画面に留まり、エラーメッセージが表示され、チケットは作成されない（DBにも保存されない）。
- **実際（修正前）**：チケットが作成され、詳細画面（例：`/tickets/9/`）へ遷移してしまう。body は 4001 文字のまま DB に保存される。
- **影響範囲**：RQ-004（Must要件）の受入条件を満たしていない。SQLite の TextField にも長さ制約がないため、データ整合性の最終防衛線も失われる。実運用では長大本文が UI 表示の崩れ、ログサイズ肥大化、検索性能の劣化につながる可能性。

## 6. 原因と修正方針
- **（確認済）原因**：Django の `TextField` は `CharField` と異なり、`max_length` 引数から自動で `MaxLengthValidator` を追加しない仕様。Django shell の `Ticket(body='x'*4001).full_clean()` で例外が出ないことを確認した。
- **修正方針**：`Ticket.body` フィールドに `validators=[MaxLengthValidator(4000)]` を明示追加し、`full_clean()` 時に検証されるようにする。本文の改行想定を維持するため CharField への変更は採用しない。

## 7. 修正内容
- 修正ビルド：app-v0.4
- 修正概要：`app/tickets/models.py` の `Ticket.body` に `MaxLengthValidator(4000)` を validators 引数で明示追加。実装差分はコミット参照。
- 既存データへの影響：validator は新規/更新時に発火するため、既に4001文字以上の body を持つチケットがある場合 DB レベルでは保持される。今回はテストデータのみのため追加マイグレーションは不要。

## 8. リテスト・回帰結果
- ローカル：Auto-03 を 2026-05-10 に再実行 → Pass。スクショは `evidence/auto/test_body_exceeding_max_length_is_rejected[chromium]/body_validation_error.png`。
- 全体回帰：Auto-01〜04 を一括実行 → 4/4 Pass。
- 関連確認：title 側（CharField）は元から MaxLengthValidator が自動付与されるため影響なし（Auto-01 で確認済）。

## 9. 状態遷移
新規（起票・自動化が検出） → 修正済（コミット：app/tickets/models.py） → 検証済（Auto-03 全 Pass で確認）

## 10. 教訓
- **手動テストでは未着手だった TC-046 を自動化に昇格させた結果、要件と実装の乖離を検出**できた。手動から自動への昇格が「設計のレビュー機会」になることを実感した事例。
- Django の `TextField` と `CharField` の振る舞い差は実装者側の落とし穴。**今後 TextField を使う場合は明示 validator を必ず付ける**ことをチームルールにすべき。
