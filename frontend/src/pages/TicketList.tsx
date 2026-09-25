import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type TicketSummary } from "@/lib/api";

// Deliberately plain. This is your starting point, not a model to follow.
const TicketList = () => {
  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listTickets().then((data) => {
      setTickets(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <p style={{ padding: 24 }}>Lädt …</p>;

  return (
    <div style={{ padding: 24, fontFamily: "system-ui, sans-serif" }}>
      <h1 style={{ fontSize: 20, marginBottom: 4 }}>Support-Cockpit</h1>
      <p style={{ color: "#666", marginBottom: 16 }}>{tickets.length} Tickets</p>

      <table cellPadding={6} style={{ borderCollapse: "collapse", width: "100%", fontSize: 13 }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid #ccc" }}>
            <th>ID</th>
            <th>Betreff</th>
            <th>Kunde</th>
            <th>Status</th>
            <th>Kategorie</th>
            <th>Priorität</th>
            <th>Aktualisiert</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((t) => (
            <tr key={t.id} style={{ borderBottom: "1px solid #eee" }}>
              <td>
                <Link to={`/tickets/${t.id}`}>{t.id}</Link>
              </td>
              <td>{t.subject}</td>
              <td>{t.customer.name}</td>
              <td>{t.status}</td>
              <td>{t.category}</td>
              <td>{t.priority}</td>
              <td>{new Date(t.updated_at).toLocaleString("de-DE")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TicketList;
