# Decisions

## Choices
**W1 Triage + W2 Trust.** In the seed data the agent's confidence does not predict whether its
answer is right: TKT-1005 (62 %) sent a tracking number although both tools had failed, and
TKT-1003 (81 %) gave a dosage recommendation. Lena therefore needs a verdict she can trust (W2)
and a queue that puts that harm — plus waiting, repeatedly asking and under-supplied patients —
first (W1). Both are computed on the server (`backend/signals.py`): the trace endpoint is slow
(up to 2.5 s), and ranking needs every trace, so the list already carries verdict and score and
Lena sees them before the trace has loaded. Every score comes with its reasons, and every trust
warning points at the trace step it came from, which the trace view highlights.

## Trade-offs
Deliberately simple, keyword/threshold rules — transparent and explainable, but they miss
paraphrases. Not detected yet: prompt injection (TKT-1004), the agent echoing health data
(TKT-1008), parcels stuck at DHL Leipzig although the agent says "1–2 days" (TKT-2001–2008).
No LLM call anywhere, so the OpenAI key is not needed to run the app.
Not built: reply assistant (W3), rating loop (W4), DHL clustering (W5), team view (W7), login
(the user is hard-coded as "Lena"). Next: cluster the DHL wave into one bulk action, add the
missing safety rules, let Lena mark a warning as false alarm to tune the weights.

## Edge cases
- Seed data is from March 2026 → `COCKPIT_NOW` pins "today", otherwise every ticket waits months.
- No trace (TKT-1006, TKT-1021) → "Ohne Agent"; the trace 404 is shown as a sentence, not an error.
- Empty conversation (TKT-1006) and a 41-message thread (TKT-1007, opens at the newest message).
- Closed but dangerous tickets (TKT-1003, 1005, 1011) still surface in the queue.
- Slow traces (TKT-1007, 1019, 2004): the verdict is shown immediately, the trace loads after.
- `PATCH status=escalated` did not set the `escalated` flag → fixed in the backend.
- Deferred: TKT-1018 waits on the customer since 27.02 (no follow-up rule); TKT-1009 is partly
  English; TKT-1019 is a repeat refund (possible abuse signal).

## AI usage
Tool: Claude Code. My rule: the AI drafts, I decide and verify — and I only keep code I can explain.
- **Understand before building.** I first had it walk me through the repo, the endpoints and the
  seed data, and only then settled on the bets — the Choices above rest on cases found in the data.
- **Own the core, delegate the boilerplate.** I built the logic that carries the decisions myself,
  step by step (`signals.py`, its wiring in `main.py`, the types in `api.ts`). Under time pressure
  I let it generate the UI components from that contract, then reviewed them.
- **Verify every step, don't trust output.** After each step I ran a check against real data
  (the ranking script, the API response, `tsc`). This caught real bugs: a missing brace that
  greyed out half of `api.ts`, and a `Signals.py`/`signals.py` case mismatch that works on Windows
  but breaks on Linux. Before the final push it ran typecheck, lint, build and a browser run.
- **Rejected:** its first `signals.py` (~170 lines, regexes for personal data and prompt injection,
  timezone handling). It worked, but I could not defend every line, so I had it cut to rules I
  can explain — accepting that TKT-1004/1008 are no longer flagged (see Trade-offs).
- **Rejected:** its first plan, made before it had seen the repo — a generic OpenAI chatbot. The
  agent already exists; the product is the tool for the humans behind it, and W1/W2 need no LLM.
