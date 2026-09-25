import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "@/lib/api";
import { visibleTickets, type View } from "@/lib/queue";
import TicketQueue from "@/components/TicketQueue";
import TicketPanel from "@/components/TicketPanel";

const Cockpit = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [view, setView] = useState<View>("todo");
  const [search, setSearch] = useState("");

  const tickets = useQuery({
    queryKey: ["tickets"],
    queryFn: () => api.listTickets(),
    refetchInterval: 30_000, // new tickets show up without a reload
  });

  // j / k jump to the next / previous ticket in the queue.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") return;
      if (e.key !== "j" && e.key !== "k") return;
      const list = visibleTickets(tickets.data ?? [], view, search);
      const index = list.findIndex((t) => t.id === id);
      const next = list[e.key === "j" ? index + 1 : Math.max(index - 1, 0)];
      if (next) navigate(`/tickets/${next.id}`);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [tickets.data, view, search, id, navigate]);

  return (
    <div className="flex h-screen bg-background text-foreground">
      <aside className="w-[380px] shrink-0 border-r">
        <div className="border-b px-3 py-2 font-semibold">Sanvivo Support-Cockpit</div>
        {tickets.isPending && <p className="p-3 text-sm">Lädt …</p>}
        {tickets.isError && <p className="p-3 text-sm text-red-700">{tickets.error.message}</p>}
        {tickets.data && (
          <TicketQueue
            tickets={tickets.data}
            selectedId={id}
            view={view}
            onViewChange={setView}
            search={search}
            onSearchChange={setSearch}
          />
        )}
      </aside>
      <main className="flex-1 overflow-hidden">
        {id ? (
          <TicketPanel key={id} id={id} />
        ) : (
          <p className="p-6 text-muted-foreground">Ticket links auswählen – oder j drücken.</p>
        )}
      </main>
    </div>
  );
};

export default Cockpit;
