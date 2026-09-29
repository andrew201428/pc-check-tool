const summaryGrid = document.getElementById('summaryGrid');
const systemOverview = document.getElementById('systemOverview');
const performancePanel = document.getElementById('performancePanel');
const storageTable = document.getElementById('storageTable');
const networkList = document.getElementById('networkList');
const processTable = document.getElementById('processTable');
const gpuList = document.getElementById('gpuList');
const refreshBtn = document.getElementById('refreshBtn');
const saveReportBtn = document.getElementById('saveReportBtn');
const exportJsonBtn = document.getElementById('exportJsonBtn');
const exportHtmlBtn = document.getElementById('exportHtmlBtn');
const themeToggle = document.getElementById('themeToggle');
const statusPill = document.getElementById('statusPill');
const healthMeter = document.getElementById('healthMeter');
const healthScore = document.getElementById('healthScore');
const lastUpdatedText = document.getElementById('lastUpdatedText');
const memoryChartBar = document.getElementById('memoryChartBar');
const storageChartBar = document.getElementById('storageChartBar');
const healthChartBar = document.getElementById('healthChartBar');
const memoryChartValue = document.getElementById('memoryChartValue');
const storageChartValue = document.getElementById('storageChartValue');
const healthChartValue = document.getElementById('healthChartValue');

let currentReport = null;

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

function createSummaryCard(label, value, tone = 'neutral') {
  const card = document.createElement('div');
  card.className = 'summary-card';

  const toneMap = {
    neutral: '#e5eef8',
    success: 'var(--success)',
    warn: 'var(--warning)',
    danger: 'var(--danger)'
  };

  card.innerHTML = `
    <div class="label">${label}</div>
    <div class="value" style="color:${toneMap[tone] || toneMap.neutral};">${value}</div>
  `;

  return card;
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

function renderCharts(data) {
  const memoryUsedPercent = clamp(((Number(data.memory?.used) || 0) / (Number(data.memory?.total) || 1)) * 100, 0, 100);
  const storageUsedPercent = clamp(
    ((data.storage || []).reduce((sum, drive) => sum + (Number(drive.used) || 0), 0) /
      (data.storage || []).reduce((sum, drive) => sum + (Number(drive.size) || 0), 0 || 1)) * 100,
    0,
    100
  );
  const health = computeHealthScore(data);

  memoryChartBar.style.width = `${memoryUsedPercent}%`;
  storageChartBar.style.width = `${storageUsedPercent}%`;
  healthChartBar.style.width = `${health}%`;

  memoryChartValue.textContent = formatPercent(memoryUsedPercent);
  storageChartValue.textContent = formatPercent(storageUsedPercent);
  healthChartValue.textContent = `${health}/100`;
}

function renderPerformance(data) {
  const memory = data.memory || {};
  const cpu = data.cpu || {};
  const battery = data.battery || {};

  const performanceItems = [
    {
      label: 'Memory usage',
      value: formatPercent(((Number(memory.used) || 0) / (Number(memory.total) || 1)) * 100),
      detail: `${formatBytes(memory.used || 0)} used / ${formatBytes(memory.total || 0)}`
    },
    {
      label: 'CPU',
      value: cpu.brand || 'Unknown',
      detail: `${cpu.cores || 'Unknown'} cores`
    },
    {
      label: 'Battery',
      value: battery.isCharging ? 'Charging' : 'On power',
      detail: battery.percent ? `${battery.percent}%` : 'Not available'
    },
    {
      label: 'Users',
      value: `${(data.users || []).length || 0}`,
      detail: 'Logged in users'
    }
  ];

  performancePanel.innerHTML = performanceItems.map((item) => `
    <div class="performance-item">
      <div class="row">
        <span>${item.label}</span>
        <strong>${item.value}</strong>
      </div>
      <small>${item.detail}</small>
    </div>
  `).join('');
}

function renderSystem(data) {
  currentReport = data;
  const os = data.os || {};
  const cpu = data.cpu || {};
  const memory = data.memory || {};
  const storage = data.storage || [];
  const network = data.network || [];
  const processes = data.processes?.list || [];
  const gpus = data.graphics?.controllers || data.graphics || [];

  const health = computeHealthScore(data);
  healthMeter.style.width = `${health}%`;
  healthScore.textContent = `${health}/100`;
  statusPill.textContent = health >= 70 ? 'Healthy' : health >= 45 ? 'Watch' : 'Low';
  statusPill.style.background = health >= 70 ? 'rgba(52, 211, 153, 0.12)' : health >= 45 ? 'rgba(251, 191, 36, 0.12)' : 'rgba(251, 113, 133, 0.12)';
  statusPill.style.color = health >= 70 ? 'var(--success)' : health >= 45 ? 'var(--warning)' : 'var(--danger)';
  statusPill.style.borderColor = health >= 70 ? 'rgba(52, 211, 153, 0.18)' : health >= 45 ? 'rgba(251, 191, 36, 0.18)' : 'rgba(251, 113, 133, 0.18)';

  const timestamp = new Date(data.generatedAt || Date.now()).toLocaleString();
  lastUpdatedText.textContent = `Last synced: ${timestamp}`;

  summaryGrid.innerHTML = '';
  summaryGrid.appendChild(createSummaryCard('Platform', os.platform || 'Unknown', 'success'));
  summaryGrid.appendChild(createSummaryCard('OS', `${os.distro || 'Unknown'} ${os.release || ''}`.trim(), 'success'));
  summaryGrid.appendChild(createSummaryCard('CPU', cpu.brand || 'Unknown'));
  summaryGrid.appendChild(createSummaryCard('RAM', formatBytes(memory.total || 0), 'neutral'));
  summaryGrid.appendChild(createSummaryCard('Storage', `${storage.length || 0} drive(s)`));
  summaryGrid.appendChild(createSummaryCard('Health', `${health}/100`, health >= 70 ? 'success' : health >= 45 ? 'warn' : 'danger'));

  systemOverview.innerHTML = [
    ['Platform', os.platform || 'Unknown'],
    ['OS', `${os.distro || 'Unknown'} ${os.release || ''}`.trim() || 'Unknown'],
    ['Kernel', os.kernel || 'Unknown'],
    ['Architecture', os.arch || 'Unknown'],
    ['CPU', cpu.brand || 'Unknown'],
    ['Cores', cpu.cores || 'Unknown'],
    ['Total RAM', formatBytes(memory.total || 0)],
    ['Free RAM', formatBytes(memory.free || 0)],
    ['Available RAM', formatBytes(memory.available || 0)],
    ['Node', data.versions?.node || 'Unknown'],
    ['System', data.versions?.system || 'Unknown'],
    ['Users', `${(data.users || []).length || 0}`]
  ].map(([key, value]) => `
    <div class="info-item">
      <span class="key">${key}</span>
      <span class="value">${value}</span>
    </div>
  `).join('');

  renderPerformance(data);
  renderCharts(data);

  storageTable.innerHTML = `
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
        `).join('') || '<tr><td colspan="6">No storage data available</td></tr>'}
      </tbody>
    </table>
  `;

  networkList.innerHTML = (network || []).map((nic) => `
    <div class="list-item">
      <div>
        <strong>${nic.name || 'NIC'}</strong><br />
        <small>${nic.type || 'Unknown'} / ${nic.mac || 'No MAC'}</small>
      </div>
      <div style="text-align:right;">
        <strong>${nic.ip4 || 'No IPv4'}</strong><br />
        <small>${nic.ip6 || 'No IPv6'}</small>
      </div>
    </div>
  `).join('') || '<div class="list-item">No network interfaces found.</div>';

  const gpuEntries = Array.isArray(gpus) ? gpus : [gpus].filter(Boolean);
  gpuList.innerHTML = gpuEntries.map((gpu) => `
    <div class="list-item">
      <div>
        <strong>${gpu.model || gpu.name || 'GPU'}</strong><br />
        <small>${gpu.vendor || 'Unknown vendor'}</small>
      </div>
      <div>
        <strong>${gpu.vram || gpu.memoryTotal || 'N/A'}</strong>
      </div>
    </div>
  `).join('') || '<div class="list-item">No GPU data available.</div>';

  processTable.innerHTML = `
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
        `).join('') || '<tr><td colspan="4">No process data available</td></tr>'}
      </tbody>
    </table>
  `;
}

