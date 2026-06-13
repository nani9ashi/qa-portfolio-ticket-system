"""API 出力用シリアライザ（最小・出力専用）.

作成/更新の入力検証は HTML ビューと同じく ``Model.full_clean()`` に委ねる方針のため、
本シリアライザは主にレスポンス整形に用いる（認可・検証ルールを二重実装しない）。
"""

from rest_framework import serializers

from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    requester = serializers.CharField(source="requester.username", read_only=True)
    assignee = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id", "title", "body", "status", "due_date",
            "requester", "assignee", "created_at", "updated_at",
        ]

    def get_assignee(self, obj):
        return obj.assignee.username if obj.assignee_id else None
