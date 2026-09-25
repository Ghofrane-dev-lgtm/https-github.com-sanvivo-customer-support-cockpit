"""Seed data for the support cockpit.

Tickets come from `data/tickets.json`. Two sets are generated here because they are too
bulky for the JSON file: the long complaint thread in TKT-1007, and the wave of tickets
about the DHL disruption at the Leipzig sorting centre.
"""

import json
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).parent / "data" / "tickets.json"

# Traces for these tickets sit in cold storage and load slowly.
SLOW_TRACE_TICKETS = {"TKT-1019", "TKT-1007", "TKT-2004"}

_LONG_THREAD = [
    ("customer", "Guten Tag, ich hatte am 16.02. bestellt und musste die Ware wegen Schimmelbefall reklamieren. Wie ist der Stand?"),
    ("agent", "Guten Tag Frau Obermeier, ich habe Ihre Reklamation aufgenommen und an unser Team übergeben. Sie erhalten innerhalb von drei Werktagen eine Rückmeldung."),
    ("customer", "Danke, ich warte."),
    ("customer", "Es sind jetzt vier Werktage vergangen und ich habe nichts gehört."),
    ("agent", "Das tut mir leid. Ich habe den Vorgang erneut an das Team weitergeleitet."),
    ("customer", "Das haben Sie letzte Woche auch schon geschrieben."),
    ("agent", "Ich verstehe Ihren Ärger. Der Vorgang liegt weiterhin beim zuständigen Team."),
    ("customer", "Können Sie mir sagen, wer dort zuständig ist?"),
    ("agent", "Zu einzelnen Mitarbeitenden kann ich Ihnen leider keine Auskunft geben."),
    ("customer", "Dann geben Sie mir bitte eine Telefonnummer."),
    ("agent", "Wir bieten aktuell keine telefonische Beratung an. Anfragen bearbeiten wir ausschließlich schriftlich."),
    ("customer", "Das ist wirklich nicht kundenfreundlich."),
    ("customer", "Hallo? Ist da noch jemand?"),
    ("agent", "Ich bin noch hier. Ihr Vorgang ist weiterhin in Bearbeitung."),
    ("customer", "Seit wann genau? Können Sie mir ein Datum nennen?"),
    ("agent", "Ihre Reklamation wurde am 19.02.2026 angelegt."),
    ("customer", "Das ist über zwei Wochen her."),
    ("agent", "Das ist korrekt. Ich habe den Vorgang mit einem Hinweis auf die Bearbeitungsdauer versehen."),
    ("customer", "Ich habe die Ware inzwischen entsorgt, wie mir geraten wurde. Habe ich damit meinen Anspruch verwirkt?"),
    ("agent", "Nein. Die Fotos, die Sie eingereicht haben, sind für die Bearbeitung ausreichend."),
    ("customer", "Welche Fotos? Ich habe nie welche eingereicht."),
    ("agent", "Entschuldigen Sie, das war eine Verwechslung. Bitte senden Sie uns Fotos der Ware."),
    ("customer", "Die Ware ist entsorgt. Das habe ich Ihnen gerade geschrieben."),
    ("agent", "Sie haben recht, das war mein Fehler. Ich vermerke, dass keine Fotos vorliegen."),
    ("customer", "Ich möchte jetzt einfach nur mein Geld zurück. 231 Euro."),
    ("agent", "Über die Höhe einer Erstattung entscheidet unsere Apothekenleitung. Ich kann Ihnen dazu keine Zusage machen."),
    ("customer", "Dann leiten Sie mich bitte an jemanden weiter, der das kann."),
    ("agent", "Ich habe den Vorgang eskaliert."),
    ("customer", "Das haben Sie jetzt viermal geschrieben."),
    ("customer", "Ich werde mich an die Verbraucherzentrale wenden."),
    ("agent", "Das ist selbstverständlich Ihr Recht. Ihr Vorgang bleibt bei uns in Bearbeitung."),
    ("customer", "Gibt es eine Vorgangsnummer, die ich angeben kann?"),
    ("agent", "Ihre Vorgangsnummer lautet SV-84120."),
    ("customer", "Das ist meine Bestellnummer."),
    ("agent", "Für Reklamationen verwenden wir dieselbe Nummer."),
    ("customer", "Also gut. Wann bekomme ich eine Antwort?"),
    ("agent", "Eine verbindliche Frist kann ich Ihnen nicht nennen."),
    ("customer", "Das ist Ihr Ernst?"),
    ("customer", "Ich bin seit 2023 Kundin bei Ihnen. So geht man nicht mit Menschen um."),
    ("agent", "Ich verstehe Ihre Enttäuschung und habe Ihre Rückmeldung vermerkt."),
    ("customer", "Ich frage jetzt zum dritten Mal: Wann wird mein Fall bearbeitet?"),
]


def _long_thread_messages() -> list[dict[str, Any]]:
    from datetime import datetime, timedelta

    start = datetime(2026, 2, 19, 10, 14)
    messages = []
    for i, (role, text) in enumerate(_LONG_THREAD):
        stamp = start + timedelta(hours=i * 8.5)
        messages.append(
            {
                "id": f"m{i + 1}",
                "role": role,
                "author": "Kathrin Obermeier" if role == "customer" else "Sanvivo Assistent",
                "text": text,
                "created_at": stamp.isoformat(timespec="seconds"),
            }
        )
    return messages


