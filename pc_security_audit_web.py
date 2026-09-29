"""
PC Security Audit Tool - Flask Web Application
Modern web-based Windows system scanner with real-time dashboard
Run: python pc_security_audit_web.py
Visit: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import os
import json
import datetime
import threading
from pathlib import Path
import win32api
from collections import defaultdict
import io

app = Flask(__name__)
CORS(app)

# Global scan state
scan_state = {
    'running': False,
    'progress': 0,
    'status': 'idle',
    'current_scan': None
}

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
        os.path.expandvars(r'%USERPROFILE%\AppData\Local\Temp'),
    ]
    
    def __init__(self):
        self.report_data = {
            'scan_date': datetime.datetime.now().isoformat(),
            'computer_name': os.environ.get('COMPUTERNAME', 'UNKNOWN'),
            'username': os.environ.get('USERNAME', 'UNKNOWN'),
            'findings': defaultdict(list),
            'statistics': {}
        }
        self.suspicious_files = []
    
    def get_file_times(self, filepath):
        """Extract file creation, modification, and access times"""
        try:
            stat = os.stat(filepath)
            return {
                'created': datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'accessed': datetime.datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
                'size_bytes': stat.st_size,
                'size_display': self._format_bytes(stat.st_size)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _format_bytes(self, bytes_size):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    def scan_prefetch_files(self):
        """Scan Windows Prefetch directory"""
        global scan_state
        scan_state['status'] = 'Scanning Prefetch files...'
        scan_state['progress'] = 10
        
        prefetch_dir = os.path.expandvars(r'%WINDIR%\Prefetch')
        if not os.path.exists(prefetch_dir):
            return
        
        try:
            pf_files = os.listdir(prefetch_dir)
            found_count = 0
            
            for pf_file in pf_files:
                if not pf_file.endswith('.pf'):
                    continue
                
                exe_name = pf_file.replace('.pf', '').lower()
                filepath = os.path.join(prefetch_dir, pf_file)
                
                is_suspicious = self._check_suspicious_patterns(exe_name)
                
                if is_suspicious:
                    times = self.get_file_times(filepath)
                    self.report_data['findings']['prefetch_suspicious'].append({
                        'file': pf_file,
                        'executable': exe_name,
                        'path': filepath,
                        'times': times,
                        'reason': 'Matches known exploit/cheat signature',
                        'category': self._get_category(exe_name)
                    })
                    self.suspicious_files.append(filepath)
                    found_count += 1
            
            # Log all prefetch files
            all_files = []
            for pf_file in sorted(pf_files):
                if pf_file.endswith('.pf'):
                    exe_name = pf_file.replace('.pf', '')
                    filepath = os.path.join(prefetch_dir, pf_file)
                    times = self.get_file_times(filepath)
                    all_files.append({
                        'file': pf_file,
                        'executable': exe_name,
                        'times': times
                    })
            
            self.report_data['findings']['prefetch_all'] = sorted(all_files, 
                                                                  key=lambda x: x['times'].get('accessed', ''),
                                                                  reverse=True)
            
        except Exception as e:
            self.report_data['findings']['prefetch_error'] = str(e)
    
    def scan_recent_files(self):
        """Scan Windows Recent files"""
        global scan_state
        scan_state['status'] = 'Scanning Recent files...'
        scan_state['progress'] = 30
        
        recent_dir = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Recent')
        if not os.path.exists(recent_dir):
            return
        
        try:
            recent_files = []
            suspicious_recent = []
            
            for item in os.listdir(recent_dir):
                item_path = os.path.join(recent_dir, item)
                try:
                    times = self.get_file_times(item_path)
                    recent_files.append({
                        'name': item,
                        'path': item_path,
                        'times': times,
                        'is_shortcut': item.endswith('.lnk')
                    })
                    
                    if self._check_suspicious_patterns(item.lower()):
                        suspicious_recent.append({
                            'name': item,
                            'path': item_path,
                            'times': times,
                            'reason': 'Matches known exploit/cheat signature',
                            'category': self._get_category(item.lower())
                        })
                except Exception:
                    pass
            
            self.report_data['findings']['recent_all'] = sorted(recent_files, 
                                                               key=lambda x: x['times'].get('accessed', ''),
                                                               reverse=True)
            self.report_data['findings']['recent_suspicious'] = suspicious_recent
            
        except Exception as e:
            self.report_data['findings']['recent_error'] = str(e)
    
    def scan_temp_directories(self):
        """Scan temporary directories"""
        global scan_state
        scan_state['status'] = 'Scanning Temp directories...'
        scan_state['progress'] = 50
        
        all_temp_files = []
        suspicious_temp_files = []
        
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
                            
                            times = self.get_file_times(filepath)
                            
                            all_temp_files.append({
                                'name': file,
                                'path': filepath,
                                'directory': temp_dir,
                                'times': times
                            })
                            
                            if self._check_suspicious_patterns(file.lower()):
                                suspicious_temp_files.append({
                                    'name': file,
                                    'path': filepath,
                                    'times': times,
                                    'reason': 'Matches known exploit/cheat signature',
                                    'category': self._get_category(file.lower())
                                })
                        
                        except Exception:
                            pass
                        
                        if len(all_temp_files) > 500:
                            break
                    if len(all_temp_files) > 500:
                        break
                        
            except PermissionError:
                pass
            except Exception:
                pass
        
        self.report_data['findings']['temp_all'] = sorted(all_temp_files,
                                                         key=lambda x: x['times'].get('accessed', ''),
                                                         reverse=True)[:200]
        self.report_data['findings']['temp_suspicious'] = suspicious_temp_files
    
    def scan_program_files(self):
        """Scan Program Files for suspicious applications"""
        global scan_state
        scan_state['status'] = 'Scanning Program Files...'
        scan_state['progress'] = 65
        
        program_dirs = [
            os.path.expandvars(r'%ProgramFiles%'),
            os.path.expandvars(r'%ProgramFiles(x86)%'),
            os.path.expandvars(r'%LocalAppData%\Programs')
        ]
        
        suspicious_programs = []
        
        for prog_dir in program_dirs:
            if not os.path.exists(prog_dir):
                continue
            
            try:
                for item in os.listdir(prog_dir):
                    if self._check_suspicious_patterns(item.lower()):
                        item_path = os.path.join(prog_dir, item)
                        times = self.get_file_times(item_path)
                        suspicious_programs.append({
                            'name': item,
                            'path': item_path,
                            'times': times,
                            'location': prog_dir,
                            'reason': 'Matches known exploit/cheat signature',
                            'category': self._get_category(item.lower())
                        })
                        
            except PermissionError:
                pass
            except Exception:
                pass
        
        self.report_data['findings']['program_files_suspicious'] = suspicious_programs
    
    def scan_startup_folder(self):
        """Scan startup folders"""
        global scan_state
        scan_state['status'] = 'Scanning Startup folders...'
        scan_state['progress'] = 75
        
        startup_dirs = [
            os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup'),
            os.path.expandvars(r'%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup'),
        ]
        
        all_startup = []
        suspicious_startup = []
        
        for startup_dir in startup_dirs:
            if not os.path.exists(startup_dir):
                continue
            
            try:
                for item in os.listdir(startup_dir):
                    item_path = os.path.join(startup_dir, item)
                    times = self.get_file_times(item_path)
                    
                    all_startup.append({
                        'name': item,
                        'path': item_path,
                        'times': times,
                        'folder': startup_dir
                    })
                    
                    if self._check_suspicious_patterns(item.lower()):
                        suspicious_startup.append({
                            'name': item,
                            'path': item_path,
                            'times': times,
                            'reason': 'Matches known exploit/cheat signature',
                            'category': self._get_category(item.lower())
                        })
                        
            except Exception:
                pass
        
        self.report_data['findings']['startup_all'] = all_startup
        self.report_data['findings']['startup_suspicious'] = suspicious_startup
    
    def check_browser_history(self):
        """Extract browser history metadata"""
        global scan_state
        scan_state['status'] = 'Checking browser history...'
        scan_state['progress'] = 85
        
        browser_paths = {
            'Chrome': os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\History'),
            'Edge': os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\History'),
            'Firefox': os.path.expandvars(r'%APPDATA%\Mozilla\Firefox\Profiles')
        }
        
        browser_info = []
        
        for browser, path in browser_paths.items():
            if os.path.exists(path):
                times = self.get_file_times(path)
                browser_info.append({
                    'browser': browser,
                    'path': path,
                    'times': times
                })
        
        self.report_data['findings']['browser_history'] = browser_info
    
    def _check_suspicious_patterns(self, name):
        """Check if name matches known exploit/cheat patterns"""
        name_lower = name.lower()
        
        for patterns in self.EXPLOIT_SIGNATURES.values():
            for pattern in patterns:
                if pattern in name_lower:
                    return True
        
        suspicious_keywords = [
            'trainer', 'hack', 'crack', 'keygen', 'cheat', 'inject',
            'patcher', 'mod', 'exploit', 'bypass', 'spoofer', 'unban'
        ]
        
        for keyword in suspicious_keywords:
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


# Flask Routes
@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('index.html')


@app.route('/api/scan', methods=['POST'])
def start_scan():
    """Start security scan in background"""
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
    """Get current scan status and progress"""
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
    """Export results as JSON"""
    if not scan_state['current_scan']:
        return jsonify({'error': 'No scan results available'}), 404
    
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
    """Export results as text report"""
    if not scan_state['current_scan']:
        return jsonify({'error': 'No scan results available'}), 404
    
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
    """Generate formatted text report"""
    output = []
    output.append("=" * 80)
    output.append("WINDOWS PC SECURITY AUDIT REPORT")
    output.append("=" * 80)
    output.append("")
    
    output.append(f"Scan Date & Time: {report_data['scan_date']}")
    output.append(f"Computer Name: {report_data['computer_name']}")
    output.append(f"Username: {report_data['username']}")
    output.append("")
    
    stats = report_data.get('statistics', {})
    output.append("=" * 80)
    output.append("SUMMARY")
    output.append("=" * 80)
    output.append(f"Total Suspicious Items: {stats.get('total_suspicious', 0)}")
    output.append(f"  • Prefetch: {stats.get('prefetch_suspicious', 0)}")
    output.append(f"  • Recent Files: {stats.get('recent_suspicious', 0)}")
    output.append(f"  • Temp Files: {stats.get('temp_suspicious', 0)}")
    output.append(f"  • Program Files: {stats.get('program_suspicious', 0)}")
    output.append(f"  • Startup Items: {stats.get('startup_suspicious', 0)}")
    output.append("")
    
    # Prefetch
    output.append("=" * 80)
    output.append("SUSPICIOUS PREFETCH EXECUTABLES")
    output.append("=" * 80)
    prefetch_sus = report_data.get('findings', {}).get('prefetch_suspicious', [])
    if prefetch_sus:
        for item in prefetch_sus:
            output.append(f"\nExecutable: {item['executable']}")
            output.append(f"Path: {item['path']}")
            output.append(f"Category: {item.get('category', 'N/A')}")
            times = item.get('times', {})
            output.append(f"Created: {times.get('created', 'N/A')}")
            output.append(f"Modified: {times.get('modified', 'N/A')}")
            output.append(f"Accessed: {times.get('accessed', 'N/A')}")
            output.append(f"Reason: {item.get('reason', 'N/A')}")
    else:
        output.append("✓ No suspicious executables found in Prefetch.")
    output.append("")
    
    # Recent Files
    output.append("=" * 80)
    output.append("SUSPICIOUS RECENT FILES")
    output.append("=" * 80)
    recent_sus = report_data.get('findings', {}).get('recent_suspicious', [])
    if recent_sus:
        for item in recent_sus:
            output.append(f"\nFile: {item['name']}")
            output.append(f"Path: {item['path']}")
            output.append(f"Category: {item.get('category', 'N/A')}")
            times = item.get('times', {})
            output.append(f"Accessed: {times.get('accessed', 'N/A')}")
    else:
        output.append("✓ No suspicious files found in Recent.")
    output.append("")
    
    # Temp Files
    output.append("=" * 80)
    output.append("SUSPICIOUS TEMP FILES")
    output.append("=" * 80)
    temp_sus = report_data.get('findings', {}).get('temp_suspicious', [])
    if temp_sus:
        for item in temp_sus[:50]:
            output.append(f"\nFile: {item['name']}")
            output.append(f"Path: {item['path']}")
            output.append(f"Category: {item.get('category', 'N/A')}")
            times = item.get('times', {})
            output.append(f"Accessed: {times.get('accessed', 'N/A')}")
    else:
        output.append("✓ No suspicious files found in Temp directories.")
    output.append("")
    
    # Program Files
    output.append("=" * 80)
    output.append("SUSPICIOUS PROGRAM FILES")
    output.append("=" * 80)
    prog_sus = report_data.get('findings', {}).get('program_files_suspicious', [])
    if prog_sus:
        for item in prog_sus:
            output.append(f"\nProgram: {item['name']}")
            output.append(f"Path: {item['path']}")
            output.append(f"Category: {item.get('category', 'N/A')}")
            times = item.get('times', {})
            output.append(f"Accessed: {times.get('accessed', 'N/A')}")
    else:
        output.append("✓ No suspicious programs found.")
    output.append("")
    
    # Startup
    output.append("=" * 80)
    output.append("SUSPICIOUS STARTUP ITEMS")
    output.append("=" * 80)
    startup_sus = report_data.get('findings', {}).get('startup_suspicious', [])
    if startup_sus:
        for item in startup_sus:
            output.append(f"\nProgram: {item['name']}")
            output.append(f"Path: {item['path']}")
            output.append(f"Category: {item.get('category', 'N/A')}")
            times = item.get('times', {})
            output.append(f"Accessed: {times.get('accessed', 'N/A')}")
    else:
        output.append("✓ No suspicious startup items found.")
    output.append("")
    
    output.append("=" * 80)
    output.append("END OF REPORT")
    output.append("=" * 80)
    
    return "\n".join(output)


if __name__ == '__main__':
    print("\n" + "="*80)
    print("PC SECURITY AUDIT TOOL - Web Dashboard")
    print("="*80)
    print("\n🚀 Starting local server...")
    print("📍 Open your browser and go to: http://localhost:5000")
    print("⚠️  Keep this window open while using the tool\n")
    
    app.run(debug=True, use_reloader=False)
