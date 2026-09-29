:root {
  --bg: #07111f;
  --bg-alt: #0d1728;
  --sidebar: #0a141f;
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
}

body.light {
  --bg: #edf6ff;
  --bg-alt: #dfeaf7;
  --sidebar: #e0eaf7;
  --panel: rgba(255, 255, 255, 0.9);
  --panel-strong: rgba(255, 255, 255, 0.98);
  --panel-soft: rgba(255, 255, 255, 0.85);
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
  --card: rgba(255, 255, 255, 0.8);
  --chip: rgba(14, 165, 233, 0.08);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: linear-gradient(180deg, var(--bg) 0%, var(--bg-alt) 100%);
  color: var(--text);
  transition: background 0.2s ease, color 0.2s ease;
}
button { border: none; cursor: pointer; font: inherit; }
a { color: inherit; }

.app-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
}

.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: 240px;
  height: 100vh;
  background: var(--sidebar);
  border-right: 1px solid var(--line);
  padding: 22px 12px 18px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-header {
  padding: 4px 8px 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 800;
  color: var(--accent);
}

.logo svg { stroke: currentColor; }

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: transparent;
  color: var(--muted);
  transition: all 0.18s ease;
  font-weight: 600;
}

.nav-item:hover {
  background: rgba(148, 163, 184, 0.08);
  color: var(--text);
}

.nav-item.active {
  background: var(--accent);
  color: #04131e;
}

.nav-item svg {
  stroke: currentColor;
  flex-shrink: 0;
}

.sidebar-footer {
  display: flex;
  justify-content: center;
}

.theme-toggle {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: rgba(148, 163, 184, 0.08);
  color: var(--muted);
  display: grid;
  place-items: center;
}

.main-content {
  margin-left: 240px;
  padding: 28px 32px 40px;
  background: linear-gradient(180deg, var(--bg) 0%, var(--bg-alt) 100%);
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 26px;
}

.content-header h1 {
  margin: 0 0 4px;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
}

.subtitle {
  margin: 0;
  color: var(--muted);
}

.header-actions { display: flex; gap: 12px; }

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  border-radius: 12px;
  font-weight: 700;
  transition: transform 0.18s ease;
}

.btn:hover { transform: translateY(-1px); }

.btn-primary {
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  color: #04131e;
  box-shadow: 0 12px 22px rgba(56, 189, 248, 0.28);
}

.content-area {
  display: grid;
  gap: 22px;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 22px;
  box-shadow: 0 18px 40px var(--shadow);
  padding: 20px;
}

.hero-section {
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 18px;
}

.hero-info {
  display: grid;
  gap: 10px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
  border: 1px solid transparent;
}

.health-block {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px;
  display: grid;
  gap: 12px;
}

.health-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.75rem;
}

.health-meta strong {
  color: var(--text);
  font-size: 2rem;
}

.health-meter {
  height: 12px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  overflow: hidden;
  border: 1px solid var(--line);
}

.health-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--success), var(--accent), var(--warning));
}

.grid-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px;
  min-height: 110px;
  display: grid;
  align-content: center;
}

.card-label {
  color: var(--muted);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}

.card-value {
  font-size: clamp(1.3rem, 2vw, 2rem);
  font-weight: 800;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 12px;
  color: var(--muted);
  font-size: 0.8rem;
  text-transform: uppercase;
}

.metric-head strong {
  color: var(--text);
  font-size: 1rem;
  text-transform: none;
}

.meter-track {
  width: 100%;
  height: 14px;
  background: rgba(255,255,255,0.08);
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--line);
}

.meter-fill {
  height: 100%;
  width: 0;
  border-radius: inherit;
  transition: width 0.25s ease;
}

.two-column {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.info-item {
  padding: 12px 14px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
}

.info-item .key {
  display: block;
  color: var(--muted);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 6px;
}

.info-item .value {
  font-weight: 700;
  word-break: break-word;
}

.table-wrap { overflow-x: auto; }

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 620px;
}

th, td {
  padding: 11px 12px;
  text-align: left;
  border-bottom: 1px solid var(--line);
}

th {
  color: var(--muted);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.list-rows {
  display: grid;
  gap: 10px;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
}

.list-item small { color: var(--muted); }

.performance-grid {
  display: grid;
  gap: 12px;
}

.performance-item {
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--card);
  border: 1px solid var(--line);
}

.performance-item .row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.performance-item small {
  display: block;
  margin-top: 6px;
  color: var(--muted);
}

.export-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.export-btn {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px;
  text-align: left;
  display: grid;
  gap: 8px;
}

.export-btn:hover {
  border-color: var(--accent);
}

.export-btn .icon { font-size: 1.8rem; }
.export-btn .label { font-weight: 800; }
.export-btn .desc { color: var(--muted); font-size: 0.8rem; }

.alert-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 14px;
}

.alert-card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 16px;
}

.alert-card .a-label {
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.7rem;
}

.alert-card .a-value {
  margin-top: 8px;
  font-size: 1.4rem;
  font-weight: 800;
}

.alert-card .a-status {
  display: inline-block;
  margin-top: 10px;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
}

.history-list {
  display: grid;
  gap: 10px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  background: var(--card);
  border: 1px solid var(--line);
}

.bar-mini {
  width: 120px;
  height: 8px;
  background: rgba(255,255,255,0.08);
  border-radius: 999px;
  overflow: hidden;
}

.bar-mini > span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--success), var(--accent));
}

@media (max-width: 1024px) {
  .app-layout { grid-template-columns: 1fr; }
  .sidebar {
    position: relative;
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--line);
  }
  .main-content {
    margin-left: 0;
  }
  .hero-section, .two-column { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .main-content { padding: 20px 16px 32px; }
  .content-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-actions { width: 100%; }
  .btn { flex: 1; justify-content: center; }
}
