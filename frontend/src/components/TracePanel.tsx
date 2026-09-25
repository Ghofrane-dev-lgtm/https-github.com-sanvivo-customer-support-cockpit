import { useQuery } from "@tanstack/react-query";
import { api, type Flag, type TraceStep } from "@/lib/api";
import { cn } from "@/lib/utils";

const STEP_TITLE: Record<TraceStep["type"], string> = {
  thought: "Überlegung",
  tool_call: "Werkzeug",
  retrieval: "Wissensdatenbank",
  answer: "Antwort",
};

interface Props {
  ticketId: string;
  flags: Flag[];
}

const TracePanel = ({ ticketId, flags }: Props) => {
  const trace = useQuery({
    queryKey: ["trace", ticketId],
    queryFn: () => api.getTrace(ticketId),
    retry: false, // a 404 means "agent never ran", retrying will not change that
    staleTime: Infinity, // a trace never changes once written
  });

  if (trace.isPending) {
    return <p className="text-sm text-muted-foreground">Agent-Protokoll wird geladen …</p>;
  }
  if (trace.isError) {
    const notFound = (trace.error as Error & { status?: number }).status === 404;
    return (
      <p className="text-sm text-muted-foreground">
        {notFound ? "Der Agent hat dieses Ticket nicht bearbeitet." : trace.error.message}
      </p>
    );
  }

  const { steps, confidence, model, latency_ms } = trace.data;
  return (
    <div className="space-y-2">
      <p className="text-xs text-muted-foreground">
        Konfidenz {Math.round(confidence * 100)} % · {model} · {latency_ms} ms
      </p>
      <ol className="space-y-2">
        {steps.map((step, i) => {
          const stepFlags = flags.filter((f) => f.step === i);
          return (
            <li
              key={i}
              className={cn(
                "rounded-md border p-2 text-sm",
                stepFlags.some((f) => f.severity === "danger") && "border-red-400 bg-red-50",
                stepFlags.some((f) => f.severity === "warn") && "border-amber-400 bg-amber-50",
              )}
            >
              <div className="text-xs font-semibold uppercase text-muted-foreground">
                {i + 1}. {STEP_TITLE[step.type]}
              </div>
              {stepFlags.map((f) => (
                <div key={f.code} className="text-xs font-semibold text-red-700">
                  ⚠ {f.label}
                </div>
              ))}
              <StepBody step={step} />
            </li>
          );
        })}
      </ol>
    </div>
  );
};

const StepBody = ({ step }: { step: TraceStep }) => {
  switch (step.type) {
    case "thought":
    case "answer":
      return <p>{step.content}</p>;
    case "tool_call":
      return (
        <div>
          <p>
            <code>{step.tool}</code> — {step.status === "ok" ? "erfolgreich" : "FEHLER"} ({step.duration_ms} ms)
          </p>
          <pre className="mt-1 overflow-x-auto rounded bg-muted p-2 text-xs">
            {JSON.stringify({ eingabe: step.arguments, ergebnis: step.result }, null, 2)}
          </pre>
        </div>
      );
    case "retrieval":
      return (
        <div>
          <p className="text-xs text-muted-foreground">Suche: „{step.query}"</p>
          {step.hits.length === 0 && <p>Keine Treffer.</p>}
          {step.hits.map((hit) => (
            <blockquote key={hit.source} className="mt-1 border-l-2 pl-2">
              <p>{hit.snippet}</p>
              <p className="text-xs text-muted-foreground">
                {hit.source} · Relevanz {hit.score.toFixed(2)}
              </p>
            </blockquote>
          ))}
        </div>
      );
  }
};

export default TracePanel;
