"""
PC Security Audit Tool - Complete Flask Application
Single-file local web application for Windows system forensics
Scans for exploit executors, cheat tools, and suspicious activity
No file deletion - read-only forensic analysis

INSTALLATION:
    pip install flask flask-cors pywin32 colorama

USAGE:
    python pc_security_audit_app.py
    Then open: http://localhost:5000

REQUIREMENTS:
    - Windows 7, 8, 10, 11
    - Python 3.7+
    - Administrator access (recommended for full system scanning)
"""

from flask import Flask, render_template_string, jsonify, request, send_file
from flask_cors import CORS
import os
import json
import datetime
import threading
import win32api
from collections import defaultdict
import io
import sys

app = Flask(__name__)
CORS(app)

# Global scan state
scan_state = {
    'running': False,
    'progress': 0,
    'status': 'idle',
    'current_scan': None
}

# ==================== HTML DASHBOARD (Embedded) ====================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PC Security Audit Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #e2e8f0;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header p {
            color: #94a3b8;
            margin-bottom: 20px;
        }

        .controls {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items: center;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4);
        }

        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(56, 189, 248, 0.6);
        }

        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .btn-secondary {
            background: rgba(51, 65, 85, 0.8);
            color: #e2e8f0;
            border: 1px solid rgba(148, 163, 184, 0.3);
        }

        .btn-secondary:hover:not(:disabled) {
            background: rgba(71, 85, 105, 0.8);
            border-color: rgba(148, 163, 184, 0.5);
        }

        .btn-secondary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .status-box {
            background: rgba(51, 65, 85, 0.6);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 8px;
            padding: 16px;
            margin-top: 20px;
        }

        .progress-container {
            margin-top: 16px;
        }

        .progress-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(30, 41, 59, 0.8);
            border-radius: 4px;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.2);
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #38bdf8 0%, #0ea5e9 100%);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 4px;
        }

        .status-text {
            color: #94a3b8;
            font-size: 13px;
            margin-top: 8px;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-bottom: 30px;
        }

        .summary-card {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }

        .summary-card .number {
            font-size: 32px;
            font-weight: 700;
            color: #38bdf8;
            margin-bottom: 4px;
        }

        .summary-card .label {
            color: #94a3b8;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            border-bottom: 2px solid rgba(148, 163, 184, 0.1);
            overflow-x: auto;
            padding-bottom: 0;
        }

        .tab-btn {
            padding: 12px 20px;
            background: transparent;
            color: #94a3b8;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s ease;
            white-space: nowrap;
        }

        .tab-btn:hover {
            color: #cbd5e1;
            border-bottom-color: rgba(56, 189, 248, 0.5);
        }

        .tab-btn.active {
            color: #38bdf8;
            border-bottom-color: #38bdf8;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .table-container {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        thead {
            background: rgba(30, 41, 59, 0.8);
            border-bottom: 2px solid rgba(148, 163, 184, 0.2);
        }

        th {
            padding: 16px;
            text-align: left;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 12px;
        }

        td {
            padding: 14px 16px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
            color: #cbd5e1;
        }

        tbody tr:hover {
            background: rgba(51, 65, 85, 0.4);
        }

        tbody tr:last-child td {
            border-bottom: none;
        }

        .category-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .category-cheat {
            background: rgba(239, 68, 68, 0.2);
            color: #fca5a5;
        }

        .category-debug {
            background: rgba(249, 115, 22, 0.2);
            color: #fed7aa;
        }

        .category-remote {
            background: rgba(168, 85, 247, 0.2);
            color: #e9d5ff;
        }

        .category-script {
            background: rgba(34, 197, 94, 0.2);
            color: #bbf7d0;
        }

        .category-other {
            background: rgba(59, 130, 246, 0.2);
            color: #bfdbfe;
        }

        .timestamp {
            color: #94a3b8;
            font-size: 12px;
            font-family: 'Monaco', 'Courier New', monospace;
        }

        .path-text {
            color: #64748b;
            font-size: 11px;
            font-family: 'Monaco', 'Courier New', monospace;
            word-break: break-all;
        }

        .copy-btn {
            background: rgba(51, 65, 85, 0.6);
            border: 1px solid rgba(148, 163, 184, 0.3);
            color: #94a3b8;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .copy-btn:hover {
            background: rgba(71, 85, 105, 0.8);
            color: #cbd5e1;
        }

        .alert {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.5);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
            color: #fca5a5;
            display: none;
        }

        .alert.show {
            display: block;
        }

        .alert.success {
            background: rgba(34, 197, 94, 0.1);
            border-color: rgba(34, 197, 94, 0.5);
            color: #86efac;
        }

        .empty-msg {
            text-align: center;
            color: #64748b;
            padding: 40px 20px;
        }

        @media (max-width: 768px) {
            .header {
                padding: 20px;
            }

            .header h1 {
                font-size: 22px;
            }

            .controls {
                flex-direction: column;
                width: 100%;
            }

            .btn {
                width: 100%;
                justify-content: center;
            }

            .summary-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .tabs {
                flex-wrap: wrap;
            }

            table {
                font-size: 12px;
            }

            th, td {
                padding: 12px 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 PC Security Audit Dashboard</h1>
            <p>Scan your Windows system for exploit executors, cheat tools, and suspicious activity</p>

            <div class="controls">
                <button class="btn btn-primary" id="scanBtn" onclick="startScan()">
                    <span>▶</span> Start Scan
                </button>
                <button class="btn btn-secondary" id="exportJsonBtn" onclick="exportJSON()" disabled>
                    📋 Export JSON
                </button>
                <button class="btn btn-secondary" id="exportTxtBtn" onclick="exportTXT()" disabled>
                    📄 Export TXT
                </button>
            </div>

            <div class="status-box" id="statusBox" style="display: none;">
                <div class="progress-label">
                    <span id="progressLabel">Initializing scan...</span>
                    <span id="progressPercent">0%</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                </div>
                <div class="status-text" id="statusText">Preparing to scan...</div>
            </div>
        </div>

        <div class="alert" id="alertBox"></div>

        <div class="summary-grid" id="summaryGrid" style="display: none;">
            <div class="summary-card">
                <div class="number" id="totalCount">0</div>
                <div class="label">Total Suspicious</div>
            </div>
            <div class="summary-card">
                <div class="number" id="prefetchCount">0</div>
                <div class="label">Prefetch</div>
            </div>
            <div class="summary-card">
                <div class="number" id="recentCount">0</div>
                <div class="label">Recent Files</div>
            </div>
            <div class="summary-card">
                <div class="number" id="tempCount">0</div>
                <div class="label">Temp Files</div>
            </div>
            <div class="summary-card">
                <div class="number" id="programCount">0</div>
                <div class="label">Program Files</div>
            </div>
            <div class="summary-card">
                <div class="number" id="startupCount">0</div>
                <div class="label">Startup Items</div>
            </div>
        </div>

        <div class="tabs" id="tabs" style="display: none;">
            <button class="tab-btn active" onclick="showTab('summary')">Summary</button>
            <button class="tab-btn" onclick="showTab('prefetch')">Prefetch</button>
            <button class="tab-btn" onclick="showTab('recent')">Recent Files</button>
            <button class="tab-btn" onclick="showTab('temp')">Temp Files</button>
            <button class="tab-btn" onclick="showTab('programs')">Program Files</button>
            <button class="tab-btn" onclick="showTab('startup')">Startup Items</button>
            <button class="tab-btn" onclick="showTab('browser')">Browser History</button>
        </div>

        <!-- Summary Tab -->
        <div class="tab-content active" id="tab-summary" style="display: none;">
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Count</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="summaryTable">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Prefetch Tab -->
        <div class="tab-content" id="tab-prefetch">
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Executable</th>
                            <th>Category</th>
                            <th>Last Accessed</th>
                            <th>Created</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody id="prefetchTable">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Recent Files Tab -->
        <div class="tab-content" id="tab-recent">
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Category</th>
                            <th>Last Accessed</th>
                            <th>Path</th>
                        </tr>
                    </thead>
                    <tbody id="recentTable">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Temp Files Tab -->
        <div class="tab-content" id="tab-temp">
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Category</th>
                            <th>Last Accessed</th>
                            <th>Directory</th>
                        </tr>
                    </thead>
                    <tbody id="tempTable">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Program Files Tab -->
        <div class="tab-content" id="tab-programs">
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Program</th>
                            <th>Category</th>
                            <th>Location</th>
                            <th>Last Accessed</th>
                        </tr>
                    </thead>
                    <tbody id="programsTable">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Startup Tab -->
        <div class="tab-content" id="tab-startup">
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Program</th>
                            <th>Startup Folder</th>
                            <th>Last Accessed</th>
                        </tr>
                    </thead>
                    <tbody id="startupTable">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Browser History Tab -->
        <div class="tab-content" id="tab-browser">
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Browser</th>
                            <th>Location</th>
                            <th>Last Modified</th>
                        </tr>
                    </thead>
                    <tbody id="browserTable">
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let currentResults = null;

        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
                tab.style.display = 'none';
            });
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });

            const selectedTab = document.getElementById(`tab-${tabName}`);
            if (selectedTab) {
                selectedTab.classList.add('active');
                selectedTab.style.display = 'block';
            }

            event.target.classList.add('active');
        }

        function getCategoryColor(category) {
            if (!category) return 'category-other';
            const cat = category.toLowerCase();
            if (cat.includes('cheat') || cat.includes('trainer') || cat.includes('hack')) return 'category-cheat';
            if (cat.includes('debug') || cat.includes('debugger')) return 'category-debug';
            if (cat.includes('remote')) return 'category-remote';
            if (cat.includes('script')) return 'category-script';
            return 'category-other';
        }

        function startScan() {
            document.getElementById('scanBtn').disabled = true;
            document.getElementById('statusBox').style.display = 'block';
            document.getElementById('summaryGrid').style.display = 'none';
            document.getElementById('tabs').style.display = 'none';
            document.getElementById('progressFill').style.width = '0%';

            fetch('/api/scan', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        showAlert(`Error: ${data.error}`);
                        document.getElementById('scanBtn').disabled = false;
                        return;
                    }
                    monitorScan();
                })
                .catch(e => {
                    showAlert(`Error starting scan: ${e}`);
                    document.getElementById('scanBtn').disabled = false;
                });
        }

        function monitorScan() {
            const monitor = setInterval(() => {
                fetch('/api/scan-status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('progressFill').style.width = data.progress + '%';
                        document.getElementById('progressPercent').textContent = data.progress + '%';
                        document.getElementById('progressLabel').textContent = data.status;
                        document.getElementById('statusText').textContent = data.status;

                        if (!data.running) {
                            clearInterval(monitor);
                            document.getElementById('scanBtn').disabled = false;
                            document.getElementById('exportJsonBtn').disabled = false;
                            document.getElementById('exportTxtBtn').disabled = false;
                            setTimeout(loadResults, 500);
                        }
                    })
                    .catch(e => console.error('Status error:', e));
            }, 300);
        }

        function loadResults() {
            fetch('/api/results')
                .then(r => r.json())
                .then(data => {
                    currentResults = data;
                    displayResults(data);
                })
                .catch(e => showAlert(`Error loading results: ${e}`));
        }

        function displayResults(data) {
            const stats = data.statistics || {};
            const findings = data.findings || {};

            document.getElementById('totalCount').textContent = stats.total_suspicious || 0;
            document.getElementById('prefetchCount').textContent = stats.prefetch_suspicious || 0;
            document.getElementById('recentCount').textContent = stats.recent_suspicious || 0;
            document.getElementById('tempCount').textContent = stats.temp_suspicious || 0;
            document.getElementById('programCount').textContent = stats.program_suspicious || 0;
            document.getElementById('startupCount').textContent = stats.startup_suspicious || 0;

            document.getElementById('summaryGrid').style.display = 'grid';
            document.getElementById('tabs').style.display = 'flex';

            let summaryHTML = `
                <tr><td>Prefetch Executables</td><td>${stats.prefetch_suspicious || 0}</td><td>${stats.prefetch_suspicious > 0 ? '🔴 Found' : '✅ Clean'}</td></tr>
                <tr><td>Recent Files</td><td>${stats.recent_suspicious || 0}</td><td>${stats.recent_suspicious > 0 ? '🔴 Found' : '✅ Clean'}</td></tr>
                <tr><td>Temp Files</td><td>${stats.temp_suspicious || 0}</td><td>${stats.temp_suspicious > 0 ? '🔴 Found' : '✅ Clean'}</td></tr>
                <tr><td>Program Files</td><td>${stats.program_suspicious || 0}</td><td>${stats.program_suspicious > 0 ? '🔴 Found' : '✅ Clean'}</td></tr>
                <tr><td>Startup Items</td><td>${stats.startup_suspicious || 0}</td><td>${stats.startup_suspicious > 0 ? '🔴 Found' : '✅ Clean'}</td></tr>
            `;
            document.getElementById('summaryTable').innerHTML = summaryHTML;

            const prefetch = findings.prefetch_suspicious || [];
            let prefetchHTML = prefetch.length === 0 
                ? '<tr><td colspan="5" class="empty-msg">✅ No suspicious prefetch executables found</td></tr>'
                : prefetch.map(item => `
                    <tr>
                        <td>${item.executable}</td>
                        <td><span class="category-badge ${getCategoryColor(item.category)}">${item.category || 'Unknown'}</span></td>
                        <td><span class="timestamp">${item.times?.accessed || 'N/A'}</span></td>
                        <td><span class="timestamp">${item.times?.created || 'N/A'}</span></td>
                        <td><button class="copy-btn" onclick="copyToClipboard('${item.path.replace(/'/g, "\\'")}')">Copy</button></td>
                    </tr>
                `).join('');
            document.getElementById('prefetchTable').innerHTML = prefetchHTML;

            const recent = findings.recent_suspicious || [];
            let recentHTML = recent.length === 0 
                ? '<tr><td colspan="4" class="empty-msg">✅ No suspicious recent files found</td></tr>'
                : recent.map(item => `
                    <tr>
                        <td>${item.name}</td>
                        <td><span class="category-badge ${getCategoryColor(item.category)}">${item.category || 'Unknown'}</span></td>
                        <td><span class="timestamp">${item.times?.accessed || 'N/A'}</span></td>
                        <td><span class="path-text">${item.path}</span></td>
                    </tr>
                `).join('');
            document.getElementById('recentTable').innerHTML = recentHTML;

            const temp = findings.temp_suspicious || [];
            let tempHTML = temp.length === 0 
                ? '<tr><td colspan="4" class="empty-msg">✅ No suspicious temp files found</td></tr>'
                : temp.map(item => `
                    <tr>
                        <td>${item.name}</td>
                        <td><span class="category-badge ${getCategoryColor(item.category)}">${item.category || 'Unknown'}</span></td>
                        <td><span class="timestamp">${item.times?.accessed || 'N/A'}</span></td>
                        <td><span class="path-text">${item.directory || 'N/A'}</span></td>
                    </tr>
                `).join('');
            document.getElementById('tempTable').innerHTML = tempHTML;

            const programs = findings.program_files_suspicious || [];
            let programsHTML = programs.length === 0 
                ? '<tr><td colspan="4" class="empty-msg">✅ No suspicious programs found</td></tr>'
                : programs.map(item => `
                    <tr>
                        <td>${item.name}</td>
                        <td><span class="category-badge ${getCategoryColor(item.category)}">${item.category || 'Unknown'}</span></td>
                        <td><span class="path-text">${item.location || 'N/A'}</span></td>
                        <td><span class="timestamp">${item.times?.accessed || 'N/A'}</span></td>
                    </tr>
                `).join('');
            document.getElementById('programsTable').innerHTML = programsHTML;

            const startup = findings.startup_suspicious || [];
            let startupHTML = startup.length === 0 
                ? '<tr><td colspan="3" class="empty-msg">✅ No suspicious startup items found</td></tr>'
                : startup.map(item => `
                    <tr>
                        <td>${item.name}</td>
                        <td><span class="path-text">${item.folder || 'N/A'}</span></td>
                        <td><span class="timestamp">${item.times?.accessed || 'N/A'}</span></td>
                    </tr>
                `).join('');
            document.getElementById('startupTable').innerHTML = startupHTML;

            const browser = findings.browser_history || [];
            let browserHTML = browser.length === 0 
                ? '<tr><td colspan="3" class="empty-msg">No browser history data available</td></tr>'
                : browser.map(item => `
                    <tr>
                        <td>${item.browser}</td>
                        <td><span class="path-text">${item.path}</span></td>
                        <td><span class="timestamp">${item.times?.modified || 'N/A'}</span></td>
                    </tr>
                `).join('');
            document.getElementById('browserTable').innerHTML = browserHTML;

            showTab('summary');
            showAlert('✅ Scan complete! Review results below.', 'success');
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showAlert('✅ Path copied to clipboard!', 'success');
            });
        }

        function exportJSON() {
            if (!currentResults) {
                showAlert('No results to export');
                return;
            }
            window.location.href = '/api/export/json';
        }

        function exportTXT() {
            if (!currentResults) {
                showAlert('No results to export');
                return;
            }
            window.location.href = '/api/export/txt';
        }

        function showAlert(message, type = 'error') {
            const alertBox = document.getElementById('alertBox');
            alertBox.textContent = message;
            alertBox.className = `alert show ${type === 'success' ? 'success' : ''}`;

            setTimeout(() => {
                alertBox.className = 'alert';
            }, 5000);
        }

        window.addEventListener('load', () => {
            showAlert('Ready to scan! Click "Start Scan" to begin.', 'success');
        });
    </script>
