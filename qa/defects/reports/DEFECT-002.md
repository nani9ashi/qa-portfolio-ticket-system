# DEFECT-002 本文（body）の最大長制約が実装で enforce されていない

## 基本情報
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
  - [Auto-03 修正前の意図しない作成成功（手元検証ログ）](#)
  - [Auto-03 修正後のスクリーンショット](../../automation/evidence/auto/test_body_exceeding_max_length_is_rejected[chromium]/body_validation_error.png)
- 備考：自動化シナリオ作成中に発見。手動テスト（TC-046）では未実施だったため検出されていなかった。

## 概要
Requester が新規チケット作成時に、body フィールドへ4001文字（max_length=4000 超過）を入力しても、サーバー側でバリデーションエラーが発生せず、チケットが正常に作成されてしまう。

## 前提（テストデータ）
- requester1 でログイン可能
- `/tickets/new/` の新規作成画面が表示できる

## 再現手順
1. requester1 でログインする
2. `/tickets/new/` を開く
3. title に任意の有効値を入力
4. body に 4001 文字（例：`"x" * 4001`）を入力
5. 「Create」ボタンをクリックする

## 期待結果
- 作成画面に留まり、`<p style="color:red;">` のエラーメッセージが表示される
- チケットは作成されない（DB に保存されない）

## 実際結果（修正前）
- チケットが作成され、詳細画面（例：`/tickets/9/`）へ遷移してしまう
- 作成された body は 4001 文字のまま（DB 上にも保存される）

## 影響範囲
- RQ-004（Must要件）の受入条件「4001文字以上は保存不可（エラー表示）」を満たしていない。
- DBレイヤ（SQLite）も TextField に対して長さ制約を作らないため、データ整合性の最終防衛線も失われている。
- 業務影響：実運用で長大な本文が紛れ込み、UI 表示の崩れ、ログサイズの肥大化、検索性能の劣化につながる可能性。

## 原因仮説（推測 → 確認済）
- Django の `TextField` は `CharField` と異なり、`max_length` 引数から自動で `MaxLengthValidator` を追加しない仕様。
- 元実装：`body = models.TextField(max_length=4000)`
- `max_length` は formfield 生成や SQLite スキーマ生成のヒントとしてのみ使われ、`Model.full_clean()` 経由のバリデーションでは作用しない。
- 確認手順：Django shell で `Ticket(body='x'*4001).full_clean()` を実行 → 例外が発生しないことを確認した。

## 修正方針 / 修正内容
- 修正ビルド：app-v0.4
- 修正概要：`Ticket.body` フィールドに **明示的に `MaxLengthValidator(4000)` を追加**して、`full_clean()` 時に検証されるようにした。

```python
# app/tickets/models.py（差分）
from django.core.validators import MaxLengthValidator
...
body = models.TextField(max_length=4000, validators=[MaxLengthValidator(4000)])
```

- 補足：CharField を使う選択肢もあるが、本文は改行を含む長文想定のため TextField を維持し、validator のみ追加する方針とした。
- 既存データへの影響：既に4001文字以上の body を持つチケットがある場合、DBレベルでは引き続き保持される（validator は新規/更新時に発火）。今回はテストデータのみなので追加マイグレーションは不要。

## 回帰観点
- 修正後、Auto-03（test_scenario_03_validation.py）を実行して Pass となること。
- 影響が疑われる範囲：チケット更新フロー（現状はステータス変更のみで body 編集は不可なので影響なし）。
- title 側（CharField）は元から `MaxLengthValidator` が自動付与されるため影響なし（Auto-01 で確認済）。

## リテスト／回帰結果
- ローカル：Auto-03 を 2026-05-10 に再実行 → Pass。スクショは `evidence/auto/test_body_exceeding_max_length_is_rejected[chromium]/body_validation_error.png`。
- 全体回帰：Auto-01〜04 を一括実行 → 4/4 Pass。

## 状態遷移
新規（起票・自動化が検出） → 修正済（コミット予定：app/tickets/models.py） → 検証済（Auto-03 全 Pass で確認）

## 教訓 / メモ
- **手動テストでは未着手だった TC-046 を自動化に昇格させた結果、要件と実装の乖離を検出**できた。手動から自動への昇格が「設計のレビュー機会」になることを実感した事例。
- Django の `TextField` と `CharField` の振る舞い差は実装者側の落とし穴。**今後 TextField を使う場合は明示 validator を必ず付ける**ことをチーム ルールにすべき。
