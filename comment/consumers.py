import base64
import uuid
import logging
import sys

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from djangochannelsrestframework import pagination
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework import mixins
from django.core.files.base import ContentFile

from comment.models import Comment
from comment.serializers import CommentSerializer
from comment.permissions import IsAuthenticatedForWrite


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


class CommentConsumer(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAsyncAPIConsumer):
    """Comment consumer for handling web socket connections."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedForWrite,)
    pagination_class = pagination.WebsocketLimitOffsetPagination

    @action()
    async def subscribe_to_comment_activity(
            self, comments: str = "comments",
            **kwargs
    ) -> None:
        """Subscribe consumers to comment activity."""
        await self.comment_change_handler.subscribe(comments=comments)

    @model_observer(Comment)
    async def comment_change_handler(
            self,
            comment: Comment,
            observer=None,
            **kwargs
    ) -> None:
        """Observe comment changes."""
        await self.send_json(comment)

    @comment_change_handler.serializer
    def comment_change_handler(
            self,
            instance: Comment,
            action: str,
            **kwargs
    ) -> dict:
        """This will return the comment serializer"""
        return dict(data=CommentSerializer(instance).data, action=action.value, pk=instance.pk)

    @action()
    async def create(self, **kwargs) -> None:
        """Custom create method for creating comments"""
        data = kwargs.get("data", {})
        image_data = data.pop("image", None)
        file_data = data.pop("file", None)

        if image_data:
            format_image, imgstr = image_data.split(";base64,")
            ext = format_image.split("/")[-1]
            data["image"] = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')

        if file_data:
            format_file, filestr = file_data.split(";base64,")
            ext = format_file.split('/')[-1]
            data["file"] = ContentFile(base64.b64decode(filestr), name=f'{uuid.uuid4()}.{ext}')

        await self.load_and_update_session()

        serializer = CommentSerializer(data=data, context={"scope": self.scope})

        if await database_sync_to_async(serializer.is_valid)():
            comment = await database_sync_to_async(serializer.save)(author=self.scope["user"])
            await self.send_json(CommentSerializer(comment).data)
        else:
            logging.info("Invalid data:", serializer.errors)
            await self.send_json({"type": "error", "errors": serializer.errors})

    async def load_and_update_session(self) -> None:
        """Update actual session"""
        current_session_data = await sync_to_async(self.scope["session"].load)()
        await sync_to_async(self.scope["session"].update)(current_session_data)
        await sync_to_async(self.scope["session"].save)()
