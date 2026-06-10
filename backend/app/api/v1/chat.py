"""AI Chat endpoints — the conversational intelligence analyst."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_subject, db
from app.core.security import Subject
from app.repositories.chat import ChatRepository
from app.schemas import ChatIn, ChatMessageOut, ConversationDetailOut, ConversationOut
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("")
async def send(body: ChatIn, subject: Subject = Depends(current_subject),
               session: AsyncSession = Depends(db)):
    return await ChatService(session).send(
        tenant_id=subject.tenant_id, user_id=subject.user_id,
        convo_id=body.conversation_id, message=body.message)


@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations(subject: Subject = Depends(current_subject),
                             session: AsyncSession = Depends(db)):
    rows = await ChatRepository(session).list_conversations(subject.tenant_id, subject.user_id)
    return [ConversationOut.model_validate(r) for r in rows]


@router.get("/conversations/{convo_id}", response_model=ConversationDetailOut)
async def get_conversation(convo_id: UUID, subject: Subject = Depends(current_subject),
                           session: AsyncSession = Depends(db)):
    convo = await ChatRepository(session).get_conversation(
        subject.tenant_id, subject.user_id, convo_id)
    if convo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "conversation not found")
    msgs = sorted(convo.messages, key=lambda m: m.created_at or 0)
    return ConversationDetailOut(id=convo.id, title=convo.title,
                                 messages=[ChatMessageOut.model_validate(m) for m in msgs])
