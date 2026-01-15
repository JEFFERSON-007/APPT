"""
Advanced Port Scanner with service fingerprinting
Inspired by Hydra and nmap
"""
import socket
import json
from threading import Thread, Lock
from queue import Queue, Empty
from time import time
from typing import List, Dict, Tuple, Optional
import struct
import sys

# Service fingerprints - common banners and responses
SERVICE_FINGERPRINTS = {
    21: {"name": "FTP", "probe": b"", "response_patterns": [b"220"]},
    22: {"name": "SSH", "probe": b"", "response_patterns": [b"SSH"]},
    25: {"name": "SMTP", "probe": b"EHLO\r\n", "response_patterns": [b"250"]},
    53: {"name": "DNS", "probe": b"", "response_patterns": []},
    80: {"name": "HTTP", "probe": b"HEAD / HTTP/1.0\r\n\r\n", "response_patterns": [b"HTTP"]},
    110: {"name": "POP3", "probe": b"", "response_patterns": [b"+OK"]},
    143: {"name": "IMAP", "probe": b"", "response_patterns": [b"OK IMAP"]},
    443: {"name": "HTTPS", "probe": b"HEAD / HTTP/1.0\r\n\r\n", "response_patterns": [b"HTTP"]},
    445: {"name": "SMB", "probe": b"", "response_patterns": []},
    3306: {"name": "MySQL", "probe": b"", "response_patterns": [b"mysql"]},
    3389: {"name": "RDP", "probe": b"", "response_patterns": []},
    5432: {"name": "PostgreSQL", "probe": b"", "response_patterns": []},
    5900: {"name": "VNC", "probe": b"", "response_patterns": [b"RFB"]},
    6379: {"name": "Redis", "probe": b"PING\r\n", "response_patterns": [b"+PONG"]},
    8080: {"name": "HTTP-ALT", "probe": b"HEAD / HTTP/1.0\r\n\r\n", "response_patterns": [b"HTTP"]},
    8443: {"name": "HTTPS-ALT", "probe": b"HEAD / HTTP/1.0\r\n\r\n", "response_patterns": [b"HTTP"]},
    27017: {"name": "MongoDB", "probe": b"", "response_patterns": []},
    9200: {"name": "Elasticsearch", "probe": b"", "response_patterns": []},
}

COMMON_PORTS = [21, 22, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5900, 8080, 8443]


class PortScanner:
    """Advanced multi-threaded port scanner with service detection"""
    
    def __init__(self, host: str, timeout: float = 2.0, verbose: bool = False):
        self.host = host
        self.timeout = timeout
        self.verbose = verbose
        self.open_ports = []
        self.lock = Lock()
        self.start_time = None
        self.total_ports = 0
        self.scanned = 0
    
    def get_service_name(self, port: int) -> str:
        """Get service name for port"""
        if port in SERVICE_FINGERPRINTS:
            return SERVICE_FINGERPRINTS[port]["name"]
        return "Unknown"
    
    def scan_port(self, port: int) -> Tuple[bool, Optional[str]]:
        """Scan a single port and attempt service detection"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, port))
            
            if result == 0:
                service = self.get_service_name(port)
                
                # Try service fingerprinting if probe available
                version = None
                if port in SERVICE_FINGERPRINTS:
                    version = self._fingerprint_service(port)
                
                with self.lock:
                    port_info = {
                        "port": port,
                        "service": service,
                        "version": version,
                        "state": "open"
                    }
                    self.open_ports.append(port_info)
                    print(f"🟢 {port:5d}/tcp  {service:15} {version or ''}")
                
                sock.close()
                return True, service
            
            if self.verbose:
                sys.stdout.write(f"\r⚫ Scanning: {self.scanned}/{self.total_ports} ports")
                sys.stdout.flush()
            
            sock.close()
            return False, None
            
        except socket.timeout:
            if self.verbose:
                print(f"⏱️  Port {port}: Timeout")
        except Exception as e:
            if self.verbose:
                print(f"❌ Port {port}: {str(e)[:50]}")
        
        return False, None
    
    def _fingerprint_service(self, port: int) -> Optional[str]:
        """Attempt to identify service version"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, port))
            
            # Send probe if available
            fingerprint = SERVICE_FINGERPRINTS.get(port, {})
            if fingerprint.get("probe"):
                sock.send(fingerprint["probe"])
            
            # Receive banner
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            
            # Parse banner for version info
            if banner:
                return banner[:50]  # Return first 50 chars of banner
        except:
            pass
        
        return None
    
    def worker(self, queue: Queue):
        """Worker thread for scanning"""
        while True:
            try:
                port = queue.get(timeout=1)
            except Empty:
                break
            
            if port is None:
                break
            
            self.scan_port(port)
            
            with self.lock:
                self.scanned += 1
            
            queue.task_done()
    
    def parse_port_spec(self, port_spec: str) -> List[int]:
        """Parse port specification: 1-1000, 80,443,22, or single port"""
        ports = []
        try:
            if "-" in port_spec:
                start, end = port_spec.split("-")
                ports = list(range(int(start.strip()), int(end.strip()) + 1))
            elif "," in port_spec:
                ports = [int(p.strip()) for p in port_spec.split(",")]
            else:
                ports = [int(port_spec.strip())]
        except ValueError:
            print(f"❌ Invalid port specification: {port_spec}")
            return []
        
        return [p for p in ports if 1 <= p <= 65535]
    
    def scan(self, ports: List[int], num_threads: int = 20) -> List[Dict]:
        """Execute scan with multiple threads"""
        self.total_ports = len(ports)
        
        print(f"\n🔍 Port Scan Summary")
        print(f"   Target: {self.host}")
        print(f"   Ports: {len(ports)}")
        print(f"   Threads: {num_threads}")
        print("-" * 60)
        
        self.start_time = time()
        queue = Queue()
        threads = []
        
        # Create workers
        for _ in range(min(num_threads, len(ports))):
            t = Thread(target=self.worker, args=(queue,), daemon=True)
            t.start()
            threads.append(t)
        
        # Queue all ports
        for port in ports:
            queue.put(port)
        
        queue.join()
        
        # Stop workers
        for _ in range(num_threads):
            queue.put(None)
        for t in threads:
            t.join()
        
        elapsed = time() - self.start_time
        print("-" * 60)
        
        if self.open_ports:
            print(f"\n✅ {len(self.open_ports)} open port(s) found:")
            for p in sorted(self.open_ports, key=lambda x: x["port"]):
                print(f"   {p['port']:5d}/tcp {p['service']:15} {p['version'] or ''}")
        else:
            print(f"\n❌ No open ports found")
        
        print(f"\n📊 Scan Statistics:")
        print(f"   Ports: {len(ports)}")
        print(f"   Time: {elapsed:.2f}s")
        print(f"   Rate: {len(ports)/elapsed:.1f} ports/sec")
        
        return self.open_ports


def scan(host: str, port_spec: str = "1-1000", timeout: float = 2.0, 
         num_threads: int = 20, quick: bool = False, verbose: bool = False,
         output_format: str = "text") -> List[Dict]:
    """Convenience function for scanning"""
    scanner = PortScanner(host, timeout, verbose)
    
    if quick:
        ports = COMMON_PORTS
    else:
        ports = scanner.parse_port_spec(port_spec)
    
    if not ports:
        return []
    
    results = scanner.scan(ports, num_threads)
    
    if output_format == "json":
        return json.dumps({"host": host, "ports": results}, indent=2)
    
    return results
