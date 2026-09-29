:root {
  --bg: #07111f;
  --bg-alt: #0d1728;
  --panel: rgba(15, 23, 42, 0.8);
  --panel-strong: rgba(17, 24, 39, 0.9);
  --panel-soft: rgba(15, 23, 42, 0.55);
  --line: rgba(148, 163, 184, 0.18);
  --line-strong: rgba(148, 163, 184, 0.3);
  --text: #e5eef8;
  --muted: #9fb2c7;
  --accent: #67e8f9;
  --accent-strong: #38bdf8;
  --success: #34d399;
  --warning: #fbbf24;
  --danger: #fb7185;
  --shadow: rgba(2, 6, 23, 0.55);
  --card: rgba(15, 23, 42, 0.72);
  --chip: rgba(103, 232, 249, 0.12);
  --meter-bg: rgba(255, 255, 255, 0.08);
}

body.light {
  --bg: #edf6ff;
  --bg-alt: #dfeaf7;
  --panel: rgba(255, 255, 255, 0.8);
  --panel-strong: rgba(255, 255, 255, 0.94);
  --panel-soft: rgba(255, 255, 255, 0.7);
  --line: rgba(15, 23, 42, 0.08);
  --line-strong: rgba(15, 23, 42, 0.12);
  --text: #102033;
  --muted: #52657f;
  --accent: #0ea5e9;
  --accent-strong: #0284c7;
  --success: #16a34a;
  --warning: #d97706;
  --danger: #e11d48;
  --shadow: rgba(15, 23, 42, 0.12);
  --card: rgba(255, 255, 255, 0.7);
  --chip: rgba(14, 165, 233, 0.08);
  --meter-bg: rgba(15, 23, 42, 0.08);
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  min-height: 100vh;
  font-family: Inter, "Segoe UI", sans-serif;
  background:
    radial-gradient(circle at top left, rgba(56, 189, 248, 0.18), transparent 30%),
    radial-gradient(circle at bottom right, rgba(52, 211, 153, 0.12), transparent 25%),
    linear-gradient(180deg, var(--bg) 0%, var(--bg-alt) 100%);
  color: var(--text);
  transition: background 0.2s ease, color 0.2s ease;
}

button {
  font: inherit;
  border: none;
  cursor: pointer;
}

.bg-orb {
  position: fixed;
  width: 420px;
  height: 420px;
  filter: blur(90px);
  opacity: 0.15;
  pointer-events: none;
  z-index: 0;
}

.orb-1 {
  top: -120px;
  left: -30px;
  background: #38bdf8;
}

.orb-2 {
  right: -80px;
  bottom: -120px;
  background: #34d399;
}

.page-shell {
  position: relative;
  z-index: 1;
  max-width: 1280px;
  margin: 0 auto;
  padding: 28px 24px 40px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 20px;
}

.brand-wrap {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-mark {
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  border-radius: 18px;
  font-weight: 800;
  font-size: 1.1rem;
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  color: #04131e;
  box-shadow: 0 16px 28px rgba(56, 189, 248, 0.25);
}

.eyebrow {
  margin: 0 0 4px;
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 700;
}

h1, h2, h3, p {
  margin: 0;
}

h1 {
  font-size: clamp(2rem, 4vw, 2.7rem);
  line-height: 1.1;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-btn,
.secondary-btn,
.ghost-btn {
  border-radius: 12px;
  padding: 10px 16px;
  font-weight: 700;
  letter-spacing: 0.01em;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.2s ease;
}

.primary-btn {
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  color: #04131e;
  box-shadow: 0 12px 22px rgba(56, 189, 248, 0.28);
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--line-strong);
  color: var(--text);
}

.ghost-btn {
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid var(--line);
  color: var(--text);
}

.primary-btn:hover,
.secondary-btn:hover,
.ghost-btn:hover {
  transform: translateY(-1px);
}

.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: 22px;
  box-shadow: 0 20px 40px var(--shadow);
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 20px 22px;
  margin-bottom: 22px;
}

.hero-copy {
  display: grid;
  gap: 10px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  width: fit-content;
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(52, 211, 153, 0.12);
  color: var(--success);
  border: 1px solid rgba(52, 211, 153, 0.22);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero h2 {
  font-size: clamp(1.4rem, 2vw, 2rem);
}

.hero p {
  color: var(--muted);
}

.health-block {
  min-width: 240px;
  display: grid;
  gap: 12px;
}

.health-meta {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  color: var(--muted);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.health-meta strong {
  font-size: 2.1rem;
  letter-spacing: 0;
  color: var(--text);
}

.health-meter {
  height: 12px;
  background: var(--meter-bg);
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--line);
}

.health-fill {
  width: 50%;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--success), var(--accent), var(--warning));
  transition: width 0.3s ease;
}

.content {
  display: grid;
  gap: 22px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 16px;
}

.summary-card {
  background: linear-gradient(180deg, var(--panel-soft), var(--panel-strong));
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 18px;
  min-height: 120px;
  display: grid;
  align-content: center;
  box-shadow: 0 14px 28px var(--shadow);
}

.summary-card .label {
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.7rem;
  font-weight: 700;
}

.summary-card .value {
  margin-top: 12px;
  font-size: clamp(1.4rem, 2vw, 2.1rem);
  font-weight: 800;
  line-height: 1.2;
}

.chart-panel {
  padding: 18px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.chart-card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px;
}

.metric-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
  color: var(--muted);
  font-size: 0.8rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.metric-head strong {
  color: var(--text);
  font-size: 1rem;
  letter-spacing: 0;
  text-transform: none;
}

.meter-track {
  width: 100%;
  height: 14px;
  border-radius: 999px;
  background: var(--meter-bg);
  overflow: hidden;
  border: 1px solid var(--line);
}

.meter-fill {
  height: 100%;
  width: 0;
  border-radius: inherit;
  transition: width 0.25s ease;
}

.meter-blue { background: linear-gradient(90deg, #60a5fa, #38bdf8); }
.meter-cyan { background: linear-gradient(90deg, #2dd4bf, #67e8f9); }
.meter-green { background: linear-gradient(90deg, #34d399, #86efac); }

.two-column {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px;
}

.detail-panel,
.panel {
  padding: 18px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-header h3 {
  font-size: 1.1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.info-item {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 12px 14px;
}

.info-item .key {
  display: block;
  margin-bottom: 6px;
  color: var(--muted);
  font-size: 0.7rem;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.info-item .value {
  font-size: 1rem;
  font-weight: 700;
  word-break: break-word;
}

.performance-grid {
  display: grid;
  gap: 12px;
}

.performance-item {
  padding: 12px 14px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
}

.performance-item .row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-weight: 600;
}

.performance-item small {
  color: var(--muted);
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

th, td {
  text-align: left;
  padding: 11px 12px;
  border-bottom: 1px solid var(--line);
}

th {
  color: var(--muted);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.list-rows {
  display: grid;
  gap: 10px;
}

.list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--card);
  border: 1px solid var(--line);
}

.list-item small {
  color: var(--muted);
}

@media (max-width: 860px) {
  .hero,
  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .two-column {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .page-shell {
    padding: 18px 16px 30px;
  }

  .topbar-actions {
    width: 100%;
  }

  .topbar-actions > * {
    flex: 1 1 auto;
  }

  .hero {
    padding: 16px;
  }
}
