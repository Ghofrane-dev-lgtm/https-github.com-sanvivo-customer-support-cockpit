export type TicketStatus = "open" | "waiting_customer" | "escalated" | "closed";
export type Priority = "low" | "medium" | "high";

export interface Customer {
  name: string | null;
  email: string | null;
  customer_since: string | null;
  orders: {
    order_id: string;
    date: string;
    items: string[];
    total_eur: number;
    status: string;
  }[];
}

export interface Message {
  id: string;
  role: "customer" | "agent" | "human";
  author: string | null;
  text: string;
  created_at: string;
}

export interface TicketSummary {
  id: string;
  subject: string;
  channel: string;
  status: TicketStatus;
  category: string | null;
  priority: Priority | null;
  assignee: string | null;
  handled_by_agent: boolean;
  escalated: boolean;
  created_at: string;
  updated_at: string;
  customer: Customer;
  message_count: number;
  last_message_at: string | null;
  last_message_preview: string | null;
  has_trace: boolean;
}

export interface Ticket extends TicketSummary {
  messages: Message[];
}

export type TraceStep =
  | { type: "thought"; content: string }
  | {
      type: "tool_call";
      tool: string;
      arguments: Record<string, unknown>;
      status: "ok" | "error";
      duration_ms: number;
      result: unknown;
    }
  | {
      type: "retrieval";
      query: string;
      hits: { source: string; score: number; snippet: string }[];
    }
  | { type: "answer"; content: string };

export interface Trace {
  ticket_id: string;
  model: string;
  confidence: number;
  latency_ms: number;
  started_at: string;
  steps: TraceStep[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Anfrage fehlgeschlagen (${res.status})`);
  }
  return res.json();
}

export const api = {
  listTickets: (params: { status?: string; category?: string; q?: string } = {}) => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v) as [string, string][],
    ).toString();
    return request<TicketSummary[]>(`/tickets${query ? `?${query}` : ""}`);
  },
  getTicket: (id: string) => request<Ticket>(`/tickets/${id}`),
  getTrace: (id: string) => request<Trace>(`/tickets/${id}/trace`),
  addMessage: (id: string, text: string) =>
    request<Ticket>(`/tickets/${id}/messages`, {
      method: "POST",
      body: JSON.stringify({ text, role: "human", author: "Lena" }),
    }),
  updateTicket: (id: string, patch: Partial<Pick<TicketSummary, "status" | "priority" | "category" | "assignee">>) =>
    request<Ticket>(`/tickets/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),
  llm: (messages: { role: string; content: string }[]) =>
    request<{ content: string; model: string }>("/llm", {
      method: "POST",
      body: JSON.stringify({ messages }),
    }),
  stats: () => request<Record<string, unknown>>("/stats"),
};
