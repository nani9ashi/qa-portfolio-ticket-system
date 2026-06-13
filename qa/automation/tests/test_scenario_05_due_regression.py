"""Auto-05: 期限に過去日を入力しても 500 にならず graceful にエラー表示される.

DEFECT-003 の回帰テスト（HTML 層）。`ticket_change_due_date` が `full_clean()` を
try/except で囲っておらず、過去日入力で 500（未処理例外）になっていた不具合の再発防止。
（同じルールの API 期待値=400 は runn `validation/due_date.yml` でカバー。層別に検証する。）

期待挙動：
- admin1 でログインして任意のチケット詳細を開き、Due date に過去日を送信すると、
  - 500（Django デバッグ画面）にならない
  - 詳細画面に `<p style="color:red;">` のエラーメッセージが表示される（graceful 拒否）
"""

from playwright.sync_api import expect

PAST_DATE = "2000-01-01"


def test_past_due_date_is_rejected_gracefully(login, base_url, evidence_dir):
    page = login("admin1")
    page.goto(f"{base_url}/tickets/1/")

    # Due date (Admin only) フォームに過去日を入力して送信する
    page.locator("input[name='due_date']").fill(PAST_DATE)
    page.locator("form[action*='/due/']").get_by_role("button", name="Save").click()

    # 500 ではなく、詳細画面で赤色のエラーメッセージが表示されること（DEFECT-003 修正後）
    error_locator = page.locator("p[style*='color:red']")
    expect(error_locator).to_be_visible()

    # Django のデバッグ 500 ページ特有の文言が出ていないこと（念のための保険）
    assert "Traceback" not in page.content()

    page.screenshot(path=f"{evidence_dir}/due_past_error.png", full_page=True)
