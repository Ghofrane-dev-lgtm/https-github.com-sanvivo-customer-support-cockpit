import type { TicketStatus, TrustLevel } from "./api";

export const STATUS_LABEL: Record<TicketStatus, string> = {
  open: "Offen",
  waiting_customer: "Wartet auf Kunde",
  escalated: "Eskaliert",
  closed: "Geschlossen",
};

// One colour per trust level, used everywhere, so Lena learns it once.
export const TRUST_STYLE: Record<TrustLevel, string> = {
  wrong: "bg-red-100 text-red-800 border-red-300",
  check: "bg-amber-100 text-amber-900 border-amber-300",
  ok: "bg-emerald-100 text-emerald-800 border-emerald-300",
  none: "bg-slate-100 text-slate-600 border-slate-300",
};

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("de-DE", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}
