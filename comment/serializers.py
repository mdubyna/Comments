import logging
import sys

from rest_framework import serializers
from comment.models import Comment


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer"""
    captcha = serializers.CharField(write_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "created_at",
            "text", "image",
            "file",
            "parent_post_comment",
            "author",
            "captcha"
        ]
        read_only_fields = ["author", "created_at", "id"]

    def validate_captcha(self, value: str) -> str:
        """Validate captcha"""
        logging.info(f"Captcha from user: {value}")
        scope = self.context.get("scope")

        if not scope:
            raise serializers.ValidationError(
                "Captcha validation failed: no scope in context."
            )

        session = scope.get("session")

        if not session:
            raise serializers.ValidationError(
                "Captcha validation failed: no session in scope."
            )

        captcha_text = session.get("captcha_text")

        logging.info(f"Generated captcha: {captcha_text}")

        if not captcha_text or value != captcha_text:
            session["captcha_text"] = ""
            session.modified = True
            raise serializers.ValidationError("Invalid captcha")

        return value

    def create(self, validated_data: dict) -> Comment:
        """Remove captcha from validated data"""
        validated_data.pop("captcha")
        return super().create(validated_data)
