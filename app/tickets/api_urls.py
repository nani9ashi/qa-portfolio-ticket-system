"""薄い JSON API のルーティング（/api/ 配下）.

トークン取得 → 各エンドポイントを ``Authorization: Token <key>`` で叩く。
HTML 側（tickets.urls）とは別ツリーなので、既存のセッション/CSRF 経路には影響しない。
"""

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import api

app_name = "api"

urlpatterns = [
    path("auth/token/", obtain_auth_token, name="auth-token"),
    path("tickets/", api.TicketListCreateView.as_view(), name="ticket-list"),
    path("tickets/<int:pk>/", api.TicketDetailView.as_view(), name="ticket-detail"),
    path("tickets/<int:pk>/status/", api.TicketStatusView.as_view(), name="ticket-status"),
    path("tickets/<int:pk>/assign/", api.TicketAssignView.as_view(), name="ticket-assign"),
    path("tickets/<int:pk>/comment/", api.TicketCommentView.as_view(), name="ticket-comment"),
    path("tickets/<int:pk>/due/", api.TicketDueView.as_view(), name="ticket-due"),
]
