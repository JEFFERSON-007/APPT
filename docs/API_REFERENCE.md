# API Reference - APPT

**Complete API Documentation for All Modules**

---

## Table of Contents

1. [Port Scanner API](#port-scanner-api)
2. [Brute Forcer API](#brute-forcer-api)
3. [Configuration Manager API](#configuration-manager-api)
4. [Reporting API](#reporting-api)
5. [Utilities API](#utilities-api)
6. [Exceptions & Logging API](#exceptions--logging-api)

---

## Port Scanner API

**Module:** `src.port_scanner`

### PortScanner Class

```python
class PortScanner:
    """Advanced multi-threaded port scanner with service detection"""
```

#### Constructor

```python
def __init__(self, host: str, timeout: float = 2.0, verbose: bool = False)
```

**Parameters:**
- `host` (str): Target IP address or hostname
- `timeout` (float, optional): Connection timeout in seconds. Default: 2.0
- `verbose` (bool, optional): Enable verbose output. Default: False

**Example:**
```python
from src.port_scanner import PortScanner

scanner = PortScanner("192.168.1.1", timeout=3.0, verbose=True)
```

#### Methods

##### scan_port()

```python
def scan_port(self, port: int) -> Tuple[bool, Optional[str]]
```

**Purpose:** Scan a single port and attempt service detection.

**Parameters:**
- `port` (int): Port number to scan (1-65535)

**Returns:**
- `Tuple[bool, Optional[str]]`
  - First element: `True` if port open, `False` if closed, `None` on error
  - Second element: Service name if detected, otherwise `None`

**Example:**
```python
is_open, service = scanner.scan_port(22)
if is_open:
    print(f"Port 22 open with service: {service}")  # SSH
```

##### get_service_name()

```python
def get_service_name(self, port: int) -> str
```

**Purpose:** Get service name for a port number.

**Parameters:**
- `port` (int): Port number

**Returns:**
- `str`: Service name (e.g., "SSH", "HTTP") or "Unknown"

**Example:**
```python
service = scanner.get_service_name(22)  # Returns "SSH"
```

##### parse_port_spec()

```python
def parse_port_spec(self, port_spec: str) -> List[int]
```

**Purpose:** Parse port specification string into list of port numbers.

**Parameters:**
- `port_spec` (str): Port specification
  - Range: `"1-1000"` → `[1, 2, ..., 1000]`
  - List: `"80,443,22"` → `[80, 443, 22]`
  - Single: `"22"` → `[22]`

**Returns:**
- `List[int]`: List of valid port numbers (1-65535)

**Example:**
```python
ports = scanner.parse_port_spec("1-100")
# Returns: [1, 2, 3, ..., 100]

ports = scanner.parse_port_spec("80,443,22")
# Returns: [80, 443, 22]
```

##### worker()

```python
def worker(self, queue: Queue)
```

**Purpose:** Worker thread function for concurrent port scanning.

**Parameters:**
- `queue` (Queue): Queue containing port numbers to scan

**Note:** Called internally by `scan()` method. Multiple worker threads pull ports from queue.

##### scan()

```python
def scan(self, ports: List[int], num_threads: int = 20) -> List[Dict]
```

**Purpose:** Execute multi-threaded port scan.

**Parameters:**
- `ports` (List[int]): List of port numbers to scan
- `num_threads` (int, optional): Number of worker threads. Default: 20

**Returns:**
- `List[Dict]`: List of open port information
  ```python
  [
      {
          "port": 22,
          "service": "SSH",
          "version": "OpenSSH 7.4",
          "state": "open"
      },
      ...
  ]
  ```

**Example:**
```python
ports = [22, 80, 443, 3306]
results = scanner.scan(ports, num_threads=10)

for port_info in results:
    print(f"Port {port_info['port']}: {port_info['service']}")
```

### Module-Level Functions

#### scan()

```python
def scan(host: str, port_spec: str = "1-1000", timeout: float = 2.0,
         num_threads: int = 20, quick: bool = False, verbose: bool = False,
         output_format: str = "text") -> Union[List[Dict], str]
```

**Purpose:** Convenience function to scan a target.

**Parameters:**
- `host` (str): Target IP or hostname
- `port_spec` (str, optional): Port specification. Default: "1-1000"
- `timeout` (float, optional): Connection timeout. Default: 2.0
- `num_threads` (int, optional): Number of threads. Default: 20
- `quick` (bool, optional): Use common ports only. Default: False
- `verbose` (bool, optional): Verbose output. Default: False
- `output_format` (str, optional): Output format ("text" or "json"). Default: "text"

**Returns:**
- `Union[List[Dict], str]`: Results as list (text) or JSON string

**Example:**
```python
from src.port_scanner import scan

results = scan("192.168.1.1", port_spec="1-1000", num_threads=50)
for port_info in results:
    print(f"{port_info['port']}: {port_info['service']}")
```

### Constants

#### SERVICE_FINGERPRINTS

```python
SERVICE_FINGERPRINTS = {
    21: {"name": "FTP", "probe": b"", "response_patterns": [b"220"]},
    22: {"name": "SSH", "probe": b"", "response_patterns": [b"SSH"]},
    ...
}
```

**Purpose:** Dictionary mapping port numbers to service information for fingerprinting.

#### COMMON_PORTS

```python
COMMON_PORTS = [21, 22, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5900, 8080, 8443]
```

**Purpose:** List of frequently used ports for quick scanning.

---

## Brute Forcer API

**Module:** `src.brute_forcer`

### AttackMode Enum

```python
class AttackMode(Enum):
    SINGLE = "single"      # One password per user
    LOOP = "loop"          # All passwords for each user
    COMBO = "combo"        # Paired user:password credentials
```

**Usage:**
```python
from src.brute_forcer import AttackMode

mode = AttackMode.LOOP  # Default attack mode
```

### Credential Dataclass

```python
@dataclass
class Credential:
    username: str
    password: str
```

**Properties:**
- `username` (str): Username for authentication
- `password` (str): Password for authentication

**Methods:**
- `__str__()`: Returns "username:password" format

**Example:**
```python
from src.brute_forcer import Credential

cred = Credential("admin", "password123")
print(cred)  # Output: admin:password123
```

### RateLimiter Class

```python
class RateLimiter:
    """Rate limiting to avoid detection"""
```

#### Constructor

```python
def __init__(self, delay: float = 0.1, burst_size: int = 10)
```

**Parameters:**
- `delay` (float, optional): Delay between attempts in seconds. Default: 0.1
- `burst_size` (int, optional): Attempts before enforcing delay. Default: 10

#### Methods

##### wait()

```python
def wait(self)
```

**Purpose:** Apply rate limiting before attempt. Call before each login attempt.

**Example:**
```python
limiter = RateLimiter(delay=0.5, burst_size=5)

for attempt in attempts:
    limiter.wait()  # Enforces rate limit
    try_login(attempt)
```

### BruteForcer Class

```python
class BruteForcer:
    """Advanced multi-threaded brute force attacker"""
```

#### Constructor

```python
def __init__(self, host: str, port: Optional[int] = None,
             protocol: str = "ftp", timeout: float = 5.0,
             verbose: bool = False)
```

**Parameters:**
- `host` (str): Target IP or hostname
- `port` (Optional[int]): Target port. If None, auto-detected from protocol
- `protocol` (str, optional): Protocol name. Default: "ftp"
  - Supported: "ftp", "ssh", "http", "https", "telnet", "mysql", "postgres"
- `timeout` (float, optional): Connection timeout. Default: 5.0
- `verbose` (bool, optional): Verbose output. Default: False

**Example:**
```python
from src.brute_forcer import BruteForcer

attacker = BruteForcer(
    host="192.168.1.100",
    protocol="ssh",
    timeout=10.0,
    verbose=True
)
```

#### Properties

- `host` (str): Target host
- `port` (int): Target port
- `protocol` (str): Protocol name
- `timeout` (float): Connection timeout
- `verbose` (bool): Verbose flag
- `found_credentials` (List[Credential]): Found valid credentials
- `attempts` (int): Total authentication attempts
- `failures` (int): Failed authentication attempts
- `start_time` (float): Attack start timestamp

#### Methods

##### attempt_login()

```python
def attempt_login(self, username: str, password: str) -> Optional[bool]
```

**Purpose:** Attempt login with credentials using configured protocol.

**Parameters:**
- `username` (str): Username to try
- `password` (str): Password to try

**Returns:**
- `bool`: `True` if successful, `False` if failed, `None` if error

**Example:**
```python
result = attacker.attempt_login("admin", "password123")
if result is True:
    print("Success!")
elif result is False:
    print("Failed")
else:
    print("Error")
```

##### attack()

```python
def attack(self, usernames: List[str], passwords: List[str],
           num_threads: int = 10, attack_mode: AttackMode = AttackMode.LOOP,
           stop_on_success: bool = False) -> List[Credential]
```

**Purpose:** Execute multi-threaded brute force attack.

**Parameters:**
- `usernames` (List[str]): List of usernames to try
- `passwords` (List[str]): List of passwords to try
- `num_threads` (int, optional): Number of worker threads. Default: 10
- `attack_mode` (AttackMode, optional): Attack mode. Default: LOOP
- `stop_on_success` (bool, optional): Stop after first success. Default: False

**Returns:**
- `List[Credential]`: List of valid credentials found

**Example:**
```python
users = ["admin", "root", "user"]
passwords = ["password", "123456", "admin"]

credentials = attacker.attack(
    usernames=users,
    passwords=passwords,
    num_threads=20,
    attack_mode=AttackMode.LOOP,
    stop_on_success=True
)

for cred in credentials:
    print(f"Found: {cred}")
```

##### worker()

```python
def worker(self, queue: Queue)
```

**Purpose:** Worker thread function for concurrent attack.

**Parameters:**
- `queue` (Queue): Queue containing Credential objects

**Note:** Called internally by `attack()` method.

### Module-Level Functions

#### attack()

```python
def attack(host: str, usernames: List[str], passwords: List[str],
           protocol: str = "ftp", port: Optional[int] = None,
           num_threads: int = 10, timeout: float = 5.0,
           attack_mode: str = "loop", stop_on_success: bool = False,
           verbose: bool = False) -> List[Credential]
```

**Purpose:** Convenience function to perform brute force attack.

**Parameters:**
- `host` (str): Target IP or hostname
- `usernames` (List[str]): Usernames to try
- `passwords` (List[str]): Passwords to try
- `protocol` (str, optional): Protocol. Default: "ftp"
- `port` (Optional[int]): Port number. Default: auto-detect
- `num_threads` (int, optional): Worker threads. Default: 10
- `timeout` (float, optional): Connection timeout. Default: 5.0
- `attack_mode` (str, optional): "single", "loop", or "combo". Default: "loop"
- `stop_on_success` (bool, optional): Stop on first success. Default: False
- `verbose` (bool, optional): Verbose output. Default: False

**Returns:**
- `List[Credential]`: Found credentials

**Example:**
```python
from src.brute_forcer import attack

creds = attack(
    host="192.168.1.100",
    usernames=["admin"],
    passwords=["password", "admin123"],
    protocol="ssh",
    num_threads=10
)
```

---

## Configuration Manager API

**Module:** `src.config_manager`

### ConfigManager Class

```python
class ConfigManager:
    """Manages configuration and attack profiles"""
```

#### Constructor

```python
def __init__(self, config_file: str = "config/default.conf")
```

**Parameters:**
- `config_file` (str, optional): Path to configuration file. Default: "config/default.conf"

#### Methods

##### load_config()

```python
def load_config(self, filepath: str) -> Dict
```

**Purpose:** Load INI-format configuration file.

**Parameters:**
- `filepath` (str): Path to config file

**Returns:**
- `Dict`: Configuration dictionary

##### load_profiles()

```python
def load_profiles(self) -> Dict[str, Dict]
```

**Purpose:** Load YAML attack profiles.

**Returns:**
- `Dict[str, Dict]`: Dictionary of profiles

##### get_profile()

```python
def get_profile(self, name: str) -> Dict
```

**Purpose:** Get specific attack profile by name.

**Parameters:**
- `name` (str): Profile name (e.g., "quick_scan", "ssh_bruteforce")

**Returns:**
- `Dict`: Profile configuration

**Example:**
```python
from src.config_manager import ConfigManager

config = ConfigManager()
profile = config.get_profile("quick_scan")
print(profile["scanner"]["threads"])  # 50
```

##### merge_args_with_profile()

```python
def merge_args_with_profile(self, args: Any, profile_name: str) -> Dict
```

**Purpose:** Merge CLI arguments with profile settings (CLI overrides profile).

**Parameters:**
- `args`: Argument namespace from argparse
- `profile_name` (str): Profile name to load

**Returns:**
- `Dict`: Merged configuration

---

## Reporting API

**Module:** `src.reporting`

### ScanResult Dataclass

```python
@dataclass
class ScanResult:
    target: str
    port: int
    service: str
    version: Optional[str] = None
    status: str = "open"
```

**Properties:**
- `target` (str): Target IP/hostname
- `port` (int): Port number
- `service` (str): Service name (e.g., "SSH")
- `version` (Optional[str]): Service version
- `status` (str): Port status ("open" or "closed")

### CredentialResult Dataclass

```python
@dataclass
class CredentialResult:
    target: str
    username: str
    password: str
    protocol: str
    status: ResultStatus
```

**Properties:**
- `target` (str): Target IP/hostname
- `username` (str): Username
- `password` (str): Password
- `protocol` (str): Protocol used
- `status` (ResultStatus): Result status enum

### AttackSummary Dataclass

```python
@dataclass
class AttackSummary:
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

**Properties:**
- `attack_type` (str): "scan" or "bruteforce"
- `target` (str): Target IP/hostname
- `start_time` (str): ISO format start time
- `end_time` (str): ISO format end time
- `duration` (float): Attack duration in seconds
- `total_attempts` (int): Total attempts made
- `successful` (int): Successful attempts
- `failed` (int): Failed attempts
- `errors` (int): Errors encountered
- `success_rate` (float): Success percentage (0-100)

### ReportGenerator Class

```python
class ReportGenerator:
    """Multi-format report generator"""
```

#### Constructor

```python
def __init__(self, output_dir: Path = Path("output"))
```

**Parameters:**
- `output_dir` (Path, optional): Output directory. Default: "output"

#### Methods

##### add_scan_result()

```python
def add_scan_result(self, result: ScanResult)
```

**Purpose:** Add port scan result to report.

**Parameters:**
- `result` (ScanResult): Scan result object

##### add_credential_result()

```python
def add_credential_result(self, result: CredentialResult)
```

**Purpose:** Add credential discovery to report.

**Parameters:**
- `result` (CredentialResult): Credential result object

##### add_summary()

```python
def add_summary(self, summary: AttackSummary)
```

**Purpose:** Add attack summary to report.

**Parameters:**
- `summary` (AttackSummary): Attack summary object

##### generate_json_report()

```python
def generate_json_report(self, filename: str) -> str
```

**Purpose:** Generate JSON format report.

**Parameters:**
- `filename` (str): Output filename

**Returns:**
- `str`: Path to generated file

##### generate_csv_report()

```python
def generate_csv_report(self, filename: str) -> str
```

**Purpose:** Generate CSV format report.

**Parameters:**
- `filename` (str): Output filename

**Returns:**
- `str`: Path to generated file

**Note:** Skips generation if no results available

##### generate_html_report()

```python
def generate_html_report(self, filename: str) -> str
```

**Purpose:** Generate interactive HTML dashboard report.

**Parameters:**
- `filename` (str): Output filename

**Returns:**
- `str`: Path to generated file

**Features:**
- Real-time progress visualization
- Service summary charts
- Sortable port table
- Timeline statistics

##### generate_xml_report()

```python
def generate_xml_report(self, filename: str) -> str
```

**Purpose:** Generate XML format report.

**Parameters:**
- `filename` (str): Output filename

**Returns:**
- `str`: Path to generated file

##### export_all_formats()

```python
def export_all_formats(self, prefix: str) -> List[str]
```

**Purpose:** Export all report formats (JSON, CSV, HTML, XML).

**Parameters:**
- `prefix` (str): Filename prefix

**Returns:**
- `List[str]`: List of generated file paths

**Example:**
```python
from src.reporting import ReportGenerator, ScanResult

reporter = ReportGenerator()

# Add results
reporter.add_scan_result(ScanResult(
    target="192.168.1.1",
    port=22,
    service="SSH",
    version="OpenSSH 7.4"
))

# Export all formats
files = reporter.export_all_formats("scan_results")
# Returns: ["output/scan_results.json", "output/scan_results.html", ...]
```

---

## Utilities API

**Module:** `src.utils`

### Functions

#### is_valid_ip()

```python
def is_valid_ip(host: str) -> bool
```

**Purpose:** Validate IP address or hostname.

**Parameters:**
- `host` (str): IP address or hostname to validate

**Returns:**
- `bool`: `True` if valid, `False` otherwise

**Example:**
```python
from src.utils import is_valid_ip

assert is_valid_ip("192.168.1.1") == True
assert is_valid_ip("example.com") == True
assert is_valid_ip("invalid") == False
```

#### load_wordlist()

```python
def load_wordlist(filepath: str) -> List[str]
```

**Purpose:** Load words from file (one per line).

**Parameters:**
- `filepath` (str): Path to wordlist file

**Returns:**
- `List[str]`: List of words (stripped of whitespace)

**Example:**
```python
from src.utils import load_wordlist

passwords = load_wordlist("wordlists/passwords.txt")
print(f"Loaded {len(passwords)} passwords")
```

#### save_results()

```python
def save_results(results: List[Dict], output_file: str,
                 format: str = "json") -> bool
```

**Purpose:** Save results to file.

**Parameters:**
- `results` (List[Dict]): Results to save
- `output_file` (str): Output filename
- `format` (str, optional): Output format ("json" or "csv"). Default: "json"

**Returns:**
- `bool`: `True` if successful, `False` if error

**Example:**
```python
from src.utils import save_results

results = [
    {"port": 22, "service": "SSH"},
    {"port": 80, "service": "HTTP"}
]

save_results(results, "output/report.json", format="json")
```

#### print_banner()

```python
def print_banner()
```

**Purpose:** Print application banner to stdout.

**Example:**
```python
from src.utils import print_banner

print_banner()
# Output:
# ╔═══════════════════════════════════════════════════════════════╗
# ║         Advanced Penetration Testing Toolkit v2.1             ║
# ║           Professional Security Assessment Tool              ║
# ╚═══════════════════════════════════════════════════════════════╝
```

#### parse_target_list()

```python
def parse_target_list(target_spec: str) -> List[str]
```

**Purpose:** Parse target specification (file or single target).

**Parameters:**
- `target_spec` (str): Single IP/hostname or path to file

**Returns:**
- `List[str]`: List of targets

**Example:**
```python
from src.utils import parse_target_list

# Single target
targets = parse_target_list("192.168.1.1")
# Returns: ["192.168.1.1"]

# From file
targets = parse_target_list("targets.txt")
# Returns: [list of IPs from file]
```

### Logger Class

```python
class Logger:
    """Simple logging utility"""
```

#### Constructor

```python
def __init__(self, verbose: bool = False)
```

**Parameters:**
- `verbose` (bool, optional): Enable verbose output. Default: False

---

## Exceptions & Logging API

**Module:** `src.exceptions`

### EnterpriseLogger Class

```python
class EnterpriseLogger:
    """Enterprise-grade logging with audit trail"""
```

#### Constructor

```python
def __init__(self, log_file: str = "logs/appt.log")
```

**Parameters:**
- `log_file` (str, optional): Log file path. Default: "logs/appt.log"

#### Methods

##### info()

```python
def info(self, message: str, metadata: Dict = None)
```

**Purpose:** Log information message.

**Parameters:**
- `message` (str): Log message
- `metadata` (Dict, optional): Additional metadata to log

##### warning()

```python
def warning(self, message: str)
```

**Purpose:** Log warning message.

**Parameters:**
- `message` (str): Warning message

##### error()

```python
def error(self, message: str, error: Exception = None)
```

**Purpose:** Log error message.

**Parameters:**
- `message` (str): Error message
- `error` (Exception, optional): Exception object

##### audit()

```python
def audit(self, action: str, target: str, result: str)
```

**Purpose:** Log security-relevant action.

**Parameters:**
- `action` (str): Action performed (e.g., "attack", "scan")
- `target` (str): Target of action
- `result` (str): Result of action ("success", "failure", "error")

**Example:**
```python
from src.exceptions import EnterpriseLogger

logger = EnterpriseLogger()

logger.info("Scan started")
logger.warning("Connection timeout")
logger.error("Authentication failed", exception)
logger.audit("scan", "192.168.1.1", "success")
```

### Retry Decorator

```python
@retry(max_attempts: int = 3, backoff: BackoffStrategy = ExponentialBackoff())
def function():
    # Automatically retried on failure
```

**Purpose:** Automatically retry function on failure with exponential backoff.

**Parameters:**
- `max_attempts` (int, optional): Maximum retry attempts. Default: 3
- `backoff` (BackoffStrategy, optional): Backoff strategy. Default: ExponentialBackoff

**Example:**
```python
from src.exceptions import retry, ExponentialBackoff

@retry(max_attempts=5)
def unreliable_operation():
    # Will retry up to 5 times with exponential backoff
    result = some_network_call()
    return result
```

---

## Summary Table

| Module | Key Classes | Main Functions |
|--------|------------|-----------------|
| port_scanner | PortScanner | scan() |
| brute_forcer | BruteForcer, AttackMode, Credential | attack() |
| config_manager | ConfigManager | get_profile() |
| reporting | ReportGenerator, ScanResult, CredentialResult | export_all_formats() |
| utils | Logger | is_valid_ip(), load_wordlist(), save_results() |
| exceptions | EnterpriseLogger, retry | @retry decorator |

---

For usage examples and command reference, see [USER_MANUAL.md](USER_MANUAL.md)

For detailed code implementation, see [CODE_WALKTHROUGH.md](CODE_WALKTHROUGH.md)
