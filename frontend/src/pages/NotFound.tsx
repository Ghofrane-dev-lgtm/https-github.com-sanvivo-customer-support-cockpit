import { Link } from "react-router-dom";

const NotFound = () => (
  <div style={{ padding: 24 }}>
    <h1>Seite nicht gefunden</h1>
    <Link to="/">Zurück zur Ticketliste</Link>
  </div>
);

export default NotFound;
