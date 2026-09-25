import type { TicketSummary } from "./api";

export type View = "todo" | "mine" | "all";

// Filter and rank the queue. Shared by the list and the j/k keyboard navigation.
export function visibleTickets(tickets: TicketSummary[], view: View, search: string) {
  const needle = search.trim().toLowerCase();
  return tickets
    .filter((t) => {
      if (view === "todo") return t.triage.score > 0;
      if (view === "mine") return t.assignee === "Lena";
      return true;
    })
    .filter(
      (t) =>
        !needle ||
        t.subject.toLowerCase().includes(needle) ||
        t.id.toLowerCase().includes(needle) ||
        (t.customer.name ?? "").toLowerCase().includes(needle),
    )
    .sort((a, b) => b.triage.score - a.triage.score);
}
