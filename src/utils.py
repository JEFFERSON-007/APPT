"""
Utility functions for the penetration testing toolkit
"""
import re
import socket
import json
from pathlib import Path
from typing import List, Optional, Dict
import sys


def is_valid_ip(host: str) -> bool:
    """Check if host is valid IPv4 address or hostname"""
    # IPv4 validation
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, host):
        try:
            socket.inet_aton(host)
            return True
        except socket.error:
            return False
    
    # Hostname validation
    hostname_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
    if re.match(hostname_pattern, host):
        return True
    
    return False


def load_wordlist(filepath: str) -> List[str]:
    """Load words from file"""
    try:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []


def save_results(results: List[Dict], output_file: str, format: str = "json"):
    """Save results to file"""
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
        elif format == "csv":
            import csv
            if results and isinstance(results[0], dict):
                with open(output_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
        
        print(f"✅ Results saved to: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving results: {e}")
        return False


def print_banner():
    """Print application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║         Advanced Penetration Testing Toolkit v2.1             ║
║           Professional Security Assessment Tool              ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def parse_target_list(target_spec: str) -> List[str]:
    """Parse target specification (file or single host)"""
    targets = []
    
    # Check if it's a file
    if target_spec.endswith('.txt') or target_spec.endswith('.lst'):
        targets = load_wordlist(target_spec)
    else:
        # Single target
        if is_valid_ip(target_spec):
            targets = [target_spec]
        else:
            print(f"❌ Invalid target: {target_spec}")
    
    return targets


class Logger:
    """Simple logging utility"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def debug(self, msg: str):
        if self.verbose:
            print(f"🔍 {msg}")
    
    def info(self, msg: str):
        print(f"ℹ️  {msg}")
    
    def warning(self, msg: str):
        print(f"⚠️  {msg}")
    
    def error(self, msg: str):
        print(f"❌ {msg}")
    
    def success(self, msg: str):
        print(f"✅ {msg}")


def progress_bar(current: int, total: int, prefix: str = "", length: int = 40):
    """Print progress bar"""
    if total == 0:
        return
    
    percent = current / total
    filled = int(length * percent)
    bar = '█' * filled + '░' * (length - filled)
    
    sys.stdout.write(f'\r{prefix} |{bar}| {percent*100:.1f}%')
    sys.stdout.flush()


def format_time(seconds: float) -> str:
    """Format seconds to readable time"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}h"
