# テスト完了レポート - チケット管理アプリ

- 文書ID：TCR-TICKET-001
- 版：v1.2
- ステータス：Approved
- 最終更新日：2026-06-13
- 作成者：仁後慎太郎
- 対象：チケット管理アプリ（Web, Django + SQLite）
- 関連：
  - [テスト計画書](10_test_plan.md)
  - [テスト条件](20_test_conditions.md)
  - [要件とテストのトレーサビリティ](70_requirements_test_traceability.md)
  - [テストケース](../testcases/testcases.csv)
  - [テスト結果](../results/test_results.csv)
  - [欠陥ログ](../defects/defect_log.csv)

## 1. サマリ

本レポートは、テスト実行の結果概要（定量/定性）と、残存リスク・今後の課題をまとめる。

- 対象期間：2026-01-13 〜 2026-02-12
- 実行環境：Win11 / Chrome（[テスト結果](../results/test_results.csv)の実行環境列を正とする）
- 実行ビルド：
  - `app-defect-idor`（意図的欠陥の再現）
  - `app-v0.3`
  - `app-v0.3.1`（マイナーアップデート）

結論：現行テストセット（TC-001〜TC-044）の実行が完了し、重大欠陥（Critical/High）の未解決はゼロである。一方で、要件カバレッジ上の未カバー/一部カバー要件が残っており、Backlogとして整理済み（70参照）。

## 2. 実施範囲

### 2.1 実施した主要領域
- 権限・認可（参照/更新、直接アクセス/直接操作の拒否を含む）
- 状態遷移（許可遷移・禁止遷移、禁止遷移の拒否）
- 入力検証（必須、境界値、添付制約、期限）
- 一覧・検索・フィルタ
- 履歴/監査ログ（表示、操作種別の識別）

### 2.2 非対象（本レポートでは扱わない）
- 負荷・性能（定量的な性能評価）
- 専門的な脆弱性診断（侵入テスト等）
- 自動テスト（CI上のE2E実行）：本レポートの定量集計対象外。詳細は §11 を参照。

## 3. 結果概要（定量）

[テスト結果](../results/test_results.csv)からの集計（TR-0001〜TR-0046）。

- 実行件数：46
- 合格（Pass）：44
- 不合格（Fail）：2
- 実行不可（Blocked）：0

補足：
- 不合格2件（TR-0001/TR-0002）は **意図的欠陥ビルド（app-defect-idor）** における再現結果。
- 同一観点は回帰で合格確認済み（TR-0003/TR-0004、`app-v0.3`）。

## 4. 終了基準の達成状況

[テスト計画書](10_test_plan.md)の終了基準に沿って、以下を確認した。

### (1) 実行完了（現行テストセット）
- [x] 現行テストセット（TC-001〜TC-044）の実行が完了している（結果が [テスト結果](../results/test_results.csv) に記録済み）
- [x] 証跡（スクショ等）が記録され、TRから追跡できる（[テスト結果](../results/test_results.csv) の証跡列）

### (2) 最優先リスク（R-01〜R-02）の評価完了
- [x] **R-01（認可/IDOR）**の代表ケースを実行済み  
  （例：**TC-001/TC-002/TC-003/TC-010/TC-012/TC-014/TC-007/TC-008**）
- [x] **R-02（状態遷移/制約）**の代表ケースを実行済み  
  - 許可遷移（例：**TC-021/TC-022/TC-023/TC-025/TC-027/TC-030**）  
  - 禁止遷移（例：**TC-019/TC-020/TC-024/TC-026/TC-028/TC-031**）  
  - 直接操作での禁止遷移（例：**TC-029**）


### (3) 欠陥の収束（重大欠陥）
- [x] 未解決の重大欠陥（Critical/High）がゼロ  
  - [DEFECT-001](../defects/reports/DEFECT-001.md) は「検証済」（修正確認まで完了）

### (4) 要件カバレッジの説明責任（未カバーを根拠付きで扱う）
- [x] [要件とテストのトレーサビリティ](70_requirements_test_traceability.md)
にて、未カバー/一部カバーを A/B/C で分類している
- [x] Must/Should の扱い（採用/スコープ外/要件明確化）がBacklogで追跡できる

### (5) 完了レポートへの明示
- [x] 本レポートに実行結果サマリ／欠陥状況／残存リスク（Backlog含む）を記載した

## 5. 要件カバレッジ（70の集計に基づく）

[要件とテストのトレーサビリティ](70_requirements_test_traceability.md)
 の集計（全42件）。

- カバー：37件
- 一部カバー：3件
- 未カバー：2件

### Must / Should の内訳
- Must：39件（カバー35 / 一部3 / 未カバー1）
- Should：3件（カバー2 / 一部0 / 未カバー1）

