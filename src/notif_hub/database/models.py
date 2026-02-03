from sqlalchemy import ForeignKey, String, Text, Integer, ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str]
    password: Mapped[str] = mapped_column(Text, nullable=False)

    notifications: Mapped['Notification'] = relationship('Notification', back_populates='user')


class Notification(Base):
    __tablename__ = 'notifications'

    id: Mapped[int] = mapped_column(primary_key=True)
    channels: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    recipient: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    user: Mapped['User'] = relationship('User', back_populates='notifications')


class Chat_id(Base):
    __tablename__ = 'chat_ids'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, nullable=False)
    username: Mapped[str] = mapped_column(String(32), nullable=False)