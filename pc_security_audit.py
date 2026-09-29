"""
PC Security Audit Tool - Windows System Scanner
Scans for suspicious activity, exploit executors, and generates forensic reports.
Requires: Python 3.7+, pywin32, colorama
Install: pip install pywin32 colorama
"""

import os
import sys
import json
import datetime
import subprocess
import win32api
import win32con
from pathlib import Path
from collections import defaultdict
from colorama import Fore, Back, Style, init

init(autoreset=True)

class PCSecurityAudit:
    """Windows PC Security Audit Tool"""
    
    # Known cheat/exploit executor patterns
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
        os.path.expandvars(r'%PUBLIC%\Documents'),
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
                'created': datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.datetime.fromtimestamp(stat.st_atime).isoformat(),
                'size_bytes': stat.st_size
            }
        except Exception as e:
            return {'error': str(e)}
    
    def scan_prefetch_files(self):
        """Scan Windows Prefetch directory for suspicious executables"""
        print(f"\n{Fore.CYAN}[*] Scanning Windows Prefetch...{Style.RESET_ALL}")
        
        prefetch_dir = os.path.expandvars(r'%WINDIR%\Prefetch')
        if not os.path.exists(prefetch_dir):
            print(f"{Fore.YELLOW}[!] Prefetch directory not found{Style.RESET_ALL}")
            return
        
        try:
            pf_files = os.listdir(prefetch_dir)
            found_count = 0
            
            for pf_file in pf_files:
                if not pf_file.endswith('.pf'):
                    continue
                
                exe_name = pf_file.replace('.pf', '').lower()
                filepath = os.path.join(prefetch_dir, pf_file)
                
                # Check if executable name matches suspicious patterns
                is_suspicious = self._check_suspicious_patterns(exe_name)
                
                if is_suspicious:
                    times = self.get_file_times(filepath)
                    self.report_data['findings']['prefetch_suspicious'].append({
                        'file': pf_file,
                        'executable': exe_name,
                        'path': filepath,
                        'times': times,
                        'reason': 'Matches known exploit/cheat signature'
                    })
                    self.suspicious_files.append(filepath)
                    found_count += 1
                    print(f"{Fore.RED}[SUSPICIOUS] {exe_name} (Prefetch){Style.RESET_ALL}")
            
            # Also log all prefetch files (not just suspicious)
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
            
            self.report_data['findings']['prefetch_all'] = all_files
            print(f"{Fore.GREEN}[+] Prefetch scan complete. Found {len(all_files)} total, {found_count} suspicious{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Prefetch scan failed: {e}{Style.RESET_ALL}")
            self.report_data['findings']['prefetch_error'] = str(e)
    
    def scan_recent_files(self):
        """Scan Windows Recent files and shortcuts"""
        print(f"\n{Fore.CYAN}[*] Scanning Recent Files...{Style.RESET_ALL}")
        
        recent_dir = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Recent')
        if not os.path.exists(recent_dir):
            print(f"{Fore.YELLOW}[!] Recent directory not found{Style.RESET_ALL}")
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
                    
                    # Check if suspicious
                    if self._check_suspicious_patterns(item.lower()):
                        suspicious_recent.append({
                            'name': item,
                            'path': item_path,
                            'times': times
                        })
                        print(f"{Fore.RED}[SUSPICIOUS] {item} (Recent){Style.RESET_ALL}")
                except Exception as e:
                    pass
            
            self.report_data['findings']['recent_all'] = sorted(recent_files, 
                                                               key=lambda x: x['times'].get('accessed', ''), 
                                                               reverse=True)
            self.report_data['findings']['recent_suspicious'] = suspicious_recent
            print(f"{Fore.GREEN}[+] Recent files scan complete. Found {len(recent_files)} files, {len(suspicious_recent)} suspicious{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Recent files scan failed: {e}{Style.RESET_ALL}")
    
    def scan_temp_directories(self):
        """Scan temporary directories for suspicious files"""
        print(f"\n{Fore.CYAN}[*] Scanning Temporary Directories...{Style.RESET_ALL}")
        
        all_temp_files = []
        suspicious_temp_files = []
        
        for temp_dir in self.TEMP_DIRS:
            if not os.path.exists(temp_dir):
                continue
            
            print(f"  Scanning: {temp_dir}")
            
            try:
                for root, dirs, files in os.walk(temp_dir):
                    # Limit depth to avoid excessive scanning
                    if root.count(os.sep) - temp_dir.count(os.sep) > 3:
                        continue
                    
                    for file in files:
                        filepath = os.path.join(root, file)
                        
                        try:
                            # Skip system files
                            if file.startswith('~') or file.startswith('.'):
                                continue
                            
                            times = self.get_file_times(filepath)
                            
                            all_temp_files.append({
                                'name': file,
                                'path': filepath,
                                'directory': temp_dir,
                                'times': times
                            })
                            
                            # Check if suspicious
                            if self._check_suspicious_patterns(file.lower()):
                                suspicious_temp_files.append({
                                    'name': file,
                                    'path': filepath,
                                    'times': times
                                })
                                print(f"{Fore.RED}[SUSPICIOUS] {file} ({temp_dir}){Style.RESET_ALL}")
                        
                        except Exception as e:
                            pass
                        
                        # Limit to first 500 files per directory
                        if len(all_temp_files) > 500:
                            break
                    if len(all_temp_files) > 500:
                        break
                        
            except PermissionError:
                print(f"  {Fore.YELLOW}[!] Permission denied: {temp_dir}{Style.RESET_ALL}")
            except Exception as e:
                print(f"  {Fore.YELLOW}[!] Error scanning {temp_dir}: {e}{Style.RESET_ALL}")
        
        self.report_data['findings']['temp_all'] = sorted(all_temp_files, 
                                                         key=lambda x: x['times'].get('accessed', ''), 
                                                         reverse=True)[:200]  # Limit to 200 most recent
        self.report_data['findings']['temp_suspicious'] = suspicious_temp_files
        
        print(f"{Fore.GREEN}[+] Temp directories scan complete. Found {len(all_temp_files)} files, {len(suspicious_temp_files)} suspicious{Style.RESET_ALL}")
    
    def scan_program_files(self):
        """Scan Program Files for suspicious applications"""
        print(f"\n{Fore.CYAN}[*] Scanning Program Files...{Style.RESET_ALL}")
        
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
                            'location': prog_dir
                        })
                        print(f"{Fore.RED}[SUSPICIOUS] {item} (Program Files){Style.RESET_ALL}")
                        
            except PermissionError:
                pass
            except Exception as e:
                pass
        
        self.report_data['findings']['program_files_suspicious'] = suspicious_programs
        print(f"{Fore.GREEN}[+] Program Files scan complete. Found {len(suspicious_programs)} suspicious{Style.RESET_ALL}")
    
    def scan_startup_folder(self):
        """Scan startup folders for malicious programs"""
        print(f"\n{Fore.CYAN}[*] Scanning Startup Folders...{Style.RESET_ALL}")
        
        startup_dirs = [
            os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup'),
            os.path.expandvars(r'%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup'),
            os.path.expandvars(r'%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'),
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
                            'times': times
                        })
                        print(f"{Fore.RED}[SUSPICIOUS] {item} (Startup){Style.RESET_ALL}")
                        
            except Exception as e:
                pass
        
        self.report_data['findings']['startup_all'] = all_startup
        self.report_data['findings']['startup_suspicious'] = suspicious_startup
        print(f"{Fore.GREEN}[+] Startup scan complete. Found {len(all_startup)} items, {len(suspicious_startup)} suspicious{Style.RESET_ALL}")
    
    def check_browser_history(self):
        """Extract browser history metadata"""
        print(f"\n{Fore.CYAN}[*] Scanning Browser History...{Style.RESET_ALL}")
        
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
                print(f"{Fore.GREEN}[+] {browser} history found{Style.RESET_ALL}")
        
        self.report_data['findings']['browser_history'] = browser_info
    
    def _check_suspicious_patterns(self, name):
        """Check if name matches known exploit/cheat patterns"""
        name_lower = name.lower()
        
        for category, patterns in self.EXPLOIT_SIGNATURES.items():
            for pattern in patterns:
                if pattern in name_lower:
                    return True
        
        # Additional heuristics
        suspicious_keywords = [
            'trainer', 'hack', 'crack', 'keygen', 'cheat', 'inject',
            'patcher', 'mod', 'exploit', 'bypass', 'spoofer', 'unban'
        ]
        
        for keyword in suspicious_keywords:
            if keyword in name_lower:
                return True
        
        return False
    
    def generate_text_report(self, filepath):
        """Generate a detailed text report"""
        print(f"\n{Fore.CYAN}[*] Generating Text Report...{Style.RESET_ALL}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("WINDOWS PC SECURITY AUDIT REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Scan Date & Time: {self.report_data['scan_date']}\n")
            f.write(f"Computer Name: {self.report_data['computer_name']}\n")
            f.write(f"Username: {self.report_data['username']}\n")
            f.write(f"Report Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Prefetch Summary
            f.write("=" * 80 + "\n")
            f.write("WINDOWS PREFETCH ANALYSIS\n")
            f.write("=" * 80 + "\n\n")
            
            suspicious = self.report_data['findings'].get('prefetch_suspicious', [])
            if suspicious:
                f.write(f"⚠️  SUSPICIOUS EXECUTABLES FOUND: {len(suspicious)}\n\n")
                for item in suspicious:
                    f.write(f"  Executable: {item['executable']}\n")
                    f.write(f"  Prefetch File: {item['file']}\n")
                    f.write(f"  Full Path: {item['path']}\n")
                    if 'times' in item:
                        f.write(f"  Last Accessed: {item['times'].get('accessed', 'N/A')}\n")
                        f.write(f"  Last Modified: {item['times'].get('modified', 'N/A')}\n")
                        f.write(f"  Created: {item['times'].get('created', 'N/A')}\n")
                    f.write(f"  Reason: {item.get('reason', 'N/A')}\n")
                    f.write("\n")
            else:
                f.write("✓ No suspicious executables found in Prefetch.\n\n")
            
            all_pf = self.report_data['findings'].get('prefetch_all', [])
            f.write(f"TOTAL PREFETCH FILES: {len(all_pf)}\n\n")
            f.write("Recent Prefetch Entries (Last 20):\n")
            f.write("-" * 80 + "\n")
            for item in sorted(all_pf, key=lambda x: x.get('times', {}).get('accessed', ''), reverse=True)[:20]:
                f.write(f"  {item['executable']:<40} Accessed: {item.get('times', {}).get('accessed', 'N/A')}\n")
            f.write("\n")
            
            # Recent Files
            f.write("=" * 80 + "\n")
            f.write("WINDOWS RECENT FILES\n")
            f.write("=" * 80 + "\n\n")
            
            recent_sus = self.report_data['findings'].get('recent_suspicious', [])
            if recent_sus:
                f.write(f"⚠️  SUSPICIOUS FILES: {len(recent_sus)}\n\n")
                for item in recent_sus:
                    f.write(f"  File: {item['name']}\n")
                    f.write(f"  Path: {item['path']}\n")
                    f.write(f"  Last Accessed: {item.get('times', {}).get('accessed', 'N/A')}\n\n")
            
            recent_all = self.report_data['findings'].get('recent_all', [])
            f.write(f"TOTAL RECENT FILES: {len(recent_all)}\n\n")
            f.write("Most Recent Files (Last 30):\n")
            f.write("-" * 80 + "\n")
            for item in recent_all[:30]:
                f.write(f"  {item['name']:<50} Accessed: {item.get('times', {}).get('accessed', 'N/A')}\n")
            f.write("\n")
            
            # Temporary Files
            f.write("=" * 80 + "\n")
            f.write("TEMPORARY FILES ANALYSIS\n")
            f.write("=" * 80 + "\n\n")
            
            temp_sus = self.report_data['findings'].get('temp_suspicious', [])
            if temp_sus:
                f.write(f"⚠️  SUSPICIOUS TEMP FILES: {len(temp_sus)}\n\n")
                for item in temp_sus[:50]:  # Limit to 50
                    f.write(f"  File: {item['name']}\n")
                    f.write(f"  Path: {item['path']}\n")
                    f.write(f"  Last Accessed: {item.get('times', {}).get('accessed', 'N/A')}\n\n")
            
            temp_all = self.report_data['findings'].get('temp_all', [])
            f.write(f"TOTAL SCANNED TEMP FILES: {len(temp_all)}\n\n")
            
            # Program Files
            f.write("=" * 80 + "\n")
            f.write("SUSPICIOUS PROGRAM FILES\n")
            f.write("=" * 80 + "\n\n")
            
            prog_sus = self.report_data['findings'].get('program_files_suspicious', [])
            if prog_sus:
                f.write(f"⚠️  SUSPICIOUS PROGRAMS: {len(prog_sus)}\n\n")
                for item in prog_sus:
                    f.write(f"  Program: {item['name']}\n")
                    f.write(f"  Path: {item['path']}\n")
                    f.write(f"  Location: {item.get('location', 'N/A')}\n")
                    f.write(f"  Last Accessed: {item.get('times', {}).get('accessed', 'N/A')}\n\n")
            else:
                f.write("✓ No suspicious programs found.\n\n")
            
            # Startup Programs
            f.write("=" * 80 + "\n")
            f.write("STARTUP PROGRAMS\n")
            f.write("=" * 80 + "\n\n")
            
            startup_all = self.report_data['findings'].get('startup_all', [])
            startup_sus = self.report_data['findings'].get('startup_suspicious', [])
            
            if startup_sus:
                f.write(f"⚠️  SUSPICIOUS STARTUP ITEMS: {len(startup_sus)}\n\n")
                for item in startup_sus:
                    f.write(f"  Program: {item['name']}\n")
                    f.write(f"  Path: {item['path']}\n")
                    f.write(f"  Last Accessed: {item.get('times', {}).get('accessed', 'N/A')}\n\n")
            
            f.write(f"TOTAL STARTUP ITEMS: {len(startup_all)}\n\n")
            for item in startup_all:
                f.write(f"  {item['name']:<50} Accessed: {item.get('times', {}).get('accessed', 'N/A')}\n")
            f.write("\n")
            
            # Browser History
            f.write("=" * 80 + "\n")
            f.write("BROWSER HISTORY METADATA\n")
            f.write("=" * 80 + "\n\n")
            
            browser_info = self.report_data['findings'].get('browser_history', [])
            for item in browser_info:
                f.write(f"  {item['browser']}: {item['path']}\n")
                f.write(f"    Last Modified: {item.get('times', {}).get('modified', 'N/A')}\n")
            f.write("\n")
            
            # Summary
            f.write("=" * 80 + "\n")
            f.write("SUMMARY & RECOMMENDATIONS\n")
            f.write("=" * 80 + "\n\n")
            
            total_suspicious = (len(suspicious) + len(recent_sus) + len(temp_sus) + 
                              len(prog_sus) + len(startup_sus))
            
            f.write(f"Total Suspicious Items Found: {total_suspicious}\n\n")
            
            if total_suspicious > 0:
                f.write("⚠️  RECOMMENDATIONS:\n")
                f.write("  1. Research each suspicious file before deletion\n")
                f.write("  2. Cross-reference with known legitimate software\n")
                f.write("  3. Check file properties and digital signatures\n")
                f.write("  4. Consider running additional security scans\n")
                f.write("  5. Isolate affected system if malware is confirmed\n")
            else:
                f.write("✓ No obvious suspicious activity detected.\n")
                f.write("  Note: Absence of known signatures doesn't guarantee security.\n")
                f.write("  Consider running full antivirus/malware scans regularly.\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        print(f"{Fore.GREEN}[+] Text report saved: {filepath}{Style.RESET_ALL}")
    
    def generate_json_report(self, filepath):
        """Generate a detailed JSON report"""
        print(f"\n{Fore.CYAN}[*] Generating JSON Report...{Style.RESET_ALL}")
        
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
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)
        
        print(f"{Fore.GREEN}[+] JSON report saved: {filepath}{Style.RESET_ALL}")
    
    def run_full_scan(self):
        """Execute complete security audit"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  WINDOWS PC SECURITY AUDIT TOOL{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        # Check admin rights
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print(f"{Fore.YELLOW}[!] WARNING: Not running as Administrator.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}    Some scans may be limited. For best results, run as Admin.{Style.RESET_ALL}\n")
        except:
            pass
        
        try:
            self.scan_prefetch_files()
            self.scan_recent_files()
            self.scan_startup_folder()
            self.scan_program_files()
            self.scan_temp_directories()
            self.check_browser_history()
            
            # Generate reports
            report_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            
            txt_report = os.path.join(report_dir, f'PC_Security_Audit_{timestamp}.txt')
            json_report = os.path.join(report_dir, f'PC_Security_Audit_{timestamp}.json')
            
            self.generate_text_report(txt_report)
            self.generate_json_report(json_report)
            
            print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}SCAN COMPLETE!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
            print(f"\n📄 Reports saved to Desktop:")
            print(f"   • {txt_report}")
            print(f"   • {json_report}\n")
            
        except Exception as e:
            print(f"\n{Fore.RED}[FATAL ERROR] {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    audit = PCSecurityAudit()
    audit.run_full_scan()


if __name__ == '__main__':
    main()
