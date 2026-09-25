import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type Ticket } from "@/lib/api";

// Nothing here yet. The agent trace is available via api.getTrace(id),
// actions via api.addMessage and api.updateTicket.
const TicketDetail = () => {
  const { id } = useParams<{ id: string }>();
  const [ticket, setTicket] = useState<Ticket | null>(null);

  useEffect(() => {
    if (id) api.getTicket(id).then(setTicket);
  }, [id]);

  if (!ticket) return <p style={{ padding: 24 }}>Lädt …</p>;

  return (
    <div style={{ padding: 24, fontFamily: "system-ui, sans-serif", maxWidth: 800 }}>
      <Link to="/">← Zurück</Link>
      <h1 style={{ fontSize: 18, margin: "12px 0" }}>
        {ticket.id} — {ticket.subject}
      </h1>

      {ticket.messages.map((m) => (
        <div key={m.id} style={{ marginBottom: 12, fontSize: 13 }}>
          <b>{m.author ?? m.role}</b>
          <div style={{ whiteSpace: "pre-wrap" }}>{m.text}</div>
        </div>
      ))}
    </div>
  );
};

export default TicketDetail;
