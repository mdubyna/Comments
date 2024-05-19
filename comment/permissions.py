from typing import Dict, Any

from channels.consumer import AsyncConsumer
from djangochannelsrestframework import permissions


class IsAuthenticatedForWrite(permissions.IsAuthenticated):
    """Custom authentication class
    to allow access fpr write only to Authenticated Users"""
    async def has_permission(
            self, scope: Dict[str, Any],
            consumer: AsyncConsumer,
            action: str,
            **kwargs
    ) -> bool:
        """Check action"""
        if action == "list":
            return True
        return await super().has_permission(
            scope,
            consumer,
            action,
            **kwargs
        )
