"""Auto-03: body 境界値（4001文字超過）の拒否確認.

要件 RQ-004 / 手動テスト TC-046 の自動化。
title は HTML側で `maxlength=80` のクライアント抑止があるが、body は textarea で
maxlength なし → サーバ側 `Ticket.full_clean()` の MaxLengthValidator で検証される
（`app/tickets/models.py:34`、`app/tickets/views.py:99-101`）。

期待挙動：
- 4001 文字の body で submit すると、URL は /tickets/new/ のままで、
  `<p style="color:red;">` のエラーメッセージが表示される（`create.html:5-7`）。
"""

from playwright.sync_api import expect


def test_body_exceeding_max_length_is_rejected(login, base_url, evidence_dir):
    page = login("requester1")
    page.goto(f"{base_url}/tickets/new/")

    page.locator("input[name='title']").fill("Boundary Test (body 4001)")
    page.locator("textarea[name='body']").fill("x" * 4001)

    page.get_by_role("button", name="Create").click()

    # 詳細画面へ遷移していないこと（バリデーションエラーで作成失敗）
    expect(page).to_have_url(f"{base_url}/tickets/new/")

    # 赤色のエラーメッセージが表示されていること
    error_locator = page.locator("p[style*='color:red']")
    expect(error_locator).to_be_visible()

    page.screenshot(path=f"{evidence_dir}/body_validation_error.png", full_page=True)
