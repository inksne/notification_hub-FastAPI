from sqlalchemy import extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .models import Chat_id



class DBManager():
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


db_manager = DBManager()