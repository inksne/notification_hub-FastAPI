from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

import logging
from typing import Optional, Sequence
from datetime import datetime
import redis.asyncio as redis

from .models import User, Chat_id, Notification, Refresh_token
from ..config import configure_logging, constant_settings



configure_logging()
logger = logging.getLogger(__name__)



class PSQLManager():
    async def register(self, username: str, email: str, hashed_password: str, session: AsyncSession) -> Optional[bool]:
        try:
            result_user = await session.execute(select(User).where(User.username == username, User.email == email))
            user = result_user.scalar_one_or_none()

            if user:
                return False

            new_user = User(username=username, email=email, password=hashed_password)

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return True

        except IntegrityError:
            return None


    async def get_or_create_oauth_user(self, email: str, username: str, hashed_password: str, session: AsyncSession) -> Optional[User]:
        user = await self.get_user_by_username(username=username, session=session)

        if user:
            return user

        try:
            new_user = User(username=username, email=email, password=hashed_password)

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return new_user

        except IntegrityError:
            await session.rollback()

            user = await self.get_user_by_username(username=username, session=session)
            if user:
                return user

            return None


    async def get_user_by_username(self, username: str | None, session: AsyncSession) -> Optional[User]:
        if not username:    # mypy
            return None

        result = await session.execute(select(User).where(User.username == username))
        user = result.scalars().first()

        if user is None:
            return None

        return user


    async def get_user_by_user_id(self, user_id: int, session: AsyncSession) -> Optional[User]:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if user is None:
            return None

        return user


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


    async def delete_chat_id(self, username: str | None, session: AsyncSession) -> None:
        if not username:    # mypy
            return

        chat_id = await session.execute(select(Chat_id).where(Chat_id.username == username))
        result_chat_id = chat_id.scalar_one_or_none()

        await session.delete(result_chat_id)
        await session.commit()


    async def add_notification(
        self,
        channels: list[str] | dict[str, str | dict[str, str]],
        content: str,
        user_id: int,
        recipient: list[str | dict[str, str]],
        session: AsyncSession
    ) -> None:

        new_notification = Notification(
            channels=channels, content=content, user_id=user_id, recipient=recipient
        )

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


    async def add_refresh_token_hash(
        self,
        username: str,
        refresh_token_hash: str,
        expires_at: datetime,
        session: AsyncSession
    ) -> None:
        user = await self.get_user_by_username(username=username, session=session)
        if not user:    # mypy
            raise ValueError

        new_refresh = Refresh_token(
            user_id=user.id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
        )

        session.add(new_refresh)

        await session.commit()
        await session.refresh(new_refresh)


    async def get_refresh_token_hash(
        self,
        refresh_token_hash: str,
        now: datetime,
        session: AsyncSession
    ) -> Optional[Refresh_token]:
        result = await session.execute(
            select(Refresh_token).where(
                Refresh_token.refresh_token_hash == refresh_token_hash,
                Refresh_token.is_revoked.is_(False),
                Refresh_token.expires_at > now,
            )
        )

        refresh = result.scalars().first()

        return refresh


    async def update_refresh_token_hash(
        self,
        refresh_token_hash: str,
        now: datetime,
        new_refresh_token_hash: str,
        new_expires_at: datetime,
        session: AsyncSession
    ) -> None:
        db_refresh_token_hash = await self.get_refresh_token_hash(
            refresh_token_hash=refresh_token_hash,
            now=now,
            session=session
        )

        if not db_refresh_token_hash:    # mypy
            raise ValueError

        db_refresh_token_hash.refresh_token_hash =new_refresh_token_hash
        db_refresh_token_hash.expires_at = new_expires_at

        session.add(db_refresh_token_hash)

        await session.commit()
        await session.refresh(db_refresh_token_hash)


    async def delete_refresh_token_hash(
        self,
        db_refresh_token_hash: Refresh_token,
        session: AsyncSession
    ) -> None:
        await session.delete(db_refresh_token_hash)

        await session.commit()


psql_manager = PSQLManager()


class RedisManager():
    def __init__(self) -> None:
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