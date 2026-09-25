import { Link } from "react-router-dom";
import type { TicketSummary } from "@/lib/api";
import { visibleTickets, type View } from "@/lib/queue";
import { STATUS_LABEL, TRUST_STYLE } from "@/lib/format";
import { cn } from "@/lib/utils";

const VIEWS: { key: View; label: string }[] = [
  { key: "todo", label: "Zu erledigen" },
  { key: "mine", label: "Meine" },
  { key: "all", label: "Alle" },
];

interface Props {
  tickets: TicketSummary[];
  selectedId?: string;
  view: View;
  onViewChange: (view: View) => void;
  search: string;
  onSearchChange: (search: string) => void;
}

const TicketQueue = ({ tickets, selectedId, view, onViewChange, search, onSearchChange }: Props) => {
  const shown = visibleTickets(tickets, view, search);

  return (
    <div className="flex h-full flex-col">
      <div className="space-y-2 border-b p-3">
        <div className="flex gap-1">
          {VIEWS.map((v) => (
            <button
              key={v.key}
              onClick={() => onViewChange(v.key)}
              className={cn(
                "rounded-md px-3 py-1 text-sm",
                view === v.key ? "bg-primary text-primary-foreground" : "hover:bg-muted",
              )}
            >
              {v.label}
            </button>
          ))}
        </div>
        <input
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Suchen: Betreff, Kunde, Ticket-ID …"
          className="w-full rounded-md border px-3 py-1.5 text-sm"
        />
        <p className="text-xs text-muted-foreground">
          {shown.length} Tickets · sortiert nach Dringlichkeit · j/k zum Wechseln
        </p>
      </div>

      <ul className="flex-1 overflow-y-auto">
        {shown.map((t) => (
          <li key={t.id}>
            <Link
              to={`/tickets/${t.id}`}
              className={cn(
                "block border-b px-3 py-2 hover:bg-muted",
                t.id === selectedId && "bg-muted",
              )}
            >
              <div className="flex items-center gap-2">
                <span
                  className={cn("shrink-0 whitespace-nowrap rounded border px-1.5 text-xs font-medium", TRUST_STYLE[t.trust.level])}
                >
                  {t.trust.label}
                </span>
                <span className="truncate text-sm font-medium">{t.subject}</span>
              </div>
              <div className="mt-1 flex gap-2 text-xs text-muted-foreground">
                <span>{t.id}</span>
                <span>{t.customer.name ?? t.customer.email ?? "Unbekannt"}</span>
                <span>{STATUS_LABEL[t.status]}</span>
                {t.assignee && <span>→ {t.assignee}</span>}
              </div>
              {t.triage.reasons.length > 0 && (
                <div className="mt-1 truncate text-xs text-red-700">
                  {t.triage.reasons.join(" · ")}
                </div>
              )}
            </Link>
          </li>
        ))}
        {shown.length === 0 && (
          <li className="p-6 text-center text-sm text-muted-foreground">Nichts zu tun 🎉</li>
        )}
      </ul>
    </div>
  );
};

export default TicketQueue;
