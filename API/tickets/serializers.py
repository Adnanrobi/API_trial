from rest_framework import serializers
from .models import *


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "creator_id",
            "description",
            "files",
            "is_open",
            "opened_by_med_id",
        )  # Include other fields as needed

    creator_id = serializers.CharField(required=True)
    files = serializers.FileField(
        max_length=None, allow_empty_file=False, use_url=False, required=False
    )
    opened_by_med_id = serializers.CharField(required=False)


class TicketUpdateSerializer(serializers.Serializer):
    # Define user_id and ticket_id as read-only fields
    user_id = serializers.IntegerField(read_only=True)
    ticket_id = serializers.IntegerField(read_only=True)

    description = serializers.CharField(required=False)
    files = serializers.FileField(required=False)

    def update(self, instance, validated_data):
        # Update the instance with validated data
        if validated_data.get("description"):
            instance.description = validated_data["description"]
        if validated_data.get("files"):
            instance.files = validated_data["files"]
        # else:
        #     instance.files = None
        instance.save()
        return instance


class TicketFollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketFollowUp
        fields = (
            "root",
            "creator_id",
            "is_medUser",
            "description",
            "files",
        )  # Include other fields as needed

    creator_id = serializers.CharField(required=True)
    files = serializers.FileField(
        max_length=None, allow_empty_file=True, use_url=False, required=False
    )


class TicketFollowupUpdateSerializer(serializers.Serializer):
    # Define user_id and ticket_id as read-only fields
    user_id = serializers.IntegerField(read_only=True)
    ticket_fu_id = serializers.IntegerField(read_only=True)

    description = serializers.CharField(required=False)
    files = serializers.FileField(required=False)

    def update(self, instance, validated_data):
        # Update the instance with validated data
        if validated_data.get("description"):
            instance.description = validated_data["description"]
        if validated_data.get("files"):
            instance.files = validated_data["files"]
        # else:
        #     instance.files = None
        instance.save()
        return instance
