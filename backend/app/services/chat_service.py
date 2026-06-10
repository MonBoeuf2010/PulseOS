"""ChatService — the conversational intelligence analyst.

Grounds replies in the user's own context (AI memory + latest briefing) and routes
through the AI Gateway, so a configured ANTHROPIC_API_KEY yields live, reasoned
answers while the offline stub still returns a coherent conversational reply.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.council.ai_gateway import AIGateway
from app.repositories.briefings import BriefingRepository
from app.repositories.chat import ChatRepository
from app.repositories.memory import MemoryRepository

SYSTEM = (
    "You are PulseOS Chat, the user's real-time intelligence analyst. You convert signals "
    "into the single highest-value action they should take right now. Be concise, specific, "
    "and action-oriented; quantify when you can; state your uncertainty honestly; and always "
    "end with one concrete next step. Use the user's context below when relevant."
)
HISTORY_TURNS = 10


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ChatRepository(session)
        self.ai = AIGateway()

    async def _context_block(self, tenant_id: UUID, user_id: UUID) -> str:
        mem = await MemoryRepository(self.session).list(tenant_id, user_id)
        briefing = await BriefingRepository(self.session).latest(tenant_id, user_id)
        lines: list[str] = []
        if mem:
            lines.append("USER MEMORY:")
            lines += [f"- ({m.kind}) {m.content}" for m in mem[:8]]
        if briefing and briefing.items:
            lines.append("LATEST BRIEFING (top actions):")
            lines += [f"- {i.title} (confidence {float(i.confidence):.0%})"
                      for i in sorted(briefing.items, key=lambda x: x.rank)[:5]]
        return "\n".join(lines) or "(no stored context yet)"

    async def send(self, *, tenant_id: UUID, user_id: UUID, convo_id: UUID | None,
                   message: str) -> dict:
        if convo_id:
            convo = await self.repo.get_conversation(tenant_id, user_id, convo_id)
            if convo is None:
                from fastapi import HTTPException, status
                raise HTTPException(status.HTTP_404_NOT_FOUND, "conversation not found")
        else:
            title = (message.strip()[:48] + "…") if len(message) > 48 else message.strip()
            convo = await self.repo.create_conversation(tenant_id, user_id, title=title or "Chat")

        history = await self.repo.history(convo.id)
        await self.repo.add_message(convo=convo, role="user", content=message)

        context = await self._context_block(tenant_id, user_id)
        transcript = "\n".join(
            f"{'USER' if m.role == 'user' else 'ASSISTANT'}: {m.content}"
            for m in history[-HISTORY_TURNS:])
        prompt = (f"CONTEXT:\n{context}\n\n"
                  f"{transcript}\n" if transcript else f"CONTEXT:\n{context}\n\n")
        prompt += f"USER: {message}\nASSISTANT:"

        resp = await self.ai.complete(prompt=prompt, system=SYSTEM, tier="full",
                                      tenant_scoped=True, max_tokens=700)
        assistant = await self.repo.add_message(convo=convo, role="assistant", content=resp.text)
        return {"conversation_id": str(convo.id), "title": convo.title,
                "reply": {"id": str(assistant.id), "role": "assistant", "content": resp.text},
                "cost_usd": resp.cost_usd}
