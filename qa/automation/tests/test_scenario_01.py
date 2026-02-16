import pytest
from playwright.sync_api import Page, expect
import os

# 環境設定
BASE_URL = "http://127.0.0.1:8000"
USER_ID = "requester1"
PASSWORD = "pass1234"

def test_create_ticket_and_verify(page: Page):
    """
    TC-024 & TC-001 自動化シナリオ:
    依頼者(Requester)としてログインし、新規チケットを作成して、詳細画面で内容を確認する。
    """
    
    # ----------------------------------------
    # Step 1: ログイン
    # ----------------------------------------
    page.goto(f"{BASE_URL}/accounts/login/")

    # ラベルではなく、Djangoが生成するinputタグのname属性で確実に指定
    page.locator("input[name='username']").fill(USER_ID)
    page.locator("input[name='password']").fill(PASSWORD)
    
    page.get_by_role("button", name="Login").click()
    
    # ログイン成功（一覧画面遷移）の確認
    expect(page).to_have_url(f"{BASE_URL}/")

    # ----------------------------------------
    # Step 2: チケット作成 (TC-024)
    # ----------------------------------------
    page.goto(f"{BASE_URL}/tickets/new/")
    
    test_title = "AutoTest: 正常系動作確認"
    test_body = "Playwrightによる自動作成テストです。\n正常に登録されることを確認します。"
    
    # 安定性のためname属性で指定
    page.locator("input[name='title']").fill(test_title)
    page.locator("textarea[name='body']").fill(test_body)
    
    page.get_by_role("button", name="Create").click()

    # ----------------------------------------
    # Step 3: 作成結果の確認 (TC-001)
    # ----------------------------------------
    # 詳細画面への遷移を確認
    expect(page.locator("h2")).to_contain_text("Ticket #")
    
    # タイトルの検証
    title_cell = page.locator("tr", has_text="Title").locator("td")
    expect(title_cell).to_have_text(test_title)
    
    # 本文の検証
    body_cell = page.locator("tr", has_text="Body").locator("pre")
    expect(body_cell).to_have_text(test_body)
    
# ----------------------------------------
    # Step 4: 証跡の保存
    # ----------------------------------------
    # "evidence/auto" フォルダに保存するように変更
    screenshot_path = "evidence/auto/test_scenario_01_success.png"
    
    # フォルダがなければ自動作成
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    
    page.screenshot(path=screenshot_path, full_page=True)