"""認可・状態遷移ポリシー（単一ソース・オブ・トゥルース）.

HTML ビュー（``tickets.views``）と JSON API（``tickets.api``）の **両方** がこの
モジュールの述語を呼ぶ。認可・業務ルールをここに一本化することで、HTML と API は
「同じルールを別の表現（HTTP ステータス）で検証している」関係になる。

たとえば ``settings.INTENTIONAL_BUG_IDOR`` を立てると ``can_view`` が両経路で同時に
破綻し、E2E の IDOR 回帰（Auto-02）と API の IDOR テストが **同一原因で同時に失敗**
する。これが「テストが見ている対象は一つである」ことの担保になる。

本モジュールは ``HttpResponse`` や DRF ``Response`` を一切返さない純粋関数のみを持つ。
HTTP の関心（ステータスコードへの写像、POST 限定、404）は呼び出し側に残す。
"""

from django.conf import settings
from django.contrib.auth.models import User

from .models import Ticket, TicketStatus


# --- ロール判定（旧 views.role_of / is_agent_user を移設） -------------------

def role_of(user) -> str:
    names = set(user.groups.values_list("name", flat=True))
    if "Admin" in names:
        return "Admin"
    if "Agent" in names:
        return "Agent"
    return "Requester"


def is_agent_user(user: User) -> bool:
    return user.groups.filter(name="Agent").exists()


# --- 参照・更新の基本認可（旧 views.can_view / can_update_status を移設） -----

def can_view(user, ticket: Ticket) -> bool:
    # 意図的欠陥スイッチ：True にすると所有者チェックを迂回し IDOR を再現する。
    # HTML / API の両経路がこの 1 関数を共有するため、スイッチは両方を同時に壊す。
    if getattr(settings, "INTENTIONAL_BUG_IDOR", False):
        return True

    r = role_of(user)
    if r in ("Admin", "Agent"):
        return True
    return ticket.requester_id == user.id


def can_update_status(user, ticket: Ticket) -> bool:
    r = role_of(user)
    if r == "Admin":
        return True
    if r == "Agent" and ticket.assignee_id == user.id:
        return True
    return False


# --- ビュー内インライン認可から切り出した述語 -------------------------------

def can_create(user) -> bool:
    """チケットを作成できるのは Requester のみ（views.ticket_create と同一ルール）。"""
    return role_of(user) == "Requester"


def can_assign(user) -> bool:
    """担当者の割当/解除ができるのは Admin のみ（views.ticket_assign と同一ルール）。"""
    return role_of(user) == "Admin"


def can_change_due(user) -> bool:
    """期限を変更できるのは Admin のみ（views.ticket_change_due_date と同一ルール）。"""
    return role_of(user) == "Admin"


def can_comment(user, ticket: Ticket) -> bool:
    """コメントを追加できるのは当該チケットを閲覧できる者（views.ticket_add_comment と同一ルール）。"""
    return can_view(user, ticket)


def check_status_change(user, ticket: Ticket, new_status):
    """ステータス変更の可否を多段判定する。

    ``views.ticket_change_status`` の「未割当ガード → 更新認可 → 値妥当性 → 遷移妥当性」
    と **同一順序・同一理由文字列**。``can_view`` による参照認可（403）と POST 限定は
    HTTP の関心として呼び出し側に残す。

    Returns:
        ``(ok, reason)``。``reason`` は HTML ビューのエラー文字列をそのまま返す:
        ``"unassigned ticket cannot be updated by agent"`` / ``"forbidden"`` /
        ``"invalid"`` / ``"invalid transition"``。呼び出し側はこの reason を
        HTML では 403 文言として、API では 403/400/409 のコードへ写像する。
    """
    if role_of(user) == "Agent" and ticket.assignee_id is None:
        return (False, "unassigned ticket cannot be updated by agent")
    if not can_update_status(user, ticket):
        return (False, "forbidden")
    if new_status not in TicketStatus.values:
        return (False, "invalid")
    if not ticket.can_transition_to(new_status):
        return (False, "invalid transition")
    return (True, None)