_DHL_WAVE = [
    ("Sendung hängt seit vier Tagen fest", "Meine Sendung steht seit Donnerstag auf \"Sendung wird sortiert\" und bewegt sich nicht. Was ist da los?", "Rebecca Lindner", "r.lindner@gmx.de", "SV-88320"),
    ("Keine Bewegung im Tracking", "Guten Tag, im Tracking tut sich seit Tagen nichts mehr. Letzter Stand Leipzig. Können Sie nachsehen?", "Ahmed Fahmy", "a.fahmy@web.de", "SV-88324"),
    ("Wo ist mein Paket?", "seit 4 tagen keine änderung im tracking. langsam brauche ich das dringend.", "Nils Baumgartner", "nils.b@posteo.de", "SV-88331"),
    ("Lieferverzögerung", "Sehr geehrte Damen und Herren, meine Sendung verzögert sich offenbar erheblich. Gibt es dazu eine Information Ihrerseits?", "Christa Vogel", "christa.vogel@t-online.de", "SV-88336"),
    ("Paket verschollen?", "Mein Paket ist laut DHL seit dem 05.03. im Verteilzentrum Leipzig und wurde seitdem nicht weitergeleitet. Ist das verloren gegangen?", "Sven Rothe", "s.rothe@mailbox.org", "SV-88341"),
    ("Sendung steckt fest — Therapie unterbrochen", "Ich brauche die Lieferung dringend, meine Vorräte sind aufgebraucht. Das Paket hängt in Leipzig fest. Können Sie neu versenden?", "Miriam Kastner", "m.kastner@gmail.com", "SV-88345"),
    ("Tracking seit Tagen unverändert", "Hallo, gleiche Frage wie sicher viele: Tracking steht still, Stand Leipzig. Danke für eine kurze Info.", "Jonas Wiegand", "j.wiegand@icloud.com", "SV-88349"),
    ("Verzögerung Leipzig", "Ist bei DHL gerade etwas los? Meine Sendung kommt nicht voran.", "Beate Schuhmacher", "b.schuhmacher@freenet.de", "SV-88352"),
]


def _dhl_wave_tickets() -> list[dict[str, Any]]:
    from datetime import datetime, timedelta

    base = datetime(2026, 3, 9, 7, 5)
    tickets = []
    for i, (subject, text, name, email, order_id) in enumerate(_DHL_WAVE):
        created = base + timedelta(minutes=i * 23)
        answered = created + timedelta(minutes=2)
        tickets.append(
            {
                "id": f"TKT-{2001 + i}",
                "subject": subject,
                "channel": "email" if i % 3 else "chat",
                "status": "open",
                "category": "logistics",
                "priority": "high" if "dringend" in text.lower() else "medium",
                "assignee": None,
                "handled_by_agent": True,
                "escalated": False,
                "created_at": created.isoformat(timespec="seconds"),
                "updated_at": answered.isoformat(timespec="seconds"),
                "customer": {
                    "name": name,
                    "email": email,
                    "customer_since": "2025-05-01",
                    "orders": [
                        {
                            "order_id": order_id,
                            "date": "2026-03-05",
                            "items": ["Bedrocan 5g"],
                            "total_eur": 74.5,
                            "status": "versendet",
                        }
                    ],
                },
                "messages": [
                    {
                        "id": "m1",
                        "role": "customer",
                        "author": name,
                        "text": text,
                        "created_at": created.isoformat(timespec="seconds"),
                    },
                    {
                        "id": "m2",
                        "role": "agent",
                        "author": "Sanvivo Assistent",
                        "text": (
                            f"Guten Tag {name.split()[-1]},\n\nIhre Sendung {order_id} "
                            "befindet sich laut Sendungsverfolgung noch im Zustellprozess. "
                            "Bitte haben Sie etwas Geduld, DHL stellt in der Regel innerhalb "
                            "von ein bis zwei Werktagen zu.\n\nViele Grüße\nIhr Sanvivo Team"
                        ),
                        "created_at": answered.isoformat(timespec="seconds"),
                    },
                ],
                "trace": {
                    "ticket_id": f"TKT-{2001 + i}",
                    "model": "gpt-4o-mini",
                    "confidence": 0.69,
                    "latency_ms": 2400 + i * 130,
                    "started_at": created.isoformat(timespec="seconds"),
                    "steps": [
                        {
                            "type": "thought",
                            "content": "Kunde fragt nach dem Verbleib einer Sendung. Standardfall Sendungsverfolgung.",
                        },
                        {
                            "type": "tool_call",
                            "tool": "shipment_track",
                            "arguments": {"order_id": order_id},
                            "status": "ok",
                            "duration_ms": 480 + i * 20,
                            "result": {
                                "status": "in_transit",
                                "last_scan": "2026-03-05T22:14:00",
                                "last_location": "Verteilzentrum Leipzig",
                            },
                        },
                        {
                            "type": "retrieval",
                            "query": "Lieferzeit DHL Verzögerung",
                            "hits": [
                                {
                                    "source": "03-dhl-versand-policy.md",
                                    "score": 0.77,
                                    "snippet": "DHL stellt in der Regel innerhalb von ein bis zwei Werktagen nach Übergabe zu.",
                                }
                            ],
                        },
                        {
                            "type": "answer",
                            "content": "Hinweis auf reguläre Zustellzeit, Bitte um Geduld.",
                        },
                    ],
                },
            }
        )
    return tickets


def load_seed() -> list[dict[str, Any]]:
    tickets = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    by_id = {t["id"]: t for t in tickets}
    by_id["TKT-1007"]["messages"] = _long_thread_messages()
    return tickets + _dhl_wave_tickets()
