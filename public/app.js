* {
  box-sizing: border-box;
}

:root {
  --bg: #0f172a;
  --bg-soft: #111827;
  --panel: #1f2937;
  --panel-alt: #111827;
  --card: #0b1220;
  --line: rgba(148, 163, 184, 0.2);
  --text: #e5e7eb;
  --muted: #94a3b8;
  --accent: #38bdf8;
  --accent-strong: #0ea5e9;
  --success: #22c55e;
  --warning: #f59e0b;
  --danger: #ef4444;
}

body {
  margin: 0;
  font-family: Inter, "Segoe UI", sans-serif;
  background: linear-gradient(180deg, #020817 0%, var(--bg) 100%);
  color: var(--text);
}

button {
  appearance: none;
  border: none;
  cursor: pointer;
  transition: 0.2s ease;
}

.page-shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
  font-weight: 700;
}

h1, h2, h3, p {
  margin-top: 0;
}

h1 {
  margin-bottom: 0;
  font-size: clamp(2rem, 4vw, 3rem);
}

.primary-btn,
.secondary-btn {
  border-radius: 10px;
  padding: 10px 16px;
  font-weight: 700;
}

.primary-btn {
  background: var(--accent);
  color: #031321;
}

.primary-btn:hover {
  background: var(--accent-strong);
}

.secondary-btn {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--line);
}

.secondary-btn:hover {
  background: rgba(148, 163, 184, 0.08);
}

.content {
  display: grid;
  gap: 24px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 16px;
}

.card {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 18px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.2);
}

.card .label {
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.card .value {
  margin-top: 8px;
  font-size: 1.8rem;
  font-weight: 700;
}

.panel {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 18px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.info-item {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 12px;
}

.info-item .key {
  display: block;
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.info-item .value {
  font-size: 1rem;
  font-weight: 600;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

th, td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--line);
  text-align: left;
}

th {
  color: var(--muted);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 11px;
}

.list-rows {
  display: grid;
  gap: 10px;
}

.list-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 12px 14px;
}

@media (max-width: 640px) {
  .page-shell {
    padding: 16px;
  }

  .topbar,
  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
