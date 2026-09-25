# Sanvivo Support Cockpit

## Start
1. `cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
2. `cp .env.example .env` (OpenAI key optional — no feature needs it; `COCKPIT_NOW` pins the demo clock to the seed data)
3. `uvicorn main:app --reload --port 8000`
4. Second terminal: `cd frontend && npm install && npm run dev` → open http://localhost:5173

Design decisions: [DECISIONS.md](DECISIONS.md)

![Cockpit: ranked queue, trust verdict and agent trace](docs/screenshot.png)