</body>
</html>
'''

# ==================== WINDOWS SECURITY AUDIT CLASS ====================
class PCSecurityAudit:
    """Windows PC Security Audit Tool"""
    
    EXPLOIT_SIGNATURES = {
        'cheat_engines': ['cheatengine', 'ce.exe', 'cheatengine-x86', 'cheatengine-x64'],
        'injectors': ['injector', 'dll_injector', 'process_injector', 'memory_hacker'],
        'game_hackers': ['artmoney', 'speedhack', 'trainers', 'wpe', 'winaoe'],
        'modifiers': ['hex_editor', 'res_hacker', 'patchmaker', 'patch_creator'],
        'remote_tools': ['teamviewer', 'anydesk', 'chrome_remote', 'ammyy'],
        'script_runners': ['autohotkey', 'ahk.exe', 'autoit', 'au3.exe'],
        'debug_tools': ['ollydbg', 'x64dbg', 'windbg', 'ida.exe', 'ghidra'],
    }
    
    TEMP_DIRS = [
        os.path.expandvars(r'%TEMP%'),
        os.path.expandvars(r'%APPDATA%\Temp'),
        os.path.expandvars(r'%LOCALAPPDATA%\Temp'),
        os.path.expandvars(r'%WINDIR%\Temp'),
        os.path.expandvars(r'%USERPROFILE%\Downloads'),
    ]
    
    def __init__(self):
        self.report_data = {
            'scan_date': datetime.datetime.now().isoformat(),
            'computer_name': os.environ.get('COMPUTERNAME', 'UNKNOWN'),
            'username': os.environ.get('USERNAME', 'UNKNOWN'),
            'findings': defaultdict(list),
            'statistics': {}
        }
    
    def get_file_times(self, filepath):
        """Extract file timestamps"""
        try:
            stat = os.stat(filepath)
            return {
                'created': datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'accessed': datetime.datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
                'size_bytes': stat.st_size,
            }
        except:
            return {}
    
    def scan_prefetch_files(self):
        """Scan Windows Prefetch"""
        global scan_state
        scan_state['status'] = 'Scanning Prefetch files...'
        scan_state['progress'] = 15
        
        prefetch_dir = os.path.expandvars(r'%WINDIR%\Prefetch')
        if not os.path.exists(prefetch_dir):
            return
        
        try:
            for pf_file in os.listdir(prefetch_dir):
                if not pf_file.endswith('.pf'):
                    continue
                
                exe_name = pf_file.replace('.pf', '').lower()
                filepath = os.path.join(prefetch_dir, pf_file)
                
                if self._check_suspicious_patterns(exe_name):
                    times = self.get_file_times(filepath)
                    self.report_data['findings']['prefetch_suspicious'].append({
                        'file': pf_file,
                        'executable': exe_name,
                        'path': filepath,
                        'times': times,
                        'category': self._get_category(exe_name)
                    })
        except:
            pass
    
    def scan_recent_files(self):
        """Scan Recent files"""
        global scan_state
        scan_state['status'] = 'Scanning Recent files...'
        scan_state['progress'] = 30
        
        recent_dir = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Recent')
        if not os.path.exists(recent_dir):
            return
        
        try:
            for item in os.listdir(recent_dir):
                item_path = os.path.join(recent_dir, item)
                try:
                    if self._check_suspicious_patterns(item.lower()):
                        times = self.get_file_times(item_path)
                        self.report_data['findings']['recent_suspicious'].append({
                            'name': item,
                            'path': item_path,
                            'times': times,
                            'category': self._get_category(item.lower())
                        })
                except:
                    pass
        except:
            pass
    
    def scan_temp_directories(self):
        """Scan Temp directories"""
        global scan_state
        scan_state['status'] = 'Scanning Temp directories...'
        scan_state['progress'] = 50
        
        for temp_dir in self.TEMP_DIRS:
            if not os.path.exists(temp_dir):
                continue
            
            try:
                for root, dirs, files in os.walk(temp_dir):
                    if root.count(os.sep) - temp_dir.count(os.sep) > 2:
                        continue
                    
                    for file in files:
                        filepath = os.path.join(root, file)
                        try:
                            if file.startswith('~') or file.startswith('.'):
                                continue
                            
                            if self._check_suspicious_patterns(file.lower()):
                                times = self.get_file_times(filepath)
                                self.report_data['findings']['temp_suspicious'].append({
                                    'name': file,
                                    'path': filepath,
                                    'directory': temp_dir,
                                    'times': times,
                                    'category': self._get_category(file.lower())
                                })
                        except:
                            pass
                        
                        if len(self.report_data['findings']['temp_suspicious']) > 100:
                            return
            except:
                pass
    
    def scan_program_files(self):
        """Scan Program Files"""
        global scan_state
        scan_state['status'] = 'Scanning Program Files...'
        scan_state['progress'] = 65
        
        program_dirs = [
            os.path.expandvars(r'%ProgramFiles%'),
            os.path.expandvars(r'%ProgramFiles(x86)%'),
        ]
        
        for prog_dir in program_dirs:
            if not os.path.exists(prog_dir):
                continue
            
            try:
                for item in os.listdir(prog_dir):
                    if self._check_suspicious_patterns(item.lower()):
                        item_path = os.path.join(prog_dir, item)
                        times = self.get_file_times(item_path)
                        self.report_data['findings']['program_files_suspicious'].append({
                            'name': item,
                            'path': item_path,
                            'location': prog_dir,
                            'times': times,
                            'category': self._get_category(item.lower())
                        })
            except:
                pass
    
    def scan_startup_folder(self):
        """Scan Startup folders"""
        global scan_state
        scan_state['status'] = 'Scanning Startup folders...'
        scan_state['progress'] = 75
        
        startup_dirs = [
            os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup'),
            os.path.expandvars(r'%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup'),
        ]
        
        for startup_dir in startup_dirs:
            if not os.path.exists(startup_dir):
                continue
            
            try:
                for item in os.listdir(startup_dir):
                    item_path = os.path.join(startup_dir, item)
                    times = self.get_file_times(item_path)
                    
                    if self._check_suspicious_patterns(item.lower()):
                        self.report_data['findings']['startup_suspicious'].append({
                            'name': item,
                            'path': item_path,
                            'folder': startup_dir,
                            'times': times,
                            'category': self._get_category(item.lower())
                        })
            except:
                pass
    
    def check_browser_history(self):
        """Check browser history files"""
        global scan_state
        scan_state['status'] = 'Checking browser history...'
        scan_state['progress'] = 85
        
        browser_paths = {
            'Chrome': os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\History'),
            'Edge': os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\History'),
        }
        
        for browser, path in browser_paths.items():
            if os.path.exists(path):
                times = self.get_file_times(path)
                self.report_data['findings']['browser_history'].append({
                    'browser': browser,
                    'path': path,
                    'times': times
                })
    
    def _check_suspicious_patterns(self, name):
        """Check if name is suspicious"""
        name_lower = name.lower()
        
        for patterns in self.EXPLOIT_SIGNATURES.values():
            for pattern in patterns:
                if pattern in name_lower:
                    return True
        
        keywords = ['trainer', 'hack', 'crack', 'keygen', 'cheat', 'inject',
                   'patcher', 'mod', 'exploit', 'bypass', 'spoofer', 'unban']
        
        for keyword in keywords:
            if keyword in name_lower:
                return True
        
        return False
    
    def _get_category(self, name):
        """Get category of suspicious file"""
        name_lower = name.lower()
        
        for category, patterns in self.EXPLOIT_SIGNATURES.items():
            for pattern in patterns:
                if pattern in name_lower:
                    return category.replace('_', ' ').title()
        
        return 'Suspicious Keyword Match'
    
    def run_full_scan(self):
        """Execute complete security audit"""
        global scan_state
        
        scan_state['running'] = True
        scan_state['progress'] = 0
        scan_state['status'] = 'Initializing scan...'
        
        try:
            self.scan_prefetch_files()
            self.scan_recent_files()
            self.scan_startup_folder()
            self.scan_program_files()
            self.scan_temp_directories()
            self.check_browser_history()
            
            # Calculate statistics
            self.report_data['statistics'] = {
                'prefetch_suspicious': len(self.report_data['findings'].get('prefetch_suspicious', [])),
                'recent_suspicious': len(self.report_data['findings'].get('recent_suspicious', [])),
                'temp_suspicious': len(self.report_data['findings'].get('temp_suspicious', [])),
                'program_suspicious': len(self.report_data['findings'].get('program_files_suspicious', [])),
                'startup_suspicious': len(self.report_data['findings'].get('startup_suspicious', [])),
                'total_suspicious': (
                    len(self.report_data['findings'].get('prefetch_suspicious', [])) +
                    len(self.report_data['findings'].get('recent_suspicious', [])) +
                    len(self.report_data['findings'].get('temp_suspicious', [])) +
                    len(self.report_data['findings'].get('program_files_suspicious', [])) +
                    len(self.report_data['findings'].get('startup_suspicious', []))
                )
            }
            
            scan_state['status'] = 'Scan complete!'
            scan_state['progress'] = 100
            scan_state['current_scan'] = self.report_data
            
        except Exception as e:
            scan_state['status'] = f'Error: {str(e)}'
            scan_state['progress'] = 0
        
        finally:
            scan_state['running'] = False


# ==================== FLASK ROUTES ====================
@app.route('/')
def index():
    """Serve dashboard"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/scan', methods=['POST'])
def start_scan():
    """Start scan in background"""
    global scan_state
    
    if scan_state['running']:
        return jsonify({'error': 'Scan already in progress'}), 400
    
    def run_scan():
        audit = PCSecurityAudit()
        audit.run_full_scan()
    
    thread = threading.Thread(target=run_scan)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'Scan started'})


@app.route('/api/scan-status')
def scan_status():
    """Get scan status"""
    return jsonify({
        'running': scan_state['running'],
        'progress': scan_state['progress'],
        'status': scan_state['status']
    })


@app.route('/api/results')
def get_results():
    """Get scan results"""
    if not scan_state['current_scan']:
        return jsonify({'error': 'No scan results available'}), 404
    
    return jsonify(scan_state['current_scan'])


@app.route('/api/export/json')
def export_json():
    """Export as JSON"""
    if not scan_state['current_scan']:
        return jsonify({'error': 'No results'}), 404
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'PC_Security_Audit_{timestamp}.json'
    
    return send_file(
        io.BytesIO(json.dumps(scan_state['current_scan'], indent=2).encode()),
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/export/txt')
def export_txt():
    """Export as TXT"""
    if not scan_state['current_scan']:
        return jsonify({'error': 'No results'}), 404
    
    report_data = scan_state['current_scan']
    report_text = generate_text_report(report_data)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'PC_Security_Audit_{timestamp}.txt'
    
    return send_file(
        io.BytesIO(report_text.encode()),
        mimetype='text/plain',
        as_attachment=True,
        download_name=filename
    )


def generate_text_report(report_data):
    """Generate text report"""
    output = []
    output.append("=" * 80)
    output.append("WINDOWS PC SECURITY AUDIT REPORT")
    output.append("=" * 80)
    output.append("")
    
    output.append(f"Scan Date: {report_data['scan_date']}")
    output.append(f"Computer: {report_data['computer_name']}")
    output.append(f"User: {report_data['username']}")
    output.append("")
    
    stats = report_data.get('statistics', {})
    output.append("SUMMARY")
    output.append("-" * 80)
    output.append(f"Total Suspicious Items: {stats.get('total_suspicious', 0)}")
    output.append(f"  • Prefetch: {stats.get('prefetch_suspicious', 0)}")
    output.append(f"  • Recent Files: {stats.get('recent_suspicious', 0)}")
    output.append(f"  • Temp Files: {stats.get('temp_suspicious', 0)}")
    output.append(f"  • Program Files: {stats.get('program_suspicious', 0)}")
    output.append(f"  • Startup Items: {stats.get('startup_suspicious', 0)}")
    output.append("")
    
    findings = report_data.get('findings', {})
    
    output.append("=" * 80)
    output.append("SUSPICIOUS PREFETCH EXECUTABLES")
    output.append("=" * 80)
    prefetch = findings.get('prefetch_suspicious', [])
    if prefetch:
        for item in prefetch:
            output.append(f"\nExecutable: {item['executable']}")
            output.append(f"File: {item['file']}")
            output.append(f"Path: {item['path']}")
            output.append(f"Category: {item.get('category', 'N/A')}")
            output.append(f"Created: {item.get('times', {}).get('created', 'N/A')}")
            output.append(f"Modified: {item.get('times', {}).get('modified', 'N/A')}")
            output.append(f"Accessed: {item.get('times', {}).get('accessed', 'N/A')}")
    else:
        output.append("✓ No suspicious executables found.")
    output.append("")
    
    output.append("=" * 80)
    output.append("SUSPICIOUS RECENT FILES")
    output.append("=" * 80)
    recent = findings.get('recent_suspicious', [])
    if recent:
        for item in recent:
            output.append(f"\nFile: {item['name']}")
            output.append(f"Path: {item['path']}")
            output.append(f"Category: {item.get('category', 'N/A')}")
            output.append(f"Accessed: {item.get('times', {}).get('accessed', 'N/A')}")
    else:
        output.append("✓ No suspicious files found.")
    output.append("")
    
    output.append("=" * 80)
    output.append("SUSPICIOUS TEMP FILES")
    output.append("=" * 80)
    temp = findings.get('temp_suspicious', [])
    if temp:
        for item in temp[:50]:
            output.append(f"\nFile: {item['name']}")
            output.append(f"Directory: {item['directory']}")
            output.append(f"Category: {item.get('category', 'N/A')}")
            output.append(f"Accessed: {item.get('times', {}).get('accessed', 'N/A')}")
    else:
        output.append("✓ No suspicious files found.")
    output.append("")
    
    output.append("=" * 80)
    output.append("SUSPICIOUS PROGRAM FILES")
    output.append("=" * 80)
    programs = findings.get('program_files_suspicious', [])
    if programs:
        for item in programs:
            output.append(f"\nProgram: {item['name']}")
            output.append(f"Location: {item['location']}")
            output.append(f"Category: {item.get('category', 'N/A')}")
            output.append(f"Accessed: {item.get('times', {}).get('accessed', 'N/A')}")
    else:
        output.append("✓ No suspicious programs found.")
    output.append("")
    
    output.append("=" * 80)
    output.append("SUSPICIOUS STARTUP ITEMS")
    output.append("=" * 80)
    startup = findings.get('startup_suspicious', [])
    if startup:
        for item in startup:
            output.append(f"\nProgram: {item['name']}")
            output.append(f"Folder: {item['folder']}")
            output.append(f"Accessed: {item.get('times', {}).get('accessed', 'N/A')}")
    else:
        output.append("✓ No suspicious startup items found.")
    output.append("")
    
    output.append("=" * 80)
    output.append("END OF REPORT")
    output.append("=" * 80)
    
    return "\n".join(output)


# ==================== ENTRY POINT ====================
if __name__ == '__main__':
    print("\n" + "="*80)
    print("PC SECURITY AUDIT TOOL - Flask Web Dashboard")
    print("="*80)
    print("\n✅ Installation complete!")
    print("\n📍 Starting server...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("⚠️  Keep this window open while using the tool")
    print("🛑 Press CTRL+C to stop the server")
    print("\n" + "="*80 + "\n")
    
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