未カバー要件（[トレーサビリティ](70_requirements_test_traceability.md)より）：
- Must：RQ-024
- Should：RQ-014（B 確定）

一部カバー要件（[トレーサビリティ](70_requirements_test_traceability.md)より）：
- RQ-002; RQ-008; RQ-029

> v1.2：runn API/インテグレーション層の新設に伴い、RQ-005/006/027/028/031/032 をカバー化（カバレッジ集計は [70 v1.4](70_requirements_test_traceability.md) を正とする）。

## 6. 主要な欠陥と状況（定性）

[欠陥ログ](../defects/defect_log.csv)を参照。

- DEFECT-001：依頼者が他人チケット詳細を参照できる（Severity：Critical / Priority：High）  
  - 状況：意図的欠陥ビルドで再現（TR-0001/TR-0002）→ 修正後ビルドで回帰合格（TR-0003/TR-0004）→ 欠陥状態：検証済
- DEFECT-002：本文(body)の最大長制約が実装でenforceされていない（Severity：High / Priority：High、v1.1で追記）
  - 状況：自動化シナリオ Auto-03（TC-046 由来）の実装中に検出。`Ticket.body` フィールドへ明示的に `MaxLengthValidator(4000)` を追加することで修正。Auto-03 を再実行して合格 → 欠陥状態：検証済。詳細は §11.4 と [DEFECT-002](../defects/reports/DEFECT-002.md) を参照。
- DEFECT-003：期限変更で過去日入力時に 500 エラー（Severity：Medium / Priority：Medium、v1.2で追記）
  - 状況：**runn API 層の期待値設計（過去日 → 400）を書き下す過程で検出**した HTML 層の不具合。`ticket_change_due_date` が `full_clean()` を try/except 外で呼び（過去日で 500）、加えて `Ticket.clean()` が未コード化値で `TypeError`（不正フォーマットで 500）。view を try/except 化＋model を `isinstance` ガードで修正し、**Auto-05（HTML 回帰）** と runn `validation/due_date.yml`（API 400）で回帰確認 → 欠陥状態：検証済。詳細は §11.7 と [DEFECT-003](../defects/reports/DEFECT-003.md) を参照。

## 7. 残存リスク / 未完了事項（Backlogの扱い）

