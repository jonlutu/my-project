#!/usr/bin/env python3
"""
Simple System Information Utility
Uses only built-in Python modules - no external dependencies required.
"""

import platform
import os
import subprocess
import json
from datetime import datetime

def get_basic_system_info():
    """Get system information using only built-in modules."""
    info = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.architecture()[0],
            "hostname": platform.node(),
            "python_version": platform.python_version(),
            "user": os.getenv('USER', 'unknown')
        }
    }
    
    # Try to get additional info using system commands (Linux/Unix)
    try:
        # Get uptime (Linux)
        if platform.system() == "Linux":
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
                info["uptime_hours"] = round(uptime_seconds / 3600, 1)
    except:
        pass
    
    # Try to get disk space using df command
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                info["disk"] = {
                    "total": parts[1],
                    "used": parts[2], 
                    "available": parts[3],
                    "usage_percent": parts[4]
                }
    except:
        pass
        
    # Try to get memory info (Linux)
    try:
        if platform.system() == "Linux":
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                for line in meminfo.split('\n'):
                    if 'MemTotal:' in line:
                        kb = int(line.split()[1])
                        info["memory_gb"] = round(kb / 1024 / 1024, 1)
                        break
    except:
        pass
        
    return info

def print_system_info():
    """Display system information in a readable format."""
    info = get_basic_system_info()
    
    print("🖥️  Simple System Information")
    print("=" * 40)
    print(f"Generated: {info['timestamp']}")
    print()
    
    sys_info = info['system']
    print("💻 System:")
    print(f"  OS: {sys_info['os']} {sys_info['os_release']}")
    print(f"  Architecture: {sys_info['architecture']}")
    print(f"  Hostname: {sys_info['hostname']}")
    print(f"  User: {sys_info['user']}")
    print(f"  Python: {sys_info['python_version']}")
    print()
    
    if 'uptime_hours' in info:
        print(f"⏰ Uptime: {info['uptime_hours']} hours")
        print()
        
    if 'memory_gb' in info:
        print(f"💾 Memory: {info['memory_gb']} GB total")
        print()
        
    if 'disk' in info:
        disk = info['disk']
        print("💽 Disk Usage:")
        print(f"  Total: {disk['total']}")
        print(f"  Used: {disk['used']} ({disk['usage_percent']})")
        print(f"  Available: {disk['available']}")
        print()

def main():
    """Main function."""
    print_system_info()
    print("💡 This version uses only built-in Python modules.")
    print("💡 For advanced system monitoring, install requirements.txt")

if __name__ == "__main__":
    main()