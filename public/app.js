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
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif;
  background: linear-gradient(180deg, var(--bg) 0%, var(--bg-alt) 100%);
  color: var(--text);
  transition: background 0.2s ease, color 0.2s ease;
}

button {
  font: inherit;
  border: none;
  cursor: pointer;
}

.app-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
}

.sidebar {
  background: var(--sidebar);
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  padding: 20px 12px;
  gap: 24px;
  position: fixed;
  left: 0;
  top: 0;
  width: 240px;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-header {
  padding: 0 8px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 800;
  font-size: 1rem;
  color: var(--accent);
}

.logo svg {
  stroke: var(--accent);
}

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
  font-weight: 500;
  font-size: 0.95rem;
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
  flex-shrink: 0;
  stroke: currentColor;
}

.sidebar-footer {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.theme-toggle {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(148, 163, 184, 0.08);
  color: var(--muted);
  display: grid;
  place-items: center;
  transition: all 0.18s ease;
}

.theme-toggle:hover {
  background: rgba(148, 163, 184, 0.12);
  color: var(--text);
}

.main-content {
  grid-column: 2;
  background: linear-gradient(180deg, var(--bg) 0%, var(--bg-alt) 100%);
  padding: 32px 40px;
  overflow-y: auto;
}

.content-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
}

.content-header h1 {
  font-size: 2rem;
  margin: 0 0 4px;
}

.subtitle {
  color: var(--muted);
  font-size: 0.95rem;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 12px;
  font-weight: 700;
  transition: all 0.18s ease;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  color: #04131e;
  box-shadow: 0 12px 22px rgba(56, 189, 248, 0.28);
}

.btn-primary:hover {
  transform: translateY(-1px);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--line-strong);
  color: var(--text);
}

.btn-secondary:hover {
  background: rgba(148, 163, 184, 0.08);
}

.content-area {
  display: grid;
  gap: 24px;
}

.section-hidden {
  display: none;
}

.section {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  backdrop-filter: blur(8px);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 20px 40px var(--shadow);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-header h3 {
  font-size: 1.1rem;
  margin: 0;
}

.hero-section {
  display: grid;
  gap: 20px;
  grid-template-columns: 1fr 280px;
}

.hero-info {
  display: grid;
  gap: 12px;
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
  align-items: baseline;
  color: var(--muted);
  font-size: 0.8rem;
  text-transform: uppercase;
}

.health-meta strong {
  color: var(--text);
  font-size: 2rem;
  letter-spacing: -0.01em;
}

.health-meter {
  height: 12px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--line);
}

.health-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--success), var(--accent), var(--warning));
  transition: width 0.3s ease;
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
  font-size: 1.3rem;
  font-weight: 800;
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
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
  border: 1px solid var(--line);
}

.meter-fill {
  height: 100%;
  width: 0;
  border-radius: inherit;
  transition: width 0.25s ease;
  background: linear-gradient(90deg, #60a5fa, #38bdf8);
}

.two-column {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.info-item {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 12px;
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
  font-size: 0.95rem;
  font-weight: 700;
  word-break: break-word;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

tr {
  border-bottom: 1px solid var(--line);
}

th, td {
  text-align: left;
  padding: 12px;
}

th {
  color: var(--muted);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
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

.export-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.export-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  padding: 16px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  transition: all 0.18s ease;
}

.export-btn:hover {
  background: var(--panel-soft);
  border-color: var(--accent);
}

.export-btn .icon {
  font-size: 1.8rem;
}

.export-btn .label {
  font-weight: 700;
  font-size: 0.95rem;
}

.export-btn .desc {
  color: var(--muted);
  font-size: 0.8rem;
}

@media (max-width: 1024px) {
  .app-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: absolute;
    left: -240px;
    width: 240px;
    z-index: 1000;
    transition: left 0.3s ease;
  }

  .sidebar.open {
    left: 0;
  }

  .main-content {
    grid-column: 1;
  }

  .two-column {
    grid-template-columns: 1fr;
  }

  .hero-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .main-content {
    padding: 20px 16px;
  }

  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .content-header h1 {
    font-size: 1.5rem;
  }

  .charts-grid,
  .grid-cards {
    grid-template-columns: 1fr;
  }
}
