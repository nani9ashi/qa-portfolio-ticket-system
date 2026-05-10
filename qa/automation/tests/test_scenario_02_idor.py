"""Auto-02: IDOR 回帰テスト（DEFECT-001 由来）.

要件 RQ-015 / 手動テスト TC-002 の自動化。
Requester が他人チケットの詳細URLを直接アクセスしても閲覧できないこと（403）を確認する。

実演メモ：
- `INTENTIONAL_BUG_IDOR=False`（既定）：本テストはPass（403で拒否される）。
- `INTENTIONAL_BUG_IDOR=True`：本テストはFail（200で他人チケットが見えてしまう）。
  → DEFECT-001 の検出能力を実演する手順として `60_test_completion_report.md §11` に記載。
"""


def test_requester_cannot_view_others_ticket_via_direct_url(login, base_url, page, evidence_dir):
    login("requester1")

    # Ticket #2 は requester2 所有 + agent1 割当 → requester1 は閲覧権限なし
    response = page.goto(f"{base_url}/tickets/2/")

    assert response is not None, "navigation response should not be None"
    assert response.status == 403, (
        f"expected 403 (forbidden) for cross-user access, got {response.status}"
    )

    # 念のため、Ticket #2 の本文が画面に出ていないことも確認
    body_text = page.content()
    assert "Column names mismatch spec." not in body_text, (
        "Ticket #2 body content must not be visible to requester1"
    )

    page.screenshot(path=f"{evidence_dir}/idor_blocked.png", full_page=True)
