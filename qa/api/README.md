# API / インテグレーションテスト層（runn）

[テストピラミッド最適化](../docs/80_test_layer_strategy.md)の判断に基づき、**認可（RBAC・IDOR）／状態遷移／入力検証の「組合せが爆発するロジック」を E2E から押し下げた**高速・決定的な層です。テスト対象は、テスト容易性のために最小追加した薄い JSON API（`/api/`・[app/tickets/api.py](../../app/tickets/api.py)）で、認可ルールは HTML ビューと同一の [policy.py](../../app/tickets/policy.py) を共有します。

> なぜ薄い API を足したのか／何を E2E に残したのかは [80_test_layer_strategy.md](../docs/80_test_layer_strategy.md) を参照。

## 構成

```text
qa/api/
└── runn/
    ├── rbac_idor/                 # (a) 認可マトリクス・IDOR・未認証
    │   ├── idor.yml               #   IDOR（DEFECT-001 の API 回帰。INTENTIONAL_BUG_IDOR で失敗実演）
    │   ├── unauthenticated.yml     #   トークン無し → 全エンドポイント 401
    │   ├── view_authorization.yml  #   詳細の可視性＋一覧のロール別スコープ（RQ-015/016/017）
    │   ├── create_authorization.yml#   作成は Requester のみ（RQ-012/013）
    │   └── assign_due_authorization.yml # 割当・期限は Admin のみ（RQ-007/027/028/030/031）
    ├── transitions/               # (b) 状態遷移
    │   ├── valid_edges.yml         #   許可6エッジ＋遷移後ステータス
    │   ├── invalid_transitions.yml #   禁止エッジ=409／enum外=400／Closed終端
    │   └── role_constraints.yml    #   デシジョンテーブル R1-R6（30_test_design §3.2 の API 実現）
    └── validation/                # (c) 入力検証・境界値
        ├── title_body_boundary.yml #   title(80)/body(4000) の 4点境界（RQ-003/004）
        └── due_date.yml            #   過去日/不正値=400（RQ-006 / DEFECT-003 の API 期待値）
```

- **10 runbook・約100ステップ**。期待値は HTTP ステータス（と一部 body）で**一意に**書き下す（① の決定的な世界）。
- HTML の全拒否 403 に対し、API は意味的に **401/403/400/409/404** へ写像（対応は [80_test_layer_strategy.md](../docs/80_test_layer_strategy.md) のコード表を参照）。

## 決定性・独立性

- 各 runbook は**自前でトークンを取得し、必要なチケットを API で生成**してから検証する（runbook 間で状態を共有しない）。固定 ID への依存がないため、実行順・既存データに影響されない。
- 必要な前提は**既知ユーザーのみ**（`requester1/2`, `agent1/2`, `admin1`／パスワード `pass1234`）。これは既存の `python manage.py seed_demo` が用意する。

## 実行方法

runn のバージョンは**再現性のため固定**（CI と一致）：`v1.9.2`。

```bash
# 1) runn を取得（例：Linux。Windows は *_windows_amd64.tar.gz）
curl -sL https://github.com/k1LoW/runn/releases/download/v1.9.2/runn_v1.9.2_linux_amd64.tar.gz | tar xz runn

# 2) アプリ＋DB を起動（E2E と同じ起動機構）
cd app
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000 &

# 3) runbook を実行（プロジェクトルートから）
runn run "qa/api/runn/**/*.yml"
```

- 対象は `http://127.0.0.1:8000`（CI と一致。各 runbook の `runners.req` に明示）。
- CI（GitHub Actions）では毎 push で `api-test` ジョブとして自動実行されます。詳細は [../../.github/workflows/ci.yml](../../.github/workflows/ci.yml)。

## 単一ソースの確認（IDOR 失敗実演）

`app/config/settings.py` の `INTENTIONAL_BUG_IDOR=True` にして再起動すると、`rbac_idor/idor.yml` の `idor_denied`（403 期待）が **200 を返して失敗**します。同じ `policy.can_view` を共有しているため、E2E の `Auto-02`（IDOR 回帰）も**同時に・同一原因で**失敗します。これが「テストが見ている対象は一つである」ことの担保です。
