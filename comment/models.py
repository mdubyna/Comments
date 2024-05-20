import pathlib
import uuid

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from django_resized import ResizedImageField

from comment.validators import file_size


def comment_media_path(instance: "Comment", filename: str) -> pathlib.Path:
    """Path for media file to be uploaded"""
    filename = (f"{slugify(filename)}-{uuid.uuid4()}"
                + pathlib.Path(filename).suffix)
    return pathlib.Path(filename)


def comment_image_path(instance: "Comment", filename: str) -> pathlib.Path:
    """Path for image media file to be uploaded"""
    return pathlib.Path("images/") / comment_media_path(instance, filename)


def comment_file_path(instance: "Comment", filename: str) -> pathlib.Path:
    """Path for text media file to be uploaded"""
    return pathlib.Path("files/") / comment_media_path(instance, filename)


class Comment(models.Model):
    """Comment model"""
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    text = models.TextField()
    image = ResizedImageField(
        null=True,
        upload_to=comment_image_path,
        size=[320, 240],
        validators=[FileExtensionValidator(
            allowed_extensions=["jpg", "gif", "png", "jpeg"],
            message="Please upload an image "
                    "of one of these formats 'jpg', 'gif', 'png'"
        )]
    )
    file = models.FileField(
        null=True,
        upload_to=comment_file_path,
        validators=[FileExtensionValidator(
            allowed_extensions=["txt", "plain"],
            message="Please upload an file "
                    "of this format - 'txt'"
        ), file_size]
    )
    parent_post_comment = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="child",
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.author} - {self.created_at}"
