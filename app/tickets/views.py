from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .models import Ticket, Comment, TicketHistory, TicketStatus
# 認可・状態遷移のルールは policy.py に一本化し、HTML ビューと JSON API で共有する。
# （role_of / can_view 等はここから再エクスポートされるので既存の参照名は不変）
from .policy import (
    role_of,
    is_agent_user,
    can_view,
    can_update_status,
    can_create,
    can_assign,
    can_change_due,
    can_comment,
    check_status_change,
)

@login_required
def ticket_list(request):
    r = role_of(request.user)
    qs = Ticket.objects.all().order_by("-created_at")

    if r == "Requester":
        qs = qs.filter(requester=request.user)

    status = request.GET.get("status") or ""
    q = (request.GET.get("q") or "").strip()

    if status:
        qs = qs.filter(status=status)

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))

    return render(request, "tickets/list.html", {
        "tickets": qs,
        "role": r,
        "status": status,
        "q": q,
        "statuses": TicketStatus.choices,
    })

def _detail_context(request, ticket, error=None):
    """詳細画面のコンテキスト（ticket_detail と期日エラー再描画で共有）。"""
    return {
        "ticket": ticket,
        "role": role_of(request.user),
        "next_candidates": [s for s in TicketStatus.values if ticket.can_transition_to(s)],
        "agents": User.objects.filter(groups__name="Agent").order_by("username"),
        "can_update_status": can_update_status(request.user, ticket),
        "error": error,
    }


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if not can_view(request.user, ticket):
        return HttpResponseForbidden("forbidden")
    return render(request, "tickets/detail.html", _detail_context(request, ticket))

@login_required
def ticket_create(request):
    if not can_create(request.user):
        return HttpResponseForbidden("forbidden")

    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        body = (request.POST.get("body") or "").strip()
        attachment = request.FILES.get("attachment")

        t = Ticket(
            title=title,
            body=body,
            requester=request.user,
            attachment=attachment,
        )

        try:
            t.full_clean()
        except Exception as e:
            return render(request, "tickets/create.html", {"error": str(e)})

        t.save()
        TicketHistory.objects.create(
            ticket=t,
            actor=request.user,
            action=TicketHistory.Action.CREATED
        )
        return redirect("ticket_detail", pk=t.pk)

    return render(request, "tickets/create.html")


@login_required
def ticket_change_status(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if not can_view(request.user, ticket):
        return HttpResponseForbidden("forbidden")
    if request.method != "POST":
        return HttpResponseForbidden("POST only")

    new_status = request.POST.get("status")
    # 未割当ガード→更新認可→値妥当性→遷移妥当性を policy 側で多段判定（順序・文言は不変）。
    ok, reason = check_status_change(request.user, ticket, new_status)
    if not ok:
        return HttpResponseForbidden(reason)

    old = ticket.status
    ticket.status = new_status
    ticket.save(update_fields=["status", "updated_at"])

    TicketHistory.objects.create(
        ticket=ticket,
        actor=request.user,
        action=TicketHistory.Action.STATUS_CHANGED,
        from_value=old,
        to_value=new_status,
    )
    return redirect("ticket_detail", pk=ticket.pk)

@login_required
def ticket_assign(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if not can_assign(request.user):
        return HttpResponseForbidden("forbidden")
    if request.method != "POST":
        return HttpResponseForbidden("POST only")

    assignee_id = request.POST.get("assignee_id") or ""
    if assignee_id == "":
        old = str(ticket.assignee_id) if ticket.assignee_id else ""
        ticket.assignee = None
        ticket.save(update_fields=["assignee", "updated_at"])
        TicketHistory.objects.create(
            ticket=ticket, actor=request.user,
            action=TicketHistory.Action.ASSIGNEE_CHANGED,
            from_value=old, to_value="",
        )
        return redirect("ticket_detail", pk=ticket.pk)

    user = get_object_or_404(User, pk=int(assignee_id))
    if not is_agent_user(user):
        return HttpResponseForbidden("assignee must be Agent")

    old = str(ticket.assignee_id) if ticket.assignee_id else ""
    ticket.assignee = user
    ticket.save(update_fields=["assignee", "updated_at"])

    TicketHistory.objects.create(
        ticket=ticket,
        actor=request.user,
        action=TicketHistory.Action.ASSIGNEE_CHANGED,
        from_value=old,
        to_value=str(user.id),
    )
    return redirect("ticket_detail", pk=ticket.pk)

@login_required
def ticket_add_comment(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if not can_comment(request.user, ticket):
        return HttpResponseForbidden("forbidden")
    if request.method != "POST":
        return HttpResponseForbidden("POST only")

    body = (request.POST.get("body") or "").strip()
    if not body:
        return redirect("ticket_detail", pk=ticket.pk)

    Comment.objects.create(ticket=ticket, author=request.user, body=body)
    TicketHistory.objects.create(
        ticket=ticket,
        actor=request.user,
        action=TicketHistory.Action.COMMENT_ADDED,
    )
    return redirect("ticket_detail", pk=ticket.pk)

@login_required
def ticket_change_due_date(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if not can_change_due(request.user):
        return HttpResponseForbidden("forbidden")
    if request.method != "POST":
        return HttpResponseForbidden("POST only")

    due = request.POST.get("due_date") or ""
    old = ticket.due_date.isoformat() if ticket.due_date else ""

    if due == "":
        ticket.due_date = None
    else:
        ticket.due_date = due
        try:
            ticket.full_clean()
        except ValidationError as e:
            # DEFECT-003 修正: 過去日/不正値は未処理例外（500）ではなく、
            # 作成画面と同様に詳細画面でエラー表示して graceful に拒否する。
            return render(
                request, "tickets/detail.html",
                _detail_context(request, ticket, error=str(e)),
            )

    ticket.save(update_fields=["due_date", "updated_at"])

    new = ticket.due_date.isoformat() if ticket.due_date else ""
    TicketHistory.objects.create(
        ticket=ticket, actor=request.user,
        action=TicketHistory.Action.DUE_DATE_CHANGED,
        from_value=old, to_value=new,
    )
    return redirect("ticket_detail", pk=ticket.pk)
