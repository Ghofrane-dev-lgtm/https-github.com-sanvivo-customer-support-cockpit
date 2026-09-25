"""Sanvivo Support Cockpit — backend.

Serves tickets, conversations and agent traces. Extend this wherever your bet needs it.
Note: the seed content is German on purpose — that is the language this team works in.
"""

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, String, Text, create_engine, func
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from seed import SLOW_TRACE_TICKETS, load_seed

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cockpit.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, index=True)
    subject = Column(String)
    channel = Column(String)
    status = Column(String, index=True)
    category = Column(String, index=True, nullable=True)
    priority = Column(String, index=True, nullable=True)
    assignee = Column(String, nullable=True)
    handled_by_agent = Column(Boolean, default=False)
    escalated = Column(Boolean, default=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    customer_json = Column(Text)
    messages_json = Column(Text)
    trace_json = Column(Text, nullable=True)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def to_summary(t: Ticket) -> dict[str, Any]:
    messages = json.loads(t.messages_json)
    last = messages[-1] if messages else None
    return {
        "id": t.id,
        "subject": t.subject,
        "channel": t.channel,
        "status": t.status,
        "category": t.category,
        "priority": t.priority,
        "assignee": t.assignee,
        "handled_by_agent": t.handled_by_agent,
        "escalated": t.escalated,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        "customer": json.loads(t.customer_json),
        "message_count": len(messages),
        "last_message_at": last["created_at"] if last else None,
        "last_message_preview": (last["text"][:140] if last else None),
        "has_trace": t.trace_json is not None,
    }


def to_detail(t: Ticket) -> dict[str, Any]:
    detail = to_summary(t)
    detail["messages"] = json.loads(t.messages_json)
    return detail


app = FastAPI(
    title="Sanvivo Support Cockpit API",
    version="1.0.0",
    description=(
        "Backend for the support cockpit. Serves tickets, conversations and agent "
        "traces.\n\n"
        "Ticket content is German on purpose — it is what the support team reads. "
        "Field names and this documentation are English.\n\n"
        "Interactive docs: `/docs` (Swagger) and `/redoc`."
    ),
    openapi_tags=[
        {"name": "Tickets", "description": "Read and modify tickets."},
        {"name": "Agent", "description": "What the AI agent did, and calling the LLM."},
        {"name": "System", "description": "Aggregates and health."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def seed_if_empty() -> None:
    db = SessionLocal()
    try:
        if db.query(func.count(Ticket.id)).scalar():
            return
        for row in load_seed():
            db.add(
                Ticket(
                    id=row["id"],
                    subject=row["subject"],
                    channel=row["channel"],
                    status=row["status"],
                    category=row.get("category"),
                    priority=row.get("priority"),
                    assignee=row.get("assignee"),
                    handled_by_agent=row.get("handled_by_agent", False),
                    escalated=row.get("escalated", False),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    customer_json=json.dumps(row["customer"], ensure_ascii=False),
                    messages_json=json.dumps(row["messages"], ensure_ascii=False),
                    trace_json=(
                        json.dumps(row["trace"], ensure_ascii=False)
                        if row.get("trace")
                        else None
                    ),
                )
            )
        db.commit()
    finally:
        db.close()


@app.get("/api/tickets", tags=["Tickets"], summary="List tickets")
def list_tickets(
    status: str | None = None,
    category: str | None = None,
    q: str | None = None,
    limit: int = Query(200, le=500),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Ticket summaries, newest activity first.

    Filters combine. `q` matches subject, last message and customer, case-insensitively.
    Summaries omit the message list — use the detail endpoint for the conversation.
    """
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    if category:
        query = query.filter(Ticket.category == category)
    rows = query.order_by(Ticket.updated_at.desc()).limit(limit).all()
    result = [to_summary(t) for t in rows]
    if q:
        needle = q.lower()
        result = [
            r
            for r in result
            if needle in (r["subject"] or "").lower()
            or needle in (r["last_message_preview"] or "").lower()
            or needle in json.dumps(r["customer"], ensure_ascii=False).lower()
        ]
    return result


@app.get("/api/tickets/{ticket_id}", tags=["Tickets"], summary="Get one ticket")
def get_ticket(ticket_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """A single ticket including its full conversation, oldest message first.

    Returns 404 for an unknown id.
    """
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")
    return to_detail(t)


@app.get("/api/tickets/{ticket_id}/trace", tags=["Agent"], summary="Get the agent trace")
async def get_trace(ticket_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """How the agent reached its answer: reasoning steps, tool calls, retrieval, confidence.

    Not every ticket has one — 404 means the agent never ran on it. Traces are loaded
    from a separate store and are slow; expect several hundred ms, occasionally seconds.
    """
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")
    # The trace is fetched from a separate store, which takes a moment.
    await asyncio.sleep(2.5 if ticket_id in SLOW_TRACE_TICKETS else 0.35)
    if not t.trace_json:
        raise HTTPException(
            status_code=404, detail="Für dieses Ticket existiert kein Agent-Trace"
        )
    return json.loads(t.trace_json)


class MessageIn(BaseModel):
    text: str
    role: Literal["human", "agent"] = "human"
    author: str | None = "Lena"


@app.post("/api/tickets/{ticket_id}/messages", tags=["Tickets"], summary="Reply to a ticket")
def add_message(
    ticket_id: str, payload: MessageIn, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Append a message to the conversation and return the updated ticket.

    Use role `human` for a reply written by a support agent. Rejects empty text with 422.
    """
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")
    if not payload.text.strip():
        raise HTTPException(status_code=422, detail="Nachricht ist leer")
    messages = json.loads(t.messages_json)
    message = {
        "id": str(uuid.uuid4()),
        "role": payload.role,
        "author": payload.author,
        "text": payload.text,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    messages.append(message)
    t.messages_json = json.dumps(messages, ensure_ascii=False)
    t.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(t)
    return to_detail(t)


class TicketPatch(BaseModel):
    status: Literal["open", "waiting_customer", "escalated", "closed"] | None = None
    priority: Literal["low", "medium", "high"] | None = None
    category: str | None = None
    assignee: str | None = None


@app.patch("/api/tickets/{ticket_id}", tags=["Tickets"], summary="Update ticket fields")
def patch_ticket(
    ticket_id: str, payload: TicketPatch, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Change status, priority, category or assignee. Omitted fields stay untouched.

    Rejects unknown status or priority values with 422.
    """
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket nicht gefunden")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    t.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(t)
    return to_detail(t)


class LLMRequest(BaseModel):
    messages: list[dict[str, str]]
    model: str | None = None
    temperature: float = 0.3
    max_tokens: int = 800


@app.post("/api/llm", tags=["Agent"], summary="Call the LLM")
def llm(payload: LLMRequest) -> dict[str, Any]:
    """Proxy to the OpenAI chat completions API, so the key never reaches the browser.

    Pass OpenAI-shaped messages. Returns 503 if OPENAI_API_KEY is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY ist nicht gesetzt")
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=payload.model or os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        messages=payload.messages,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )
    return {
        "content": completion.choices[0].message.content,
        "model": completion.model,
        "usage": completion.usage.model_dump() if completion.usage else None,
    }


@app.get("/api/stats", tags=["System"], summary="Ticket aggregates")
def stats(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Counts across the whole ticket set, grouped by status, category and priority.

    Tickets without a category or priority are counted as `unbekannt`.
    """
    rows = db.query(Ticket).all()
    total = len(rows)
    return {
        "total": total,
        "by_status": _count(rows, lambda t: t.status),
        "by_category": _count(rows, lambda t: t.category or "unbekannt"),
        "by_priority": _count(rows, lambda t: t.priority or "unbekannt"),
        "escalated": sum(1 for t in rows if t.escalated),
        "handled_by_agent": sum(1 for t in rows if t.handled_by_agent),
    }


def _count(rows, key) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        out[key(row)] = out.get(key(row), 0) + 1
    return out


@app.get("/api/health", tags=["System"], summary="Health check")
def health() -> dict[str, str]:
    """Returns ok when the backend is up. Useful to check the Vite proxy is wired."""
    return {"status": "ok"}
