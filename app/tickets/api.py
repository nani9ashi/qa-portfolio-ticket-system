"""テスト容易性のための薄い JSON API（QA 判断による最小実装）.

HTML アプリと **同じ** 認可・業務ルール（``tickets.policy``）を呼び出し、その結果を
意味的に正しい HTTP ステータスへ写像する。プロダクト機能の追加ではなく、runn による
API/インテグレーションテストを成立させるための最小層。

HTML ビューが全拒否を 403 文言で表現するのに対し、本 API は同じ *ルール* を
401（未認証）/ 403（認可）/ 400（入力不正）/ 409（状態競合）/ 404（不在）へ写像する。
これは「① は期待値を一意に書き下せる決定的な世界」の体現でもある。

認証は TokenAuthentication（``settings.REST_FRAMEWORK``）。Session/CSRF は用いない
ため、runn は ``Authorization: Token <key>`` を引き回すだけでよい。
"""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status as http
from rest_framework.response import Response
from rest_framework.views import APIView

from . import policy
from .models import Comment, Ticket, TicketHistory
from .serializers import TicketSerializer

# policy.check_status_change の reason 文字列 → HTTP コード。
# HTML は全て 403 文言。API は意味で分ける（入力不正=400 / 状態競合=409 / 認可=403）。
_STATUS_CODE = {
    "unassigned ticket cannot be updated by agent": http.HTTP_403_FORBIDDEN,
    "forbidden": http.HTTP_403_FORBIDDEN,
    "invalid": http.HTTP_400_BAD_REQUEST,          # enum 外の不正値
    "invalid transition": http.HTTP_409_CONFLICT,  # 妥当値だが禁止エッジ＝状態競合
}


def _forbidden(detail="forbidden"):
    return Response({"detail": detail}, status=http.HTTP_403_FORBIDDEN)


class TicketListCreateView(APIView):
    """GET: ロールでスコープした一覧 / POST: 作成（Requester のみ）。"""

    def get(self, request):
        user = request.user
        qs = Ticket.objects.all().order_by("-created_at")
        if policy.role_of(user) == "Requester":
            qs = qs.filter(requester=user)

        status_f = request.query_params.get("status") or ""
        q = (request.query_params.get("q") or "").strip()
        if status_f:
            qs = qs.filter(status=status_f)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))

        return Response(TicketSerializer(qs, many=True).data)

    def post(self, request):
        user = request.user
        if not policy.can_create(user):
            return _forbidden()

        title = (request.data.get("title") or "").strip()
        body = (request.data.get("body") or "").strip()

        ticket = Ticket(title=title, body=body, requester=user)
        try:
            # 入力検証は HTML 作成ビューと同じ Model.full_clean()（title 80 / body 4000 等）。
            ticket.full_clean()
        except ValidationError as e:
            return Response(
                {"detail": "validation error", "errors": e.message_dict},
                status=http.HTTP_400_BAD_REQUEST,
            )

        ticket.save()
        TicketHistory.objects.create(
            ticket=ticket, actor=user, action=TicketHistory.Action.CREATED,
        )
        return Response(TicketSerializer(ticket).data, status=http.HTTP_201_CREATED)


class TicketDetailView(APIView):
    """GET: 詳細（can_view 不成立は 403＝IDOR もここで忠実にミラー）。"""

    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if not policy.can_view(request.user, ticket):
            return _forbidden()
        return Response(TicketSerializer(ticket).data)


class TicketStatusView(APIView):
    """POST: ステータス変更（policy.check_status_change を共有）。"""

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if not policy.can_view(request.user, ticket):
            return _forbidden()

        new_status = request.data.get("status")
        ok, reason = policy.check_status_change(request.user, ticket, new_status)
        if not ok:
            return Response({"detail": reason}, status=_STATUS_CODE[reason])

        old = ticket.status
        ticket.status = new_status
        ticket.save(update_fields=["status", "updated_at"])
        TicketHistory.objects.create(
            ticket=ticket, actor=request.user,
            action=TicketHistory.Action.STATUS_CHANGED,
            from_value=old, to_value=new_status,
        )
        return Response(TicketSerializer(ticket).data)


