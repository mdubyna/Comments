from django.core.exceptions import ValidationError


def file_size(value) -> None:
    """Validate test file size"""
    limit = 100 * 1024
    if value.size > limit:
        raise ValidationError("File too large. Size should not exceed 100 KBytes.")