async function fetchSystemData() {
  try {
    const response = await fetch('/api/system');
    const data = await response.json();
    renderSystem(data);
  } catch (error) {
    console.error('Failed to fetch system data:', error);
    summaryGrid.innerHTML = '<div class="summary-card"><div class="label">Error</div><div class="value">Unable to load system information</div></div>';
    lastUpdatedText.textContent = 'Unable to refresh diagnostics.';
    statusPill.textContent = 'Error';
    statusPill.style.background = 'rgba(251, 113, 133, 0.12)';
    statusPill.style.color = 'var(--danger)';
  }
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
    } else {
      alert('Unable to save report.');
    }
  } catch (error) {
    console.error('Failed to save report:', error);
    alert('Unable to save the report.');
  }
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
      <p><strong>System:</strong> ${currentReport.os?.distro || 'Unknown'} ${currentReport.os?.release || ''}</p>
      <p><strong>CPU:</strong> ${currentReport.cpu?.brand || 'Unknown'}</p>
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

function applyTheme(theme) {
  const isLight = theme === 'light';
  document.body.classList.toggle('light', isLight);
  themeToggle.textContent = isLight ? '🌙 Dark' : '☀️ Light';
  localStorage.setItem('pc-check-theme', theme);
}

refreshBtn.addEventListener('click', fetchSystemData);
saveReportBtn.addEventListener('click', saveReport);
exportJsonBtn.addEventListener('click', exportJson);
exportHtmlBtn.addEventListener('click', exportHtml);
themeToggle.addEventListener('click', () => {
  const nextTheme = document.body.classList.contains('light') ? 'dark' : 'light';
  applyTheme(nextTheme);
});

const savedTheme = localStorage.getItem('pc-check-theme') || 'dark';
applyTheme(savedTheme);
fetchSystemData();
