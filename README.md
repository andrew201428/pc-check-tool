const summaryGrid = document.getElementById('summaryGrid');
const systemOverview = document.getElementById('systemOverview');
const storageTable = document.getElementById('storageTable');
const networkList = document.getElementById('networkList');
const processTable = document.getElementById('processTable');
const gpuList = document.getElementById('gpuList');
const refreshBtn = document.getElementById('refreshBtn');
const saveReportBtn = document.getElementById('saveReportBtn');

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let value = bytes;
  let i = 0;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i += 1;
  }
  return `${value.toFixed(1)} ${units[i]}`;
}

function createSummaryCard(label, value, tone = 'normal') {
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `
    <div class="label">${label}</div>
    <div class="value" style="color:${tone === 'good' ? 'var(--success)' : tone === 'warn' ? 'var(--warning)' : 'var(--text)'};">${value}</div>
  `;
  return card;
}

function renderSystem(data) {
  const os = data.os || {};
  const cpu = data.cpu || {};
  const memory = data.memory || {};

  summaryGrid.innerHTML = '';

  summaryGrid.appendChild(createSummaryCard('Platform', os.platform || 'Unknown', 'good'));
  summaryGrid.appendChild(createSummaryCard('OS', `${os.distro || 'Unknown'} ${os.release || ''}`.trim(), 'good'));
  summaryGrid.appendChild(createSummaryCard('CPU', cpu.brand || 'Unknown'));
  summaryGrid.appendChild(createSummaryCard('Memory', formatBytes(memory.total || 0)));
  summaryGrid.appendChild(createSummaryCard('Storage', `${(data.storage || []).length} drive(s)`));
  summaryGrid.appendChild(createSummaryCard('Network', `${(data.network || []).length} adapter(s)`));

  systemOverview.innerHTML = '';
  const fields = [
    ['Platform', os.platform || 'Unknown'],
    ['Kernel', os.kernel || 'Unknown'],
    ['Architecture', os.arch || 'Unknown'],
    ['CPU', cpu.brand || 'Unknown'],
    ['Cores', cpu.cores || 'Unknown'],
    ['Total RAM', formatBytes(memory.total || 0)],
    ['Free RAM', formatBytes(memory.free || 0)],
    ['Available RAM', formatBytes(memory.available || 0)],
    ['Node', data.versions?.node || 'Unknown'],
    ['System', data.versions?.system || 'Unknown']
  ];

  fields.forEach(([key, value]) => {
    const item = document.createElement('div');
    item.className = 'info-item';
    item.innerHTML = `
      <span class="key">${key}</span>
      <span class="value">${value}</span>
    `;
    systemOverview.appendChild(item);
  });

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
        ${(data.storage || []).map((drive) => `
          <tr>
            <td>${drive.mount || 'Disk'}</td>
            <td>${drive.type || 'Disk'}</td>
            <td>${formatBytes(drive.size || 0)}</td>
            <td>${formatBytes(drive.used || 0)}</td>
            <td>${formatBytes(drive.available || 0)}</td>
            <td>${drive.use || 0}%</td>
          </tr>
        `).join('') || '<tr><td colspan="6">No storage data available</td></tr>'}
      </tbody>
    </table>
  `;

  networkList.innerHTML = (data.network || []).map((nic) => `
    <div class="list-item">
      <div><strong>${nic.name || 'NIC'}</strong><br/><small>${nic.type || 'Unknown'} </small></div>
      <div>${nic.ip4 || 'No IPv4'}<br/><small>${nic.mac || 'No MAC'}</small></div>
    </div>
  `).join('') || '<div class="list-item">No network interfaces found.</div>';

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
        ${(data.processes?.list || []).map((proc) => `
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

  const gpus = data.graphics?.controllers || data.graphics || [];
  gpuList.innerHTML = (Array.isArray(gpus) ? gpus : [gpus]).map((gpu) => `
    <div class="list-item">
      <div><strong>${gpu.model || gpu.name || 'GPU'}</strong></div>
      <div>${gpu.vram || gpu.memoryTotal || 'Unknown'} </div>
    </div>
  `).join('') || '<div class="list-item">No GPU data available.</div>';
}

async function fetchSystemData() {
  try {
    const response = await fetch('/api/system');
    const data = await response.json();
    renderSystem(data);
  } catch (error) {
    console.error('Failed to fetch system data:', error);
    summaryGrid.innerHTML = '<div class="card"><div class="label">Error</div><div class="value">Unable to load system information</div></div>';
  }
}

async function saveReport() {
  try {
    const response = await fetch('/api/system');
    const data = await response.json();
    const saveResponse = await fetch('/api/report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
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

refreshBtn.addEventListener('click', fetchSystemData);
saveReportBtn.addEventListener('click', saveReport);

fetchSystemData();
