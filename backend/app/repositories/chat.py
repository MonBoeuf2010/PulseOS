"""Data access for AI-chat conversations + messages (RLS-scoped to the tenant)."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import ChatMessage, Conversation


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_conversation(self, tenant_id: UUID, user_id: UUID,
                                  title: str = "New conversation") -> Conversation:
        convo = Conversation(tenant_id=tenant_id, user_id=user_id, title=title)
        self.session.add(convo)
        await self.session.flush()
        return convo

    async def get_conversation(self, tenant_id: UUID, user_id: UUID,
                               convo_id: UUID) -> Conversation | None:
        res = await self.session.execute(
            select(Conversation)
            .where(Conversation.id == convo_id, Conversation.tenant_id == tenant_id,
                   Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages)))
        return res.scalar_one_or_none()

    async def list_conversations(self, tenant_id: UUID, user_id: UUID) -> list[Conversation]:
        res = await self.session.execute(
            select(Conversation)
            .where(Conversation.tenant_id == tenant_id, Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at)).limit(50))
        return list(res.scalars().all())

    async def history(self, convo_id: UUID) -> list[ChatMessage]:
        res = await self.session.execute(
            select(ChatMessage).where(ChatMessage.conversation_id == convo_id)
            .order_by(ChatMessage.created_at))
        return list(res.scalars().all())

    async def add_message(self, *, convo: Conversation, role: str, content: str) -> ChatMessage:
        msg = ChatMessage(conversation_id=convo.id, tenant_id=convo.tenant_id,
                          role=role, content=content)
        self.session.add(msg)
        await self.session.flush()
        return msg
