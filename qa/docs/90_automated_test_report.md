# 自動テスト実施レポート - チケット管理アプリ

- 文書ID：ATR-TICKET-001
- 版：v1.0
- ステータス：Approved
- 最終更新日：2026-07-23
- 作成者：仁後慎太郎
- 対象：チケット管理アプリ（Web, Django + SQLite）
- 関連：
  - [テスト完了レポート](60_test_completion_report.md)（手動テストフェーズの完了記録）
  - [テスト層戦略](80_test_layer_strategy.md)（層配分の根拠）
  - [API README](../api/README.md)（runn runbook 一覧）

CIパイプラインの品質ゲートは **3層** で構成する：**(1) pytest による単体層**（policy.py の認可述語・状態遷移、53件）、**(2) runn による API/インテグレーション層**（認可・状態遷移・入力検証の組合せ網羅、10 runbook / 102 step）、**(3) Playwright による E2E 層**（代表4シナリオ）。組合せ網羅は下層（単体・API）に置き、E2E は代表シナリオに絞る（配分の根拠は [80](80_test_layer_strategy.md)、ここに至る経緯は §8）。本書の Auto-0x は E2E 層、API-x は runn 層を指す。

## 1. 自動化スコープと選定理由
代表的な業務フローと、QAリスク観点で重みのある領域（IDOR・境界値・RBAC）をバランスよくカバーすることで、CIで「動く仕様書」として機能させることを意図している。

| ID | 対応TC | カテゴリ | 自動化シナリオ名 | 検証内容（Assertion） |
| :--- | :--- | :--- | :--- | :--- |
| **Auto-01** | TC-032 & TC-001 | ハッピーパス | Requesterによるチケット作成と確認 | ログイン成功／新規チケットDB書き込み／詳細画面での入力値（Title/Body）完全一致 |
| **Auto-02** | TC-002（RQ-015） | セキュリティ（認可スモーク） | Requesterは他人チケットURLを直叩きしても閲覧不可（IDOR回帰） | 他人チケット詳細URLが 403 を返す／本文がDOMに含まれない |
| **Auto-04** | TC-007（RQ-029） | 認可（UI抑止） | 非担当 Agent はステータス変更UIを操作できない | "Not allowed to change status." が可視／`select[name='status']` が DOM に不在（サーバ側認可は API-B3 へ移設） |
| **Auto-05** | TC-036（RQ-006）/ DEFECT-003 | 回帰（実欠陥） | 期限に過去日を入力しても 500 にならず graceful にエラー表示 | 詳細画面で赤エラーが可視／Traceback 非表示（API 期待値=400 は API-C2） |

## 2. runn API/インテグレーションテスト層

組合せが爆発する認可・状態遷移・入力検証は、**高速・決定的な API 層で網羅する**（[80](80_test_layer_strategy.md)）。

**規模**：10 runbook / 102 step（[API README](../api/README.md)）。

| 区分 | runbook | 主な検証（一意な期待値） |
| :--- | :--- | :--- |
| **API-A** 認可+IDOR | idor / unauthenticated / view_authorization / create_authorization / assign_due_authorization | IDOR=403（DEFECT-001 の API 回帰）／未認証=401／一覧スコープ／作成は Requester のみ／割当・期限は Admin のみ |
| **API-B** 状態遷移 | valid_edges / invalid_transitions / role_constraints | 許可6エッジ=200＋遷移後状態／禁止エッジ=409／不正値=400／R1-R6（デシジョンテーブル） |
| **API-C** 入力検証 | title_body_boundary / due_date | title(80)/body(4000) の4点境界／過去日・不正値=400 |

