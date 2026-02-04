from sqlalchemy import ForeignKey, String, Text, Integer, ARRAY, func, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str]
    password: Mapped[str] = mapped_column(Text, nullable=False)

    notifications: Mapped['Notification'] = relationship('Notification', back_populates='user')
    refresh_tokens: Mapped['Refresh_token'] = relationship('Refresh_token', back_populates='user')


class Notification(Base):
    __tablename__ = 'notifications'

    id: Mapped[int] = mapped_column(primary_key=True)
    channels: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    recipient: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    user: Mapped['User'] = relationship('User', back_populates='notifications')


class Refresh_token(Base):
    __tablename__ = 'refresh_tokens'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    refresh_token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped['User'] = relationship('User', back_populates='refresh_tokens')


class Chat_id(Base):
    __tablename__ = 'chat_ids'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, nullable=False)
    username: Mapped[str] = mapped_column(String(32), nullable=False)