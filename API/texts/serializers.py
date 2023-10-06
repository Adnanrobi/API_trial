from rest_framework import serializers
from .models import Text


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = [
            "id",
            "user_input",
            "chatgpt_input",
            "user_id",
        ]

    chatgpt_input = serializers.CharField(required=False)
    user_id = serializers.CharField(required=True)