Backlog（A/B/C分類）の正本は [70_requirements_test_traceability.md §8](70_requirements_test_traceability.md#8-backlog未カバー一部の解消候補)。本節では集計と最重要3件のみ抜粋する。

- 未カバー：5件（Must 3 / Should 2）／ 一部カバー：7件
- 分類内訳：A（追加してカバー）が大半、B（スコープ外）2件、C（要件を修正・明確化）3件
- A：追加してカバー／B：スコープ外として明記／C：要件を修正・明確化

次サイクルで優先対応する3件：
- **RQ-024（未カバー・A）**：Admin が任意チケットへコメント追加できることを TC 追加
- **RQ-006（一部・C）**：due_date の入力主体（Requester/Admin）整合を要件レベルで確定
- **RQ-002（一部・C→A）**：監査ログ “全操作” の範囲定義 → 不足 TC 追加

完全な内訳・各要件の方針・既存IDは 70 を参照。

## 8. バージョンまたぎ実行の説明

今回の実行は `app-v0.3` と `app-v0.3.1` を跨いで実施した。
理由は、`v0.3.1` が **セキュリティ関連のマイナーアップデート**であり、要件・期待結果に影響する機能仕様変更がない前提で、テスト実行を継続したため。

運用ルール（今回の整理）：
- テスト結果は [テスト結果](../results/test_results.csv)の build 列で追跡可能であるため、跨ぎ実行を許容する
- 仕様影響が疑われる変更が入った場合は、影響範囲の代表ケースを回帰として追加実行する

## 9. 得られた教訓

- 認可や禁止遷移は、UI上の制御だけでなく **サーバ側（直接操作）** で拒否されることを確認すると説得力が上がる
- 要件カバレッジを「未カバー＝悪」とせず、A/B/C分類で **説明可能な状態** にしておくと、完了判定と改善活動が両立できる
- テスト結果（TR）と欠陥ログ（DEFECT）を分離すると、再現→修正→回帰の流れが追跡しやすい

## 10. 次のアクション（優先順）

### 完了済み（v1.1, 2026-05-10）
- [x] **RQ-004（一部）→ カバー化**：TC-045/TC-046 追加 → Auto-03 として自動化 → DEFECT-002（body max_length 未実装）を検出・修正・回帰まで完了。
- [x] **Auto-04 追加で RQ-029 のUI側面検証を強化**（TC-007 のUI側を自動化）。「更新」定義の整理は引き続きC扱いで継続課題。
- [x] **app/README.md §5 RBAC 表を実装・要件に合わせて修正**（Agent×（RQ-013 Must）、Admin×（RQ-014 Should、B 確定））。
- [x] **RQ-014（Should、Admin作成可）を B 確定（対象外）**：起票責務をRequesterに集約する設計判断。責務分離の徹底＋起票の真正性確保が理由。代理起票の需要が出た場合は『代理起票ロール』として別建てする想定。

### 継続課題
- [ ] 70のBacklog（A/B/C）を更新し、未カバー/一部カバーの解消方針を確定する
- [ ] （A群）必要に応じてTC追加（RQ-024/RQ-028/RQ-032/RQ-005/RQ-008 など）
- [ ] （C群）要件と実装/TCの不一致を解消（RQ-006, RQ-029, RQ-002）

## 11. 付記：テスト自動化の実施結果 (Automated Test Summary)

本プロジェクトでは、CIパイプラインの品質ゲートを **2層** で構成している：**(1) runn による API/インテグレーション層**（認可・状態遷移・入力検証の組合せ網羅）と、**(2) Playwright による E2E 層**（代表シナリオ）。v1.2 でテストピラミッド最適化を実施し、組合せ網羅を E2E から API 層へ再配分した（判断は [80](80_test_layer_strategy.md)）。本節の Auto-0x は E2E 層、API-x は runn 層を指す。

### 11.1 自動化スコープと選定理由
代表的な業務フローと、QAリスク観点で重みのある領域（IDOR・境界値・RBAC）をバランスよくカバーすることで、CIで「動く仕様書」として機能させることを意図している。

| ID | 対応TC | カテゴリ | 自動化シナリオ名 | 検証内容（Assertion） |
| :--- | :--- | :--- | :--- | :--- |
| **Auto-01** | TC-032 & TC-001 | ハッピーパス | Requesterによるチケット作成と確認 | ログイン成功／新規チケットDB書き込み／詳細画面での入力値（Title/Body）完全一致 |
| **Auto-02** | TC-002（RQ-015） | セキュリティ（認可スモーク） | Requesterは他人チケットURLを直叩きしても閲覧不可（IDOR回帰） | 他人チケット詳細URLが 403 を返す／本文がDOMに含まれない |
| **Auto-04** | TC-007（RQ-029） | 認可（UI抑止） | 非担当 Agent はステータス変更UIを操作できない | "Not allowed to change status." が可視／`select[name='status']` が DOM に不在（サーバ側認可は API-B3 へ移設） |
| **Auto-05** | TC-036（RQ-006）/ DEFECT-003 | 回帰（実欠陥） | 期限に過去日を入力しても 500 にならず graceful にエラー表示 | 詳細画面で赤エラーが可視／Traceback 非表示（API 期待値=400 は API-C2） |

### 11.2 実装の工夫（Engineering Highlights）
- **セレクタの堅牢性**：UI変更に弱いラベル依存（`getByLabel`）を避け、Djangoフォームの不変属性である `name` 属性（`input[name='title']`等）を指定することで、テストの保守性を高めている。
- **共通fixtureの整備**：`qa/automation/conftest.py` に `login` / `base_url` / `evidence_dir` fixtureを集約し、シナリオ追加時のボイラープレートを最小化（4シナリオで重複コードがほぼゼロ）。
- **環境依存の排除**：BASE_URL を環境変数化（既定はローカルサーバー）。CI／ローカル／別ポートでの実行を1コマンドで切替え可能に。
- **証跡の構造化**：テスト名ごとに `evidence/auto/<test_name>/` のサブディレクトリ自動生成。スクショの帰属が明確化。
- **責務分離の体現**：title はクライアント抑止（`maxlength=80`）、body はサーバ側バリデーション、と異なる検証層をテストで明示（Auto-03）。

### 11.3 検出能力の実演手順（IDOR回帰）
Auto-02 は **意図的に失敗させることが可能** で、QAテストの「検出能力」自体を見せる材料として用意している。

```powershell
# settings.py の INTENTIONAL_BUG_IDOR を True に切替後、サーバー再起動
python -m pytest automation/tests/test_scenario_02_idor.py
# 期待: Auto-02 が FAIL（403 期待が 200 で返るため）

# 確認後、必ず False に戻す
```

### 11.4 自動化が検出した実バグ：DEFECT-002（body max_length の未実装）

Auto-03 を実装してローカル実行した際、**事前想定では Pass するはず** のテストが FAIL した。

- 想定：body 4001文字は `Ticket.full_clean()` の `MaxLengthValidator` で拒否される（要件 RQ-004）
- 実際：チケットが正常に作成され、詳細画面へ遷移した（DBにも保存）

調査の結果、**Django の `TextField` は `CharField` と異なり、`max_length` 引数から自動で `MaxLengthValidator` を追加しない仕様** であることが原因と判明。要件と実装の乖離（実装側のバグ）と結論付け、[DEFECT-002](../defects/reports/DEFECT-002.md) として起票・修正・回帰の1サイクルを実施した。

**修正内容：** `app/tickets/models.py` の `body` フィールドに明示的に `MaxLengthValidator(4000)` を追加。修正後、Auto-03 を再実行 → Pass を確認。

**学び：**
- **手動TC（TC-046）を自動化に昇格させるプロセスそれ自体が、要件と実装の整合性を再点検する機会** になった。
- 「全Pass前提で書いた自動テストが意外な FAIL を返したとき、慌てず原因を追跡し、結果としてバグを正規プロセスに乗せられる」ことを実演できた事例（DEFECT-001 の IDOR と並ぶ「QA→欠陥→修正→回帰」の2サイクル目）。

### 11.5 実行結果と導入効果
GitHub Actionsを用いたCI環境におけるテスト実行結果、および導入による品質改善効果は以下の通り。

- **テスト成功率**：**100%**（4/4 Pass、`INTENTIONAL_BUG_IDOR=False` 既定状態、DEFECT-002 修正後）。
- **実行効率の向上**：手動実施で約12分（4シナリオ × 約180秒）に対し、自動実施でローカル実測 約3〜4秒（fixture共有・並列なし）。**約99%のリードタイム短縮**となり、カバー範囲は1→4本に拡大。
- **品質ゲートの構築**：CI上で4シナリオを「マージの必須条件」化。セキュリティ／バリデーション／認可の3観点で自動的に回帰検知。
- **リスク低減**：DEFECT-001（IDOR）／DEFECT-002（body長制約） の再発を Auto-02／Auto-03 が即時検知する体制を構築。

### 11.6 今後の拡張計画（Backlog）
- ~~**直叩きAPIテスト**：CSRF処理ヘルパーを整備し、サーバ側を自動化~~ → **✓ v1.2 で実現**（runn API 層・CSRF 不要の Token 認証 API。§11.7）。
- **ページオブジェクト（POM）パターンの導入**：E2E シナリオが増えた段階で検討。
- **ブラウザmatrix**：Firefox / WebKit 追加。
- **並列実行**：runn の `--concurrent`、E2E の `pytest-xdist`。

### 11.7 runn API/インテグレーションテスト層（新設・v1.2）

テストピラミッド最適化（[80](80_test_layer_strategy.md)）に基づき、組合せが爆発する認可・状態遷移・入力検証を **高速・決定的な API 層へ押し下げた**。

**規模**：10 runbook / 102 step（[API README](../api/README.md)）。

| 区分 | runbook | 主な検証（一意な期待値） |
| :--- | :--- | :--- |
| **API-A** 認可+IDOR | idor / unauthenticated / view_authorization / create_authorization / assign_due_authorization | IDOR=403（DEFECT-001 の API 回帰）／未認証=401／一覧スコープ／作成は Requester のみ／割当・期限は Admin のみ |
| **API-B** 状態遷移 | valid_edges / invalid_transitions / role_constraints | 許可6エッジ=200＋遷移後状態／禁止エッジ=409／不正値=400／R1-R6（デシジョンテーブル） |
| **API-C** 入力検証 | title_body_boundary / due_date | title(80)/body(4000) の4点境界／過去日・不正値=400 |

**E2E 再配分（before / after）**：

| シナリオ | before | after |
| :--- | :--- | :--- |
| Auto-01 ハッピーパス | E2E | **KEEP**（E2E） |
| Auto-02 IDOR | E2E | **KEEP**（認可スモーク。組合せ IDOR は API-A へ） |
| Auto-03 本文境界 | E2E | **API層へ移設し削除**（API-C・4点境界へ拡張） |
| Auto-04 非担当Agent | E2E | **KEEP**（UI 抑止のみ。サーバ側認可は API-B3 へ） |
| Auto-05 期限回帰 | （無） | **新規**（DEFECT-003 の HTML 回帰） |

**単一ソースの確認**：認可は [policy.py](../../app/tickets/policy.py) を HTML/API で共有。`INTENTIONAL_BUG_IDOR=True` にすると **API-A(idor) と Auto-02 が同時に・同一原因で失敗**する（§11.3 の検出能力実演を両層へ拡張）。

**実行結果**：runn 10/10 scenario Pass（`INTENTIONAL_BUG_IDOR=False` 既定）。E2E 4/4 Pass。CI で `e2e-test` と `api-test` を毎 push 並列実行。

**DEFECT-003（API 層が炙り出した実欠陥）**：API の期待値（過去日 → 400）を厳密に書き下す過程で、HTML の期限変更が過去日で 500 になる不具合を発見。起票 → 修正（view の try/except＋model の型ガード）→ 回帰（Auto-05／API-C2）まで完了。**下層で期待値を一意に書く作業そのものが、上層の取りこぼしを検出するレビュー機会になった**事例（DEFECT-001/002 に続く3例目）。