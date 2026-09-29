const express = require('express');
const path = require('path');
const fs = require('fs');
const si = require('systeminformation');

const app = express();
const PORT = process.env.PORT || 3000;
const REPORTS_DIR = path.join(__dirname, 'reports');

if (!fs.existsSync(REPORTS_DIR)) {
  fs.mkdirSync(REPORTS_DIR, { recursive: true });
}

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.get('/api/system', async (_req, res) => {
  try {
    const [
      osInfo,
      cpu,
      mem,
      fsSize,
      graphics,
      networkInterfaces,
      versions,
      battery,
      processes,
      users
    ] = await Promise.all([
      si.osInfo(),
      si.cpu(),
      si.mem(),
      si.fsSize(),
      si.graphics(),
      si.networkInterfaces(),
      si.versions(),
      si.battery(),
      si.processes(),
      si.users()
    ]);

    const systemReport = {
      generatedAt: new Date().toISOString(),
      os: {
        platform: process.platform,
        release: osInfo.release,
        distro: osInfo.distro || 'Unknown',
        codename: osInfo.codename || 'Unknown',
        arch: osInfo.arch || process.arch,
        kernel: osInfo.kernel || 'Unknown'
      },
      cpu: {
        manufacturer: cpu.manufacturer,
        brand: cpu.brand,
        cores: cpu.cores,
        physicalCores: cpu.physicalCores,
        speed: cpu.speed,
        vendor: cpu.vendor,
        family: cpu.family,
        model: cpu.model
      },
      memory: {
        total: mem.total,
        free: mem.free,
        used: mem.used,
        active: mem.active,
        available: mem.available,
        swapTotal: mem.swaptotal,
        swapUsed: mem.swapused,
        swapFree: mem.swapfree
      },
      storage: fsSize.map((drive) => ({
        fs: drive.fs,
        type: drive.type,
        size: drive.size,
        used: drive.used,
        available: drive.available,
        use: drive.use,
        mount: drive.mount
      })),
      graphics: graphics.controllers || graphics || [],
      network: networkInterfaces.map((nic) => ({
        name: nic.ifaceName || nic.iface,
        type: nic.type,
        mac: nic.mac,
        ip4: nic.ip4,
        ip6: nic.ip6,
        dhcp: nic.dhcp,
        speed: nic.speed
      })),
      versions: {
        node: versions.node,
        npm: versions.npm,
        system: versions.system,
        python: versions.python || 'Not installed'
      },
      battery: battery || null,
      processes: {
        total: processes.total,
        list: (processes.list || []).slice(0, 20).map((p) => ({
          pid: p.pid,
          name: p.name,
          cpu: p.cpu,
          mem: p.mem,
          command: p.command
        }))
      },
      users: users || []
    };

    res.json(systemReport);
  } catch (error) {
    console.error('System gather failed:', error);
    res.status(500).json({
      error: 'Unable to gather system details.',
      details: error.message
    });
  }
});

app.post('/api/report', async (req, res) => {
  try {
    const snapshot = req.body || {};
    const fileName = `pc-report-${Date.now()}.json`;
    const filePath = path.join(REPORTS_DIR, fileName);
    const payload = {
      generatedAt: new Date().toISOString(),
      report: snapshot
    };

    fs.writeFileSync(filePath, JSON.stringify(payload, null, 2), 'utf8');

    res.json({
      success: true,
      filename: fileName,
      path: `/reports/${fileName}`
    });
  } catch (error) {
    console.error('Report save failed:', error);
    res.status(500).json({
      error: 'Unable to save report.',
      details: error.message
    });
  }
});

app.use('/reports', express.static(REPORTS_DIR));

app.get('*', (_req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`PC check tool running at http://localhost:${PORT}`);
});
