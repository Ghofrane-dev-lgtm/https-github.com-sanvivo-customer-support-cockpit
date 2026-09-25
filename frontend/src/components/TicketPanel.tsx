import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type Ticket, type TicketSummary } from "@/lib/api";
import { STATUS_LABEL, TRUST_STYLE, formatDate } from "@/lib/format";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import TracePanel from "./TracePanel";

const ROLE_LABEL = { customer: "Kunde", agent: "KI-Agent", human: "Support" };

const TicketPanel = ({ id }: { id: string }) => {
  const queryClient = useQueryClient();
  const [reply, setReply] = useState("");

  const ticket = useQuery({ queryKey: ["ticket", id], queryFn: () => api.getTicket(id) });

  // Long threads (TKT-1007 has 41 messages): open at the newest message, not the oldest.
  const conversationEnd = useRef<HTMLDivElement>(null);
  const messageCount = ticket.data?.messages.length;
  useEffect(() => {
    conversationEnd.current?.scrollIntoView();
  }, [messageCount]);

  // Every action returns the updated ticket. We store it and refresh the queue.
  const onSaved = (updated: Ticket) => {
    queryClient.setQueryData(["ticket", id], updated);
    queryClient.invalidateQueries({ queryKey: ["tickets"] });
  };

  const update = useMutation({
    mutationFn: (patch: Partial<Pick<TicketSummary, "status" | "assignee">>) =>
      api.updateTicket(id, patch),
    onSuccess: onSaved,
  });

  const send = useMutation({
    mutationFn: async (text: string) => {
      await api.addMessage(id, text);
      // After Lena answers, the ticket is hers and waits for the customer.
      return api.updateTicket(id, { status: "waiting_customer", assignee: "Lena" });
    },
    onSuccess: (updated) => {
      setReply("");
      onSaved(updated);
    },
  });

  if (ticket.isPending) return <p className="p-6 text-sm">Lädt …</p>;
  if (ticket.isError) return <p className="p-6 text-sm text-red-700">{ticket.error.message}</p>;

  const t = ticket.data;
  const busy = update.isPending || send.isPending;
  const error = update.error ?? send.error;

  return (
    <div className="flex h-full flex-col">
      {/* Header: what is this, and what can I do about it */}
      <div className="space-y-3 border-b p-4">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div>
            <h1 className="text-lg font-semibold">{t.subject}</h1>
            <p className="text-sm text-muted-foreground">
              {t.id} · {t.customer.name ?? t.customer.email ?? "Unbekannt"} · {t.channel} ·{" "}
              {STATUS_LABEL[t.status]}
              {t.assignee && ` · bei ${t.assignee}`}
            </p>
          </div>
          <div className="flex gap-2">
            {t.assignee !== "Lena" && (
              <Button size="sm" disabled={busy} onClick={() => update.mutate({ assignee: "Lena", status: "open" })}>
                Übernehmen
              </Button>
            )}
            {t.status !== "escalated" && (
              <Button size="sm" variant="outline" disabled={busy} onClick={() => update.mutate({ status: "escalated" })}>
                Eskalieren
              </Button>
            )}
            {t.status !== "closed" && (
              <Button size="sm" variant="outline" disabled={busy} onClick={() => update.mutate({ status: "closed" })}>
                Schließen
              </Button>
            )}
          </div>
        </div>

        {/* The one-second verdict */}
        <div className={cn("rounded-md border p-3", TRUST_STYLE[t.trust.level])}>
          <p className="font-semibold">
            {t.trust.label}
            {t.confidence !== null && (
              <span className="font-normal"> · Agent war sich zu {Math.round(t.confidence * 100)} % sicher</span>
            )}
          </p>
          {t.flags.length > 0 && (
            <ul className="mt-1 list-disc pl-5 text-sm">
              {t.flags.map((f, i) => (
                <li key={i}>{f.label}</li>
              ))}
            </ul>
          )}
        </div>
        {error && <p className="text-sm text-red-700">{error.message}</p>}
      </div>

      {/* Body: conversation left, how the agent got there right */}
      <div className="grid flex-1 overflow-hidden lg:grid-cols-2">
        <div className="flex flex-col overflow-hidden border-r">
          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {t.messages.length === 0 && (
              <p className="text-sm text-muted-foreground">Keine Nachrichten – der Chat wurde abgebrochen.</p>
            )}
            {t.messages.map((m) => (
              <div
                key={m.id}
                className={cn(
                  "max-w-[90%] rounded-lg p-3 text-sm",
                  m.role === "customer" ? "bg-muted" : "ml-auto bg-blue-50",
                  m.role === "human" && "bg-emerald-50",
                )}
              >
                <p className="mb-1 text-xs text-muted-foreground">
                  {ROLE_LABEL[m.role]} · {m.author ?? ""} · {formatDate(m.created_at)}
                </p>
                <p className="whitespace-pre-wrap">{m.text}</p>
              </div>
            ))}
            <div ref={conversationEnd} />
          </div>
          <form
            className="space-y-2 border-t p-3"
            onSubmit={(e) => {
              e.preventDefault();
              if (reply.trim()) send.mutate(reply);
            }}
          >
            <textarea
              value={reply}
              onChange={(e) => setReply(e.target.value)}
              placeholder="Antwort an den Kunden …"
              rows={3}
              className="w-full rounded-md border p-2 text-sm"
            />
            <Button type="submit" size="sm" disabled={busy || !reply.trim()}>
              {send.isPending ? "Wird gesendet …" : "Antwort senden"}
            </Button>
          </form>
        </div>
        <div className="overflow-y-auto p-4">
          <h2 className="mb-2 text-sm font-semibold">So kam der Agent zu seiner Antwort</h2>
          <TracePanel ticketId={t.id} flags={t.flags} />
        </div>
      </div>
    </div>
  );
};

export default TicketPanel;
