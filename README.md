# Sanvivo — Product Engineer Challenge: The Support Cockpit

**Time budget: 3 hours · Stack: FastAPI + React (provided) · Product language: German**

> Instructions are in English. The tickets and the interface are **German** — that is the
> environment this tool lives in. Write `DECISIONS.md` and code in English. We do not
> grade your German.

---

## The situation

Sanvivo is a German **mail-order pharmacy for medical cannabis**. For the past few
months our customer support has been backed by an AI agent: it reads incoming customer
messages, looks things up in our knowledge base, calls tools (order status, shipment
tracking) and answers a share of the requests on its own. The rest it escalates to the
support team.

The agent is running. **The tool for the humans behind it is missing.**

The support team is three people. Today they work blind: they cannot see what the agent
answered, why it answered that way, or which tickets are going wrong right now. They
find out when someone complains.

### Who you are building for

> **Lena, 29, support agent.** No technical background. She has this tool open **six
> hours a day** and works through tickets in parallel. She needs to see instantly what is
> urgent, judge in about a second whether the agent's answer was acceptable, and step in
> herself when it wasn't.

Lena is the user. Not us, not the CTO, not a management metrics dashboard. When you are
weighing a decision, ask what helps Lena in hour five of her shift.

---

## Your task

**Build the cockpit this team works in.**

This is deliberately not a feature list. There is a mandatory core so we can compare
submissions — beyond that, **you** decide what makes the product good.

### Part 1 — Core (mandatory)

1. **Ticket overview** — all tickets from the backend, with filtering or sorting that
   makes sense. Lena has to find her work here.
2. **Detail view** — clicking a ticket opens the full conversation between customer and
   agent.
3. **Agent transparency** — make visible *how* the agent arrived at its answer: reasoning
   steps, tool calls with arguments and results, knowledge base passages it pulled,
   confidence. The data is served by `GET /api/tickets/{id}/trace`.
4. **At least one real action** — Lena must be able to *do* something that changes state:
   take a ticket, reply herself, escalate, close. A read-only dashboard does not count as
   a product.

### Part 2 — Product bets (pick **two**)

Choose two directions and build them **in depth**, rather than touching all of them.
You may also place **your own bet** instead — justify it in `DECISIONS.md`.

| | Bet | Guiding question |
|---|---|---|
| **W1** | **Triage** | Which five tickets does Lena need to touch *right now*? Build an actual ranking (waiting time, frustration signals, risk, customer value …), not just a sort by date. |
| **W2** | **Trust** | The agent is sometimes wrong. How does Lena see in one second whether she can trust it here? Source citations, uncertainty signals, "it guessed at this point". |
| **W3** | **Reply assistant** | Lena wants to correct the agent's answer. Have the LLM propose two or three phrasings (German, Sanvivo's tone) that she edits and sends. |
| **W4** | **Quality loop** | Lena rates answers (good / wrong / dangerous). Show what happens to that judgement — how does a label turn into an improvement? |
| **W5** | **Patterns & bulk** | Sixty tickets about the same DHL outage. Detect clusters and treat them as *one* thing instead of sixty. |
| **W6** | **Safety view** | Surface red flags: medical or dosage questions, prompt injection, personal data in plain text, "the agent promised a refund". |
| **W7** | **Team view** | How well is the automation actually working? Automation rate, escalation reasons, trend. For the team lead, not for Lena. |
| **W\*** | **Your own bet** | Something you saw in the data and consider more important. Explicitly welcome. |

### You will not finish all of this

That is intended. Three hours is enough for the core plus two bets at a decent depth —
no more. **We evaluate your choices and your depth, not your coverage.** One bet done
well beats four half-built.

---

## What we provide

```
sanvivo-support-cockpit/
├── backend/          FastAPI + SQLite, running, with seed data
└── frontend/         Vite + React + TypeScript + Tailwind, deliberately plain
```

The UI we ship is **deliberately unattractive**: a working, ugly ticket list and an
almost empty detail route. We are not giving away any design, but we also do not want
you spending time on project setup. What you make of it is your call — including the
call to throw our version away.

### Backend endpoints (already there)

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/tickets` | List; supports `?status=`, `?category=`, `?q=` |
| `GET` | `/api/tickets/{id}` | Ticket including the full conversation |
| `GET` | `/api/tickets/{id}/trace` | Agent trace: reasoning, tool calls, KB hits, confidence |
| `POST` | `/api/tickets/{id}/messages` | Send a message as a human agent |
| `PATCH` | `/api/tickets/{id}` | Change status, assignee, priority |
| `POST` | `/api/llm` | Proxy to the OpenAI API — **the key stays server-side** |
| `GET` | `/api/stats` | Simple aggregates |

Full request and response details are in the interactive docs FastAPI generates at
**`http://localhost:8000/docs`** — you can call every endpoint from there.

You may — and should — extend the backend where your bet needs it. New endpoints,
changed response shapes, aggregations: all fair game. We want to see where you draw the
line between server and client.

### Setup

```bash
# Backend — terminal 1
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your OPENAI_API_KEY
uvicorn main:app --reload --port 8000

# Frontend — terminal 2
cd frontend && npm install && npm run dev
```

The frontend runs on `http://localhost:5173` and proxies all `/api` calls to the backend
on port 8000. The backend seeds `cockpit.db` from `backend/data/tickets.json` on first
start — delete that file to reset the data. API docs: `http://localhost:8000/docs`.

The **OpenAI API key** arrives separately by email. It belongs in `.env` and never in the
repository.

---

## What to hand in

A GitHub repository containing:

1. **The running code.** Your `README.md` explains in five lines or fewer how to start
   it. We will run it and expect it to work on the first try.
2. **`DECISIONS.md`** — one page maximum, four sections:
   - **Choices:** Which two bets, and why those specifically?
   - **Trade-offs:** What did you deliberately *not* build — and what would come next?
   - **Edge cases:** Which special cases did you find in the data? Handled or knowingly
     deferred — both are valid answers; saying nothing is not.
   - **AI usage:** Which tools (Cursor, Claude Code, Copilot …)? Where did they help?
     **And where did you reject a suggestion — why?**
3. OPTIONAL: **A screenshot or a video of at most 60 seconds** showing the running app.

---

## Ground rules

- **AI assistants are explicitly allowed** and part of the evaluation. We want to see how
  you work with them, not whether you can work without them. The condition: you
  understand and stand behind every line you submit.
- **No no-code tools** (n8n, Flowise, Bubble) — we need to see your code.
- Libraries are your choice. You may replace parts of the provided stack if you can
  explain why that pays off within three hours.
- Questions about the task? Write to us. A good question is a good sign.

Good luck.
# customer-support-cockpit