class TicketAssignView(APIView):
    """POST: 担当の割当/解除（Admin のみ・assignee は Agent 限定）。"""

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if not policy.can_assign(request.user):
            return _forbidden()

        # runn 向けに安定した username 指定（assignee）も受け付ける。HTML は数値 PK
        # （assignee_id）。どちらでも判定する「Agent でなければならない」ルールは不変。
        assignee_id = request.data.get("assignee_id")
        assignee_username = request.data.get("assignee")

        if not assignee_username and assignee_id in (None, "", "null"):
            old = str(ticket.assignee_id) if ticket.assignee_id else ""
            ticket.assignee = None
            ticket.save(update_fields=["assignee", "updated_at"])
            TicketHistory.objects.create(
                ticket=ticket, actor=request.user,
                action=TicketHistory.Action.ASSIGNEE_CHANGED,
                from_value=old, to_value="",
            )
            return Response(TicketSerializer(ticket).data)

        try:
            if assignee_username:
                assignee = User.objects.get(username=assignee_username)
            else:
                assignee = User.objects.get(pk=int(assignee_id))
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "assignee not found"}, status=http.HTTP_404_NOT_FOUND)

        if not policy.is_agent_user(assignee):
            return Response({"detail": "assignee must be Agent"}, status=http.HTTP_400_BAD_REQUEST)

        old = str(ticket.assignee_id) if ticket.assignee_id else ""
        ticket.assignee = assignee
        ticket.save(update_fields=["assignee", "updated_at"])
        TicketHistory.objects.create(
            ticket=ticket, actor=request.user,
            action=TicketHistory.Action.ASSIGNEE_CHANGED,
            from_value=old, to_value=str(assignee.id),
        )
        return Response(TicketSerializer(ticket).data)


class TicketCommentView(APIView):
    """POST: コメント追加（can_comment=can_view を共有）。"""

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if not policy.can_comment(request.user, ticket):
            return _forbidden()

        body = (request.data.get("body") or "").strip()
        if not body:
            # HTML は空コメントを黙って無視（リダイレクト）。API は入力不正として 400。
            return Response({"detail": "empty comment"}, status=http.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(ticket=ticket, author=request.user, body=body)
        TicketHistory.objects.create(
            ticket=ticket, actor=request.user,
            action=TicketHistory.Action.COMMENT_ADDED,
        )
        return Response(
            {"id": comment.id, "ticket": ticket.id, "body": comment.body},
            status=http.HTTP_201_CREATED,
        )


class TicketDueView(APIView):
    """POST: 期限変更（Admin のみ）。過去日/不正フォーマットは 400。

    HTML ビュー（``ticket_change_due_date``）は full_clean() を try/except で囲って
    おらず、過去日で 500 になる（DEFECT-003）。本 API は意味的に正しい 400 を返し、
    その期待値が HTML 側の不具合を炙り出す（層別テストの価値の実演）。
    """

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if not policy.can_change_due(request.user):
            return _forbidden()

        due = request.data.get("due_date")
        old = ticket.due_date.isoformat() if ticket.due_date else ""

        if due in (None, "", "null"):
            ticket.due_date = None
        else:
            ticket.due_date = due
            try:
                ticket.full_clean()  # 過去日（Model.clean）/ 不正フォーマットを検出
            except ValidationError as e:
                return Response(
                    {"detail": "validation error", "errors": e.message_dict},
                    status=http.HTTP_400_BAD_REQUEST,
                )

        ticket.save(update_fields=["due_date", "updated_at"])
        new = ticket.due_date.isoformat() if ticket.due_date else ""
        TicketHistory.objects.create(
            ticket=ticket, actor=request.user,
            action=TicketHistory.Action.DUE_DATE_CHANGED,
            from_value=old, to_value=new,
        )
        return Response(TicketSerializer(ticket).data)
