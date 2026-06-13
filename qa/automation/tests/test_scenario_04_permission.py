"""Auto-04: 非担当 Agent はステータス変更UIを操作できない.

要件 RQ-029 / 手動テスト TC-007（UI 側面）の自動化。
ディシジョンテーブル（30_test_design.md §3.2 R4）：Agent でも担当が他人なら禁止。

期待挙動：
- agent2 でログインして Ticket #2 詳細を開くと、
  - 閲覧自体は可能（Agent は全チケット閲覧可、RQ-016）
  - "Not allowed to change status." が表示される（`detail.html:67-68`）
  - status 変更用の `<select name='status'>` が DOM に存在しない
- 「見えるが触れない」を UI 側面で担保する（本テストの責務は UI 抑止のみに限定）。
- サーバ側の認可（非担当 Agent のステータス変更 → 403）は runn `transitions/role_constraints.yml`（R4）
  でカバー。本拡張で「直叩き POST は CSRF コストにより自動化スコープ外」だった旧制約を API 層で解消した。
  （テストピラミッド再配分：組合せ認可は API 層へ、UI 抑止のみ E2E に残す）
"""

from playwright.sync_api import expect


def test_non_assigned_agent_cannot_see_status_change_ui(login, base_url, evidence_dir):
    page = login("agent2")  # agent2 は Ticket #2 の担当者ではない（担当は agent1）

    page.goto(f"{base_url}/tickets/2/")

    # 閲覧自体は可能：Ticket #2 の title が表示されている
    title_cell = page.locator("tr", has_text="Title").locator("td")
    expect(title_cell).to_have_text("Invoice CSV export wrong header")

    # しかしステータス変更操作はUI上できない
    expect(page.get_by_text("Not allowed to change status.")).to_be_visible()
    expect(page.locator("select[name='status']")).to_have_count(0)

    page.screenshot(path=f"{evidence_dir}/agent_no_status_ui.png", full_page=True)
