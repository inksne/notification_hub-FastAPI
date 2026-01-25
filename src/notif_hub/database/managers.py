from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from typing import Sequence
import redis.asyncio as redis

from .models import Chat_id, Notification
from ..config import constant_settings



class PSQLManager():
    async def add_chat_id(self, chat_id: int, username: str | None, session: AsyncSession) -> None:
        if not username:    # mypy
            return

        new_chat_id = Chat_id(chat_id=chat_id, username=username)

        session.add(new_chat_id)

        await session.commit()
        await session.refresh(new_chat_id)


    async def get_chat_id(self, username: str | None, session: AsyncSession) -> int | bool:
        if not username:    # mypy
            return False

        chat_id = await session.execute(select(Chat_id).where(Chat_id.username == username))
        result_chat_id = chat_id.scalar_one_or_none()

        if not result_chat_id:
            return False

        return result_chat_id.chat_id


    async def delete_chat_id(self, username: str| None, session: AsyncSession) -> None:
        if not username:    # mypy
            return

        chat_id = await session.execute(select(Chat_id).where(Chat_id.username == username))
        result_chat_id = chat_id.scalar_one_or_none()

        await session.delete(result_chat_id)
        await session.commit()


    async def add_notification(
        self, channels: list[str], content: str, user_id: int, session: AsyncSession
    ) -> None:

        new_notification = Notification(channels=channels, content=content, user_id=user_id)

        session.add(new_notification)

        await session.commit()
        await session.refresh(new_notification)


    async def get_notifications(self, user_id: int, session: AsyncSession) -> Sequence[Notification]:
        notifications = await session.execute(
            select(Notification).where(Notification.user_id == user_id)
        )

        result_notifications = notifications.scalars().all()

        return result_notifications


    async def delete_notification(self, notification_id: int, session: AsyncSession) -> None:
        notification = await session.execute(
            select(Notification).where(Notification.id == notification_id)
        )

        result_notification = notification.scalar_one_or_none()

        await session.delete(result_notification)
        await session.commit()


psql_manager = PSQLManager()


class RedisManager():
    def __init__(self):
        self.r = redis.Redis(host=constant_settings.REDIS_HOST)

    async def add_state(self, state: str) -> None:
        await self.r.set(
            f"{constant_settings.REDIS_STATE_PREFIX}{state}",
            "1", ex=constant_settings.REDIS_STATE_TTL
        )

    async def get_state(self, state: str) -> bool:
        value = await self.r.getdel(f"{constant_settings.REDIS_STATE_PREFIX}{state}")
        return value is not None


redis_manager = RedisManager()