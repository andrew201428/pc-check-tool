const refreshBtn = document.getElementById('refreshBtn');
const contentArea = document.getElementById('contentArea');
const sectionTitle = document.getElementById('sectionTitle');
const sectionDesc = document.getElementById('sectionDesc');
const navItems = document.querySelectorAll('.nav-item');
const themeToggleSidebar = document.getElementById('themeToggleSidebar');

let currentReport = null;
let currentSection = 'overview';

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let value = bytes;
  let unitIndex = 0;

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }

  return `${value.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

function formatPercent(rawValue) {
  const value = Number(rawValue) || 0;
  return `${Math.max(0, Math.min(100, value)).toFixed(1)}%`;
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function computeHealthScore(data) {
  const memory = data.memory || {};
  const storage = data.storage || [];
  const totalStorage = storage.reduce((sum, drive) => sum + (Number(drive.size) || 0), 0);
  const freeStorage = storage.reduce((sum, drive) => sum + (Number(drive.available) || 0), 0);

  const memoryFreeRatio = (Number(memory.free) || 0) / (Number(memory.total) || 1);
  const storageFreeRatio = freeStorage / (totalStorage || 1);
  const rawScore = ((memoryFreeRatio * 0.5) + (storageFreeRatio * 0.5)) * 100;
  return clamp(Math.round(rawScore), 0, 100);
}

function getLocalHistory() {
  try {
    const raw = localStorage.getItem('pc-check-history');
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory(data) {
  const history = getLocalHistory();
  const snapshot = {
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    health: computeHealthScore(data),
    memory: clamp(((Number(data.memory?.used) || 0) / (Number(data.memory?.total) || 1)) * 100, 0, 100),
    storage: clamp(
      ((data.storage || []).reduce((sum, drive) => sum + (Number(drive.used) || 0), 0) /
      ((data.storage || []).reduce((sum, drive) => sum + (Number(drive.size) || 0), 0) || 1)) * 100,
      0,
      100
    )
  };

  const nextHistory = [...history, snapshot].slice(-10);
  localStorage.setItem('pc-check-history', JSON.stringify(nextHistory));
}

function renderOverview(data) {
  const os = data.os || {};
  const cpu = data.cpu || {};
  const memory = data.memory || {};
  const storage = data.storage || [];
  const battery = data.battery || {};
  const health = computeHealthScore(data);
  const memoryUsed = clamp(((Number(memory.used) || 0) / (Number(memory.total) || 1)) * 100, 0, 100);
  const storageUsed = clamp(
    ((storage.reduce((sum, drive) => sum + (Number(drive.used) || 0), 0)) /
    ((storage.reduce((sum, drive) => sum + (Number(drive.size) || 0), 0) || 1))) * 100,
    0,
    100
  );
  const statusText = health >= 70 ? 'Healthy' : health >= 45 ? 'Watch' : 'Low';
  const statusStyle = health >= 70 ? 'rgba(52, 211, 153, 0.12)' : health >= 45 ? 'rgba(251, 191, 36, 0.12)' : 'rgba(251, 113, 133, 0.12)';
  const statusColor = health >= 70 ? 'var(--success)' : health >= 45 ? 'var(--warning)' : 'var(--danger)';

  contentArea.innerHTML = `
    <div class="section">
      <div class="panel hero-section">
        <div class="hero-info">
          <span class="status-pill" style="background: ${statusStyle}; color: ${statusColor};">${statusText}</span>
          <h2 style="margin: 0; font-size: 1.6rem;">System is ${statusText.toLowerCase()}</h2>
          <p style="margin: 0; color: var(--muted);">Last synced: ${new Date(data.generatedAt || Date.now()).toLocaleString()}</p>
        </div>
        <div class="health-block">
          <div class="health-meta">
            <span>Health</span>
            <strong>${health}/100</strong>
          </div>
          <div class="health-meter">
            <div class="health-fill" style="width: ${health}%"></div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <h3>Quick Stats</h3>
        </div>
        <div class="grid-cards">
          <div class="card">
            <div class="card-label">Platform</div>
            <div class="card-value">${data.os?.platform || 'Unknown'}</div>
          </div>
          <div class="card">
            <div class="card-label">CPU</div>
            <div class="card-value">${(cpu.brand || 'Unknown').split(' ')[0]}</div>
          </div>
          <div class="card">
            <div class="card-label">Total RAM</div>
            <div class="card-value">${formatBytes(memory.total || 0)}</div>
          </div>
          <div class="card">
            <div class="card-label">Free RAM</div>
            <div class="card-value" style="color: var(--success);">${formatBytes(memory.free || 0)}</div>
          </div>
          <div class="card">
            <div class="card-label">Cores</div>
            <div class="card-value">${cpu.cores || 'Unknown'}</div>
          </div>
          <div class="card">
            <div class="card-label">Drives</div>
            <div class="card-value">${storage.length || 0}</div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <h3>Performance Metrics</h3>
        </div>
        <div class="charts-grid">
          <div class="chart-card">
            <div class="metric-head">
              <span>Memory</span>
              <strong>${formatPercent(memoryUsed)}</strong>
            </div>
            <div class="meter-track">
              <div class="meter-fill" style="width: ${memoryUsed}%; background: linear-gradient(90deg, #60a5fa, #38bdf8);"></div>
            </div>
          </div>
          <div class="chart-card">
            <div class="metric-head">
              <span>Storage</span>
              <strong>${formatPercent(storageUsed)}</strong>
            </div>
            <div class="meter-track">
              <div class="meter-fill" style="width: ${storageUsed}%; background: linear-gradient(90deg, #2dd4bf, #67e8f9);"></div>
            </div>
          </div>
          <div class="chart-card">
            <div class="metric-head">
              <span>Battery</span>
              <strong>${battery.percent ? `${battery.percent}%` : 'N/A'}</strong>
            </div>
            <div class="meter-track">
              <div class="meter-fill" style="width: ${(battery.percent || 0)}%; background: linear-gradient(90deg, #fbbf24, #f59e0b);"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderHardware(data) {
  const os = data.os || {};
  const cpu = data.cpu || {};
  const memory = data.memory || {};
  const gpus = data.graphics?.controllers || data.graphics || [];
  const gpuEntries = Array.isArray(gpus) ? gpus : [gpus].filter(Boolean);

  contentArea.innerHTML = `
    <div class="section">
      <div class="panel">
        <div class="panel-header"><h3>System Information</h3></div>
        <div class="info-grid">
          <div class="info-item"><span class="key">OS</span><span class="value">${os.distro || 'Unknown'} ${os.release || ''}</span></div>
          <div class="info-item"><span class="key">Kernel</span><span class="value">${os.kernel || 'Unknown'}</span></div>
          <div class="info-item"><span class="key">Architecture</span><span class="value">${os.arch || 'Unknown'}</span></div>
          <div class="info-item"><span class="key">Platform</span><span class="value">${os.platform || 'Unknown'}</span></div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header"><h3>CPU Details</h3></div>
        <div class="info-grid">
          <div class="info-item"><span class="key">Brand</span><span class="value">${cpu.brand || 'Unknown'}</span></div>
          <div class="info-item"><span class="key">Cores</span><span class="value">${cpu.cores || 'Unknown'}</span></div>
          <div class="info-item"><span class="key">Logical processors</span><span class="value">${cpu.physicalCores || 'Unknown'}</span></div>
          <div class="info-item"><span class="key">Speed</span><span class="value">${cpu.speed ? `${cpu.speed} GHz` : 'Unknown'}</span></div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header"><h3>Memory</h3></div>
        <div class="info-grid">
          <div class="info-item"><span class="key">Total</span><span class="value">${formatBytes(memory.total || 0)}</span></div>
          <div class="info-item"><span class="key">Used</span><span class="value">${formatBytes(memory.used || 0)}</span></div>
          <div class="info-item"><span class="key">Free</span><span class="value">${formatBytes(memory.free || 0)}</span></div>
          <div class="info-item"><span class="key">Available</span><span class="value">${formatBytes(memory.available || 0)}</span></div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header"><h3>GPU</h3></div>
        <div class="list-rows">
          ${gpuEntries.map((gpu) => `
            <div class="list-item">
              <div><strong>${gpu.model || gpu.name || 'GPU'}</strong><br><small>${gpu.vendor || 'Unknown'}</small></div>
              <div><strong>${gpu.vram || gpu.memoryTotal || 'N/A'}</strong></div>
            </div>
          `).join('') || '<div class="list-item">No GPU data available</div>'}
        </div>
      </div>
    </div>
  `;
}