**単一ソースの確認（実施済み）**：`INTENTIONAL_BUG_IDOR=True` で単体・API-A(idor)・Auto-02 が同一原因で同時に失敗することを確認した（設計原理は [80 §5](80_test_layer_strategy.md#5-単一ソース)、実演手順は §4）。

**実行結果**：runn 10/10 scenario Pass（`INTENTIONAL_BUG_IDOR=False` 既定）。E2E 4/4 Pass。CI で Unit／E2E／API の3ジョブを毎 push 並列実行。

**DEFECT-003（API 層が炙り出した実欠陥）**：API の期待値（過去日 → 400）を厳密に書き下す過程で、HTML の期限変更が過去日で 500 になる不具合を発見。起票 → 修正（view の try/except＋model の型ガード）→ 回帰（Auto-05／API-C2）まで完了。**下層で期待値を一意に書く作業そのものが、上層の取りこぼしを検出するレビュー機会になった**事例（DEFECT-001/002 に続く3例目）。

## 3. 実装の工夫（Engineering Highlights）
- **セレクタの堅牢性**：UI変更に弱いラベル依存（`getByLabel`）を避け、Djangoフォームの不変属性である `name` 属性（`input[name='title']`等）を指定することで、テストの保守性を高めている。
- **共通fixtureの整備**：`qa/automation/conftest.py` に `login` / `base_url` / `evidence_dir` fixtureを集約し、シナリオ追加時のボイラープレートを最小化（4シナリオで重複コードがほぼゼロ）。
- **環境依存の排除**：BASE_URL を環境変数化（既定はローカルサーバー）。CI／ローカル／別ポートでの実行を1コマンドで切替え可能に。
- **証跡の構造化**：テスト名ごとに `evidence/auto/<test_name>/` のサブディレクトリ自動生成。スクショの帰属が明確化。
- **責務分離の体現**：title はクライアント抑止（`maxlength=80`）、body はサーバ側バリデーション、と異なる検証層を明示（境界値の自動検証は現在 runn API-C が担う）。

## 4. 検出能力の実演手順（IDOR回帰）
Auto-02 は **意図的に失敗させることが可能** で、QAテストの「検出能力」自体を見せる材料として用意している。

```powershell
# settings.py の INTENTIONAL_BUG_IDOR を True に切替後、サーバー再起動
python -m pytest automation/tests/test_scenario_02_idor.py
# 期待: Auto-02 が FAIL（403 期待が 200 で返るため）

# 確認後、必ず False に戻す
```

## 5. 自動化が検出した実バグ：DEFECT-002（body max_length の未実装）

Auto-03 を実装してローカル実行した際、**事前想定では Pass するはず** のテストが FAIL した。

- 想定：body 4001文字は `Ticket.full_clean()` の `MaxLengthValidator` で拒否される（要件 RQ-004）
- 実際：チケットが正常に作成され、詳細画面へ遷移した（DBにも保存）

調査の結果、**Django の `TextField` は `CharField` と異なり、`max_length` 引数から自動で `MaxLengthValidator` を追加しない仕様** であることが原因と判明。要件と実装の乖離（実装側のバグ）と結論付け、[DEFECT-002](../defects/reports/DEFECT-002.md) として起票・修正・回帰の1サイクルを実施した。

**修正内容：** `app/tickets/models.py` の `body` フィールドに明示的に `MaxLengthValidator(4000)` を追加。修正後、Auto-03 を再実行 → Pass を確認。

**学び：**
- **手動TC（TC-046）を自動化に昇格させるプロセスそれ自体が、要件と実装の整合性を再点検する機会** になった。
- 「全Pass前提で書いた自動テストが意外な FAIL を返したとき、慌てず原因を追跡し、結果としてバグを正規プロセスに乗せられる」ことを実演できた事例（DEFECT-001 の IDOR と並ぶ「QA→欠陥→修正→回帰」の2サイクル目）。

## 6. 実行結果と導入効果
GitHub Actionsを用いたCI環境におけるテスト実行結果、および導入による品質改善効果は以下の通り。

- **テスト成功率**：**100%**（4/4 Pass、`INTENTIONAL_BUG_IDOR=False` 既定状態、DEFECT-002 修正後）。
- **実行効率の向上**：手動実施で約12分（4シナリオ × 約180秒）に対し、自動実施でローカル実測 約3〜4秒（fixture共有・並列なし）。**約99%のリードタイム短縮**となり、カバー範囲は1→4本に拡大。
- **品質ゲートの構築**：CI で **単体 53件＋runn 10 runbook＋E2E 4シナリオ** を毎 push 3ジョブ並列で必須化。認可（IDOR/RBAC）・状態遷移・入力境界を多層で自動回帰検知。
- **リスク低減**：DEFECT-001（IDOR）の再発を Auto-02（E2E）＋API-A（runn/idor）、DEFECT-002（body長制約）を API-C（runn/title_body_boundary）、DEFECT-003（期限500）を Auto-05＋API-C（due_date）が即時検知する体制を構築。

## 7. 今後の拡張計画（Backlog）
- **ページオブジェクト（POM）パターンの導入**：E2E シナリオが増えた段階で検討。
- **ブラウザmatrix**：Firefox / WebKit 追加。
- **並列実行**：runn の `--concurrent`、E2E の `pytest-xdist`。

## 8. 自動化の変遷（経緯）

本節までの記述は現在の姿を示す。ここに至る変遷は以下のとおり。

- **v1.1（2026-05-10）**：E2E 自動化を導入（Auto-01〜04）。Auto-03（本文境界）の実装過程で DEFECT-002 を検出（§5）。
- **v1.2（2026-06-13）**：runn API/インテグレーション層を新設し、テストピラミッドを最適化。組合せ網羅を E2E から API 層へ再配分。旧 Backlog の「直叩き API テスト」はこれにより実現（CSRF 不要の Token 認証 API）。
- **v1.3（2026-07-23）**：pytest 単体層（53件）を新設し3層構成が完成。CI を Unit／E2E／API の3ジョブ並列に拡張。

**E2E 再配分（before / after）**：

| シナリオ | before | after |
| :--- | :--- | :--- |
| Auto-01 ハッピーパス | E2E | **KEEP**（E2E） |
| Auto-02 IDOR | E2E | **KEEP**（認可スモーク。組合せ IDOR は API-A へ） |
| Auto-03 本文境界 | E2E | **API層へ移設し削除**（API-C・4点境界へ拡張） |
| Auto-04 非担当Agent | E2E | **KEEP**（UI 抑止のみ。サーバ側認可は API-B3 へ） |
| Auto-05 期限回帰 | （無） | **新規**（DEFECT-003 の HTML 回帰） |

