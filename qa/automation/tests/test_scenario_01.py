"""Auto-01: Requester による新規チケット作成 → 詳細画面で内容確認.

対応：TC-024（作成）＋ TC-001（自分のチケット参照）。
"""

from playwright.sync_api import expect


def test_create_ticket_and_verify(login, base_url, evidence_dir):
    page = login("requester1")
    expect(page).to_have_url(f"{base_url}/")

    page.goto(f"{base_url}/tickets/new/")

    test_title = "AutoTest: 正常系動作確認"
    test_body = (
        "Playwrightによる自動作成テストです。\n"
        "正常に登録されることを確認します。"
    )

    page.locator("input[name='title']").fill(test_title)
    page.locator("textarea[name='body']").fill(test_body)
    page.get_by_role("button", name="Create").click()

    expect(page.locator("h2")).to_contain_text("Ticket #")

    title_cell = page.locator("tr", has_text="Title").locator("td")
    expect(title_cell).to_have_text(test_title)

    body_cell = page.locator("tr", has_text="Body").locator("pre")
    expect(body_cell).to_have_text(test_body)

    page.screenshot(path=f"{evidence_dir}/test_scenario_01_success.png", full_page=True)
