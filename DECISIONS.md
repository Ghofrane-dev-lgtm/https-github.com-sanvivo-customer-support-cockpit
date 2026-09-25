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
Claude Code (via claude.ai): explained the codebase and task, proposed the server/client split,
and wrote the code with me. I built the backend part step by step (`signals.py`, the `main.py`
wiring, the types in `api.ts`) and checked each step against the seed data; the frontend
components were added by Claude Code and reviewed by me.
Rejected / changed: TODO — write your own (e.g. a first, longer rule set that was too complex to
explain line by line → replaced by a simpler one; fetching every trace from the browser → too slow).