function renderStorage(data) {
  const storage = data.storage || [];
  contentArea.innerHTML = `
    <div class="section">
      <div class="panel">
        <div class="panel-header"><h3>Storage Drives</h3></div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>Drive</th><th>Type</th><th>Size</th><th>Used</th><th>Available</th><th>Used %</th></tr>
            </thead>
            <tbody>
              ${(storage || []).map((drive) => `
                <tr>
                  <td>${drive.mount || 'Disk'}</td>
                  <td>${drive.type || 'Disk'}</td>
                  <td>${formatBytes(drive.size || 0)}</td>
                  <td>${formatBytes(drive.used || 0)}</td>
                  <td>${formatBytes(drive.available || 0)}</td>
                  <td>${formatPercent(drive.use || 0)}</td>
                </tr>
              `).join('') || '<tr><td colspan="6">No storage data</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}

function renderNetwork(data) {
  const network = data.network || [];
  const users = data.users || [];
  contentArea.innerHTML = `
    <div class="section">
      <div class="panel">
        <div class="panel-header"><h3>Network Interfaces</h3></div>
        <div class="list-rows">
          ${(network || []).map((nic) => `
            <div class="list-item">
              <div><strong>${nic.name || 'NIC'}</strong><br><small>${nic.type || 'Unknown'} • ${nic.mac || 'No MAC'}</small></div>
              <div style="text-align: right;"><strong>${nic.ip4 || 'No IPv4'}</strong><br><small>${nic.ip6 || 'No IPv6'}</small></div>
            </div>
          `).join('') || '<div class="list-item">No network interfaces found</div>'}
        </div>
      </div>

      <div class="panel">
        <div class="panel-header"><h3>Users</h3></div>
        <div class="list-rows">
          ${(users || []).map((user) => `
            <div class="list-item">
              <div><strong>${user.user || 'Unknown'}</strong><br><small>${user.tty || 'N/A'}</small></div>
              <div><small>${user.date || 'N/A'}</small></div>
            </div>
          `).join('') || '<div class="list-item">No user data available</div>'}
        </div>
      </div>
    </div>
  `;
}

function renderProcesses(data) {
  const processes = data.processes?.list || [];

  contentArea.innerHTML = `
    <div class="section">
      <div class="panel">
        <div class="panel-header"><h3>Top Processes</h3></div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>Name</th><th>PID</th><th>CPU</th><th>Memory</th><th>Action</th></tr>
            </thead>
            <tbody>
              ${(processes || []).map((proc) => `
                <tr>
                  <td>${proc.name || 'Unknown'}</td>
                  <td>${proc.pid || 'N/A'}</td>
                  <td>${proc.cpu || 0}</td>
                  <td>${formatBytes((proc.mem || 0) * 1024 * 1024)}</td>
                  <td><button class="btn btn-secondary" data-kill-pid="${proc.pid}" type="button">Kill</button></td>
                </tr>
              `).join('') || '<tr><td colspan="5">No process data</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;

  document.querySelectorAll('[data-kill-pid]').forEach((button) => {
    button.addEventListener('click', async () => {
      const pid = button.dataset.killPid;
      try {
        const response = await fetch(`/api/processes/${pid}/kill`, { method: 'POST' });
        const result = await response.json();
        if (result.success) {
          alert(`Process ${pid} terminated.`);
          fetchSystemData();
        } else {
          alert(result.error || 'Unable to terminate process.');
        }
      } catch (error) {
        alert('Unable to terminate process.');
      }
    });
  });
}

function renderAlerts(data) {
  const health = computeHealthScore(data);
  const memoryUsed = clamp(((Number(data.memory?.used) || 0) / (Number(data.memory?.total) || 1)) * 100, 0, 100);
  const storageUsed = clamp(
    ((data.storage || []).reduce((sum, drive) => sum + (Number(drive.used) || 0), 0) /
     ((data.storage || []).reduce((sum, drive) => sum + (Number(drive.size) || 0), 0) || 1)) * 100,
    0,
    100
  );
  const cpuLoad = Number(data.load?.currentLoad || 0);
  const batteryPercent = Number(data.battery?.percent || 0);

  const alerts = [
    { label: 'Health score', value: `${health}/100`, status: health >= 70 ? 'Healthy' : health >= 45 ? 'Watch' : 'Critical', tone: health >= 70 ? 'success' : health >= 45 ? 'warning' : 'danger' },
    { label: 'Memory', value: formatPercent(memoryUsed), status: memoryUsed < 75 ? 'Healthy' : memoryUsed < 90 ? 'Watch' : 'High', tone: memoryUsed < 75 ? 'success' : memoryUsed < 90 ? 'warning' : 'danger' },
    { label: 'Storage', value: formatPercent(storageUsed), status: storageUsed < 75 ? 'Healthy' : storageUsed < 90 ? 'Watch' : 'High', tone: storageUsed < 75 ? 'success' : storageUsed < 90 ? 'warning' : 'danger' },
    { label: 'CPU Load', value: `${cpuLoad.toFixed(1)}%`, status: cpuLoad < 75 ? 'Healthy' : cpuLoad < 90 ? 'Watch' : 'Critical', tone: cpuLoad < 75 ? 'success' : cpuLoad < 90 ? 'warning' : 'danger' },
    { label: 'Battery', value: `${batteryPercent}%`, status: batteryPercent > 20 ? 'Healthy' : 'Low', tone: batteryPercent > 20 ? 'success' : 'warning' }
  ];

  const history = getLocalHistory();

  contentArea.innerHTML = `
    <div class="section">
      <div class="panel">
        <div class="panel-header"><h3>System Alerts</h3></div>
        <div class="alert-grid">
          ${alerts.map((alert) => `
            <div class="alert-card">
              <div class="a-label">${alert.label}</div>
              <div class="a-value">${alert.value}</div>
              <span class="a-status" style="${alert.tone === 'success' ? 'background: rgba(52,211,153,0.12); color: var(--success);' : alert.tone === 'warning' ? 'background: rgba(251,191,36,0.12); color: var(--warning);' : 'background: rgba(251,113,133,0.12); color: var(--danger);'}">${alert.status}</span>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="panel">
        <div class="panel-header"><h3>Recent History</h3></div>
        <div class="history-list">
          ${(history.length ? history : [{ time: 'No history yet', health: 0, memory: 0, storage: 0 }]).map((entry) => `
            <div class="history-item">
              <div>
                <strong>${entry.time}</strong><br>
                <small>Health ${entry.health || 0}%</small>
              </div>
              <div class="bar-mini"><span style="width: ${(entry.health || 0)}%"></span></div>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;
}

function renderExport() {
  contentArea.innerHTML = `
    <div class="section">
      <div class="panel">
        <div class="panel-header"><h3>Export Report</h3></div>
        <p style="margin: 0 0 18px; color: var(--muted);">Download or save a snapshot of the current system state.</p>
        <div class="export-actions">
          <button class="export-btn" id="exportJsonAction" type="button">
            <div class="icon">📋</div>
            <div class="label">JSON</div>
            <div class="desc">Raw system data</div>
          </button>
          <button class="export-btn" id="exportHtmlAction" type="button">
            <div class="icon">📄</div>
            <div class="label">HTML</div>
            <div class="desc">Readable report</div>
          </button>
          <button class="export-btn" id="saveReportAction" type="button">
            <div class="icon">💾</div>
            <div class="label">Save</div>
            <div class="desc">Store to reports folder</div>
          </button>
        </div>
      </div>
    </div>
  `;

  document.getElementById('exportJsonAction').addEventListener('click', exportJson);
  document.getElementById('exportHtmlAction').addEventListener('click', exportHtml);
  document.getElementById('saveReportAction').addEventListener('click', saveReport);
}

function downloadFile(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function exportJson() {
  if (!currentReport) return alert('No report data available yet.');
  const json = JSON.stringify(currentReport, null, 2);
  downloadFile(`pc-check-report-${Date.now()}.json`, json, 'application/json');
}

function exportHtml() {
  if (!currentReport) return alert('No report data available yet.');
  const health = computeHealthScore(currentReport);
  const storageText = (currentReport.storage || []).map((drive) => `
    <tr>
      <td>${drive.mount || 'Disk'}</td>
      <td>${drive.type || 'Disk'}</td>
      <td>${formatBytes(drive.size || 0)}</td>
      <td>${formatBytes(drive.used || 0)}</td>
      <td>${formatBytes(drive.available || 0)}</td>
      <td>${formatPercent(drive.use || 0)}</td>
    </tr>`).join('');

  const html = `<!DOCTYPE html>
  <html>
    <head>
      <meta charset="UTF-8" />
      <title>PC Check Report</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 32px; color: #111827; }
        h1 { margin-bottom: 8px; }
        .meta { color: #475569; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 16px; }
        th, td { border: 1px solid #d1d5db; padding: 10px; text-align: left; }
        th { background: #f3f4f6; }
      </style>
    </head>
    <body>
      <h1>PC Check Report</h1>
      <div class="meta">Generated: ${new Date(currentReport.generatedAt || Date.now()).toLocaleString()}</div>
      <p><strong>System:</strong> ${currentReport.os?.distro || 'Unknown'} ${currentReport.os?.release || ''}</p>
      <p><strong>CPU:</strong> ${currentReport.cpu?.brand || 'Unknown'}</p>
      <p><strong>Health score:</strong> ${health}/100</p>
      <table>
        <thead>
          <tr><th>Drive</th><th>Type</th><th>Size</th><th>Used</th><th>Available</th><th>Used %</th></tr>
        </thead>
        <tbody>${storageText}</tbody>
      </table>
    </body>
  </html>`;

  downloadFile(`pc-check-report-${Date.now()}.html`, html, 'text/html');
}

async function saveReport() {
  try {
    const response = await fetch('/api/system');
    const data = await response.json();
    const saveResponse = await fetch('/api/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await saveResponse.json();
    if (result.success) {
      window.open(result.path, '_blank');
      alert(`Report saved: ${result.filename}`);
    }
  } catch (error) {
    alert('Unable to save report.');
  }
}

async function fetchSystemData() {
  try {
    const response = await fetch('/api/system');
    const data = await response.json();
    currentReport = data;
    saveHistory(data);
    renderSection(currentSection);
  } catch (error) {
    contentArea.innerHTML = '<div class="panel"><p>Unable to fetch system data.</p></div>';
  }
}

function renderSection(section) {
  currentSection = section;
  navItems.forEach((item) => item.classList.toggle('active', item.dataset.section === section));
  const titles = {
    overview: 'Overview',
    hardware: 'Hardware',
    storage: 'Storage',
    network: 'Network',
    processes: 'Processes',
    alerts: 'Alerts',
    export: 'Export'
  };
  const descriptions = {
    overview: 'Real-time diagnostics and system health',
    hardware: 'CPU, memory, and GPU information',
    storage: 'Disk drives and storage capacity',
    network: 'Network adapters and user details',
    processes: 'Running processes and resource usage',
    alerts: 'Health warnings and recent status history',
    export: 'Download or save your diagnostics report'
  };

  sectionTitle.textContent = titles[section] || 'Overview';
  sectionDesc.textContent = descriptions[section] || '';

  if (!currentReport) {
    contentArea.innerHTML = '<div class="panel"><p>Loading system data...</p></div>';
    return;
  }

  switch (section) {
    case 'overview': renderOverview(currentReport); break;
    case 'hardware': renderHardware(currentReport); break;
    case 'storage': renderStorage(currentReport); break;
    case 'network': renderNetwork(currentReport); break;
    case 'processes': renderProcesses(currentReport); break;
    case 'alerts': renderAlerts(currentReport); break;
    case 'export': renderExport(); break;
    default: renderOverview(currentReport);
  }
}

function applyTheme(theme) {
  const isLight = theme === 'light';
  document.body.classList.toggle('light', isLight);
  localStorage.setItem('pc-check-theme', theme);
}

navItems.forEach((item) => {
  item.addEventListener('click', () => renderSection(item.dataset.section));
});

refreshBtn.addEventListener('click', fetchSystemData);
themeToggleSidebar.addEventListener('click', () => {
  const nextTheme = document.body.classList.contains('light') ? 'dark' : 'light';
  applyTheme(nextTheme);
});

const savedTheme = localStorage.getItem('pc-check-theme') || 'dark';
applyTheme(savedTheme);
renderSection(currentSection);
fetchSystemData();
