#!/usr/bin/env python3
"""
System Information Utility
Displays useful system information - great for checking servers and workstations.
"""

import platform
import psutil
import json
from datetime import datetime

def get_system_info():
    """Collect comprehensive system information."""
    return {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.architecture()[0],
            "hostname": platform.node(),
            "python_version": platform.python_version()
        },
        "hardware": {
            "cpu_cores": psutil.cpu_count(logical=False),
            "logical_processors": psutil.cpu_count(logical=True),
            "cpu_freq_mhz": round(psutil.cpu_freq().current) if psutil.cpu_freq() else "N/A",
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 1),
            "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 1)
        },
        "current_usage": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "uptime": {
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "uptime_hours": round((datetime.now().timestamp() - psutil.boot_time()) / 3600, 1)
        }
    }

def print_system_info():
    """Display system information in a readable format."""
    info = get_system_info()
    
    print("🖥️  System Information Report")
    print("=" * 50)
    print(f"Generated: {info['timestamp']}")
    print()
    
    print("💻 System Details:")
    sys_info = info['system']
    print(f"  OS: {sys_info['os']} ({sys_info['architecture']})")
    print(f"  Hostname: {sys_info['hostname']}")
    print(f"  Python: {sys_info['python_version']}")
    print()
    
    print("⚙️  Hardware:")
    hw = info['hardware']
    print(f"  CPU: {hw['cpu_cores']} cores / {hw['logical_processors']} threads")
    print(f"  CPU Freq: {hw['cpu_freq_mhz']} MHz")
    print(f"  Memory: {hw['memory_gb']} GB")
    print(f"  Disk: {hw['disk_total_gb']} GB total, {hw['disk_free_gb']} GB free")
    print()
    
    print("📊 Current Usage:")
    usage = info['current_usage']
    print(f"  CPU: {usage['cpu_percent']}%")
    print(f"  Memory: {usage['memory_percent']}%")
    print(f"  Disk: {usage['disk_percent']}%")
    print()
    
    print("⏰ Uptime:")
    uptime = info['uptime']
    print(f"  Boot time: {uptime['boot_time']}")
    print(f"  Uptime: {uptime['uptime_hours']} hours")
    print()
    
def export_json(filename="system_info.json"):
    """Export system information to JSON file."""
    info = get_system_info()
    with open(filename, 'w') as f:
        json.dump(info, f, indent=2)
    print(f"✅ System info exported to {filename}")

def main():
    """Main function with command line options."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        export_json()
    else:
        print_system_info()
        print("💡 Tip: Use --json flag to export data to JSON file")

if __name__ == "__main__":
    main()