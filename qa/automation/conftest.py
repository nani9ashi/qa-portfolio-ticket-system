"""共通fixture（チケット管理アプリ E2E自動テスト用）.

- `base_url`: BASE_URL 環境変数で上書き可能（既定はローカル開発サーバー）。
- `login`: 任意ユーザーでログインする callable を返す。テスト本体側で `login("requester1")` のように呼ぶ。
- `evidence_dir`: テスト名ごとに `evidence/auto/<test_name>/` を用意して返す。
"""

import os
import pytest
from playwright.sync_api import Page

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEMO_PASSWORD = "pass1234"


@pytest.fixture(scope="session")
def base_url() -> str:
    """pytest-base-url の同名 session-scoped fixture を上書きする。

    BASE_URL 環境変数で指定可能。既定はローカル開発サーバー。
    """
    return os.getenv("BASE_URL", DEFAULT_BASE_URL)


@pytest.fixture
def login(page: Page, base_url: str):
    def _login(username: str, password: str = DEMO_PASSWORD) -> Page:
        page.goto(f"{base_url}/accounts/login/")
        page.locator("input[name='username']").fill(username)
        page.locator("input[name='password']").fill(password)
        page.get_by_role("button", name="Login").click()
        return page

    return _login


@pytest.fixture
def evidence_dir(request) -> str:
    test_name = request.node.name
    path = f"evidence/auto/{test_name}"
    os.makedirs(path, exist_ok=True)
    return path
