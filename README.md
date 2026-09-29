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

function renderOverview(data) {
  const os = data.os || {};
  const cpu = data.cpu || {};
  const memory = data.memory || {};
  const storage = data.storage || [];
  const battery = data.battery || {};
  const health = computeHealthScore(data);

  const memoryUsedPercent = clamp(((Number(memory.used) || 0) / (Number(memory.total) || 1)) * 100, 0, 100);
  const storageUsedPercent = clamp(
    ((storage.reduce((sum, drive) => sum + (Number(drive.used) || 0), 0)) /
      (storage.reduce((sum, drive) => sum + (Number(drive.size) || 0), 0) || 1)) * 100,
    0,
    100
  );

  const timestamp = new Date(data.generatedAt || Date.now()).toLocaleString();
  const statusText = health >= 70 ? 'Healthy' : health >= 45 ? 'Watch' : 'Low';
  const statusStyle = health >= 70 ? 'rgba(52, 211, 153, 0.12)' : health >= 45 ? 'rgba(251, 191, 36, 0.12)' : 'rgba(251, 113, 133, 0.12)';
  const statusColor = health >= 70 ? 'var(--success)' : health >= 45 ? 'var(--warning)' : 'var(--danger)';

  contentArea.innerHTML = `
    <div class="section">
      <div class="panel hero-section">
        <div class="hero-info">
          <div style="display: inline-flex; gap: 12px; align-items: flex-start;">
            <span class="status-pill" style="background: ${statusStyle}; color: ${statusColor};">${statusText}</span>
          </div>
          <h2 style="margin: 8px 0; font-size: 1.6rem;">System is ${statusText.toLowerCase()}</h2>
          <p style="color: var(--muted); margin: 0;">Last synced: ${timestamp}</p>
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
            <div class="card-value">${os.platform || 'Unknown'}</div>
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
              <strong>${formatPercent(memoryUsedPercent)}</strong>
            </div>
            <div class="meter-track">
              <div class="meter-fill" style="width: ${memoryUsedPercent}%; background: linear-gradient(90deg, #60a5fa, #38bdf8);"></div>
            </div>
          </div>
          <div class="chart-card">
            <div class="metric-head">
              <span>Storage</span>
              <strong>${formatPercent(storageUsedPercent)}</strong>
            </div>
            <div class="meter-track">
              <div class="meter-fill" style="width: ${storageUsedPercent}%; background: linear-gradient(90deg, #2dd4bf, #67e8f9);"></div>
            </div>
          </div>
          <div class="chart-card">
            <div class="metric-head">
              <span>Battery</span>
              <strong>${battery.percent ? battery.percent + '%' : 'N/A'}</strong>
            </div>
            <div class="meter-track">
              <div class="meter-fill" style="width: ${battery.percent || 0}%; background: linear-gradient(90deg, #fbbf24, #f59e0b);"></div>
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
  const versions = data.versions || {};

  const gpuEntries = Array.isArray(gpus) ? gpus : [gpus].filter(Boolean);

  contentArea.innerHTML = `
    <div class="section">
      <div class="panel">
        <div class="panel-header">
          <h3>System Information</h3>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <div class="key">OS</div>
            <div class="value">${os.distro || 'Unknown'} ${os.release || ''}</div>
          </div>
          <div class="info-item">
            <div class="key">Kernel</div>
            <div class="value">${os.kernel || 'Unknown'}</div>
          </div>
          <div class="info-item">
            <div class="key">Architecture</div>
            <div class="value">${os.arch || 'Unknown'}</div>
          </div>
          <div class="info-item">
            <div class="key">Platform</div>
            <div class="value">${os.platform || 'Unknown'}</div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <h3>CPU Details</h3>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <div class="key">Brand</div>
            <div class="value">${cpu.brand || 'Unknown'}</div>
          </div>
          <div class="info-item">
            <div class="key">Cores</div>
            <div class="value">${cpu.cores || 'Unknown'}</div>
          </div>
          <div class="info-item">
            <div class="key">Logical Processors</div>
            <div class="value">${cpu.physicalCores || 'Unknown'}</div>
          </div>
          <div class="info-item">
            <div class="key">Speed</div>
            <div class="value">${cpu.speed ? cpu.speed + ' GHz' : 'Unknown'}</div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <h3>Memory</h3>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <div class="key">Total</div>
            <div class="value">${formatBytes(memory.total || 0)}</div>
          </div>
          <div class="info-item">
            <div class="key">Used</div>
            <div class="value">${formatBytes(memory.used || 0)}</div>
          </div>
          <div class="info-item">
            <div class="key">Free</div>
            <div class="value">${formatBytes(memory.free || 0)}</div>
          </div>
          <div class="info-item">
            <div class="key">Available</div>
            <div class="value">${formatBytes(memory.available || 0)}</div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <h3>GPU</h3>
        </div>
        <div class="list-rows">
          ${gpuEntries.map((gpu) => `
            <div class="list-item">
              <div>
                <strong>${gpu.model || gpu.name || 'GPU'}</strong><br />
                <small>${gpu.vendor || 'Unknown'}</small>
              </div>
              <div>
                <strong>${gpu.vram || gpu.memoryTotal || 'N/A'}</strong>
              </div>
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
        <div class="panel-header">
          <h3>Storage Drives</h3>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Drive</th>
                <th>Type</th>
                <th>Size</th>
                <th>Used</th>
                <th>Available</th>
                <th>Used %</th>
              </tr>
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
        <div class="panel-header">
          <h3>Network Interfaces</h3>
        </div>
        <div class="list-rows">
          ${(network || []).map((nic) => `
            <div class="list-item">
              <div>
                <strong>${nic.name || 'NIC'}</strong><br />
                <small>${nic.type || 'Unknown'} • ${nic.mac || 'No MAC'}</small>
              </div>
              <div style="text-align: right;">
                <strong>${nic.ip4 || 'No IPv4'}</strong><br />
                <small>${nic.ip6 || 'No IPv6'}</small>
              </div>
            </div>
          `).join('') || '<div class="list-item">No network interfaces found</div>'}
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <h3>Users</h3>
        </div>
        <div class="list-rows">
          ${(users || []).map((user) => `
            <div class="list-item">
              <div>
                <strong>${user.user || 'Unknown'}</strong><br />
                <small>${user.tty || 'N/A'}</small>
              </div>
              <div>
                <small>${user.date || 'N/A'}</small>
              </div>
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
        <div class="panel-header">
          <h3>Top Processes</h3>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>PID</th>
                <th>CPU</th>
                <th>Memory</th>
              </tr>
            </thead>
            <tbody>
              ${(processes || []).map((proc) => `
                <tr>
                  <td>${proc.name || 'Unknown'}</td>
                  <td>${proc.pid || 'N/A'}</td>
                  <td>${proc.cpu || 0}</td>
                  <td>${formatBytes((proc.mem || 0) * 1024 * 1024)}</td>
                </tr>
              `).join('') || '<tr><td colspan="4">No process data</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}

function renderExport() {
  contentArea.innerHTML = `
    <div class="section">
      <div class="panel">
        <div class="panel-header">
          <h3>Export Report</h3>
        </div>
        <p style="color: var(--muted); margin-top: 0;">Download your system diagnostics in different formats.</p>
        <div class="export-actions">
          <button class="export-btn" id="exportJsonAction">
            <div class="icon">📋</div>
            <div class="label">JSON</div>
            <div class="desc">Raw data format</div>
          </button>
          <button class="export-btn" id="exportHtmlAction">
            <div class="icon">📄</div>
            <div class="label">HTML</div>
            <div class="desc">Web-friendly report</div>
          </button>
          <button class="export-btn" id="saveReportAction">
            <div class="icon">💾</div>
            <div class="label">Save</div>
            <div class="desc">Server storage</div>
          </button>
        </div>
      </div>
    </div>
  `;

  document.getElementById('exportJsonAction').addEventListener('click', () => exportJson());
  document.getElementById('exportHtmlAction').addEventListener('click', () => exportHtml());
  document.getElementById('saveReportAction').addEventListener('click', () => saveReport());
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
  if (!currentReport) {
    alert('No report data available yet.');
    return;
  }
  const json = JSON.stringify(currentReport, null, 2);
  downloadFile(`pc-check-report-${Date.now()}.json`, json, 'application/json');
}

function exportHtml() {
  if (!currentReport) {
    alert('No report data available yet.');
    return;
  }
  const health = computeHealthScore(currentReport);
  const storageText = (currentReport.storage || []).map((drive) => `
    <tr>
      <td>${drive.mount || 'Disk'}</td>
      <td>${drive.type || 'Disk'}</td>
      <td>${formatBytes(drive.size || 0)}</td>
      <td>${formatBytes(drive.used || 0)}</td>
      <td>${formatBytes(drive.available || 0)}</td>
      <td>${formatPercent(drive.use || 0)}</td>
    </tr>
  `).join('');

  const html = `<!DOCTYPE html>
  <html>
    <head>
      <meta charset="UTF-8" />
      <title>PC Check Report</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 32px; color: #111827; }
        h1 { margin-bottom: 0; }
        .meta { color: #475569; margin-bottom: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 16px; }
        th, td { border: 1px solid #d1d5db; padding: 10px; text-align: left; }
        th { background: #f3f4f6; }
      </style>
    </head>
    <body>
      <h1>PC Check Report</h1>
      <div class="meta">Generated: ${new Date(currentReport.generatedAt || Date.now()).toLocaleString()}</div>
      <p><strong>Health score:</strong> ${health}/100</p>
      <h2>Storage</h2>
      <table>
        <thead>
          <tr>
            <th>Drive</th>
            <th>Type</th>
            <th>Size</th>
            <th>Used</th>
            <th>Available</th>
            <th>Used %</th>
          </tr>
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
    renderSection(currentSection);
  } catch (error) {
    contentArea.innerHTML = '<div class="panel"><p>Unable to fetch system data.</p></div>';
  }
}

function renderSection(section) {
  currentSection = section;
  sectionTitle.textContent = section.charAt(0).toUpperCase() + section.slice(1);

  const descriptions = {
    overview: 'Real-time diagnostics and system health',
    hardware: 'CPU, memory, and GPU information',
    storage: 'Disk drives and storage capacity',
    network: 'Network interfaces and connectivity',
    processes: 'Running processes and resource usage',
    export: 'Download your system report'
  };

  sectionDesc.textContent = descriptions[section] || '';

  if (!currentReport) {
    contentArea.innerHTML = '<div class="panel"><p>Loading system data...</p></div>';
    return;
  }

  switch (section) {
    case 'overview':
      renderOverview(currentReport);
      break;
    case 'hardware':
      renderHardware(currentReport);
      break;
    case 'storage':
      renderStorage(currentReport);
      break;
    case 'network':
      renderNetwork(currentReport);
      break;
    case 'processes':
      renderProcesses(currentReport);
      break;
    case 'export':
      renderExport();
      break;
    default:
      renderOverview(currentReport);
  }
}

function updateNavigation(activeSection) {
  navItems.forEach((item) => {
    if (item.dataset.section === activeSection) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });
}

function applyTheme(theme) {
  const isLight = theme === 'light';
  document.body.classList.toggle('light', isLight);
  localStorage.setItem('pc-check-theme', theme);
}

navItems.forEach((item) => {
  item.addEventListener('click', () => {
    const section = item.dataset.section;
    updateNavigation(section);
    renderSection(section);
  });
});

refreshBtn.addEventListener('click', fetchSystemData);
themeToggleSidebar.addEventListener('click', () => {
  const nextTheme = document.body.classList.contains('light') ? 'dark' : 'light';
  applyTheme(nextTheme);
});

const savedTheme = localStorage.getItem('pc-check-theme') || 'dark';
applyTheme(savedTheme);
fetchSystemData();
