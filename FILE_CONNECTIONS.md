# APPT - File Structure & Module Connections

**Complete Overview of Project Architecture and File Dependencies**

---

## Project Directory Tree

```
PENETRATION-TESTING-TOOLKIT/
│
├── 📄 README.md                    # GitHub project overview
├── 📄 USER_MANUAL.md              # Complete usage guide (NEW)
├── 📄 CODE_WALKTHROUGH.md         # Line-by-line code explanation (NEW)
├── 📄 FILE_CONNECTIONS.md         # This file - architecture overview
│
├── 📄 appt                         # Main CLI entry point (executable)
│
├── 🔧 requirements.txt             # Python dependencies
├── 🐳 Dockerfile                   # Container configuration
├── 🐳 docker-compose.yml           # Multi-container orchestration
│
├── 📁 src/                         # Core application modules
│   ├── __init__.py                 # Package initialization
│   ├── port_scanner.py            # Port scanning module
│   ├── brute_forcer.py            # Brute force attack module
│   ├── config_manager.py          # Configuration management
│   ├── reporting.py               # Report generation
│   ├── exceptions.py              # Logging & error handling
│   └── utils.py                   # Utility functions
│
├── 📁 config/                      # Configuration files
│   ├── default.conf               # Default settings
│   └── example_profiles.yaml      # Attack profiles
│
├── 📁 wordlists/                   # Credential dictionaries
│   ├── passwords.txt              # 29,946 passwords
│   └── usernames.txt              # Common usernames
│
├── 📁 docs/                        # Extended documentation
│   ├── ARCHITECTURE.md            # System design
│   ├── DEPLOYMENT.md              # Deployment guide
│   └── API_REFERENCE.md           # API documentation (NEW)
│
├── 📁 output/                      # Reports and results
│   ├── scan_*.json
│   ├── scan_*.csv
│   ├── scan_*.html
│   └── scan_*.xml
│
├── 📁 logs/                        # Application logs
│   └── appt.log
│
├── 📁 examples/                    # Example code
│   ├── basic_scan.py
│   ├── basic_attack.py
│   └── custom_reporting.py
│
└── 📄 .gitignore                   # Git ignore rules

```

---

## Module Dependency Graph

### High-Level Dependencies

```
┌─────────────────────────────────────────────────────┐
│                    appt (CLI)                       │
│              Command-line interface                 │
└────────┬────────────────────┬──────────────┬────────┘
         │                    │              │
         ▼                    ▼              ▼
    ┌─────────┐      ┌──────────────┐  ┌────────────┐
    │ utils.py│      │ port_scanner │  │ brute_forcer│
    └─────────┘      └──────────────┘  └────────────┘
         │                    │              │
         └────────┬───────────┘──────────────┘
                  │
                  ▼
          ┌──────────────────┐
          │ reporting.py     │
          │ Report Generator │
          └──────────────────┘
                  │
                  ▼
         ┌───────────────────┐
         │ Output Files      │
         │ .json .csv .html  │
         └───────────────────┘

Optional Dependencies:
    ├── paramiko (SSH support)
    ├── requests (HTTP support)
    └── pyyaml (Config parsing)
```

---

## File Connections Detail

### 1. **appt** - CLI Entry Point

**Type:** Executable Python script  
**Lines:** 227  
**Purpose:** Command-line interface, argument parsing, command routing

**Imports:**
```python
from port_scanner import scan as scan_ports
from brute_forcer import attack
from utils import (
    is_valid_ip, load_wordlist, save_results,
    print_banner, Logger, parse_target_list
)
from config_manager import ConfigManager  # Optional
from reporting import ReportGenerator  # Optional
```

**Key Functions:**
- `create_parser()` - Creates argument parser with subcommands
- `main()` - Routes to scan/brute based on command
- Calls `scan_ports()` for `appt scan` command
- Calls `attack()` for `appt brute` command

**Execution Flow:**
```
User runs: appt scan 192.168.1.1
    ↓
appt parses args
    ↓
main() called
    ↓
args.command == "scan"
    ↓
scan_ports() called with parsed args
    ↓
Results returned
    ↓
save_results() called if --output specified
```

---

### 2. **src/port_scanner.py** - Port Scanning

**Type:** Module  
**Lines:** 231  
**Exports:** `PortScanner` class, `scan()` function, `SERVICE_FINGERPRINTS`, `COMMON_PORTS`

**Imports:**
```python
import socket          # TCP connections
import json           # Report format
from threading import Thread, Lock
from queue import Queue, Empty
from time import time
```

**Classes:**
- `PortScanner` - Multi-threaded scanner
  - `scan_port(port)` - Scan individual port
  - `_fingerprint_service(port)` - Identify service
  - `worker(queue)` - Worker thread
  - `parse_port_spec()` - Parse port ranges
  - `scan(ports, num_threads)` - Execute scan

**Usage from appt:**
```python
from port_scanner import scan as scan_ports

results = scan_ports(
    host="192.168.1.1",
    port_spec="1-1000",
    timeout=2.0,
    num_threads=20,
    quick=True
)
```

**Data Structures:**
```python
open_ports = [
    {
        "port": 22,
        "service": "SSH",
        "version": "OpenSSH 7.4",
        "state": "open"
    },
    ...
]
```

---

### 3. **src/brute_forcer.py** - Brute Force Attacks

**Type:** Module  
**Lines:** 345  
**Exports:** `BruteForcer` class, `attack()` function, `AttackMode`, `Credential`, `RateLimiter`

**Imports:**
```python
import ftplib                    # FTP protocol
import paramiko                  # SSH protocol (optional)
import requests                  # HTTP protocol (optional)
from threading import Thread, Lock, Event
from queue import Queue, Empty
from dataclasses import dataclass
from enum import Enum
```

**Classes:**
- `AttackMode` (Enum) - Attack strategies
  - `SINGLE` - One password per user
  - `LOOP` - All passwords per user
  - `COMBO` - Paired credentials
- `Credential` (Dataclass) - Username:password pair
- `RateLimiter` - Rate limiting for stealth
- `BruteForcer` - Multi-threaded brute forcer
  - `_attempt_ftp()` - FTP login
  - `_attempt_ssh()` - SSH login
  - `_attempt_http()` - HTTP auth
  - `_attempt_telnet()` - Telnet login
  - `attempt_login()` - Protocol dispatcher
  - `worker(queue)` - Worker thread
  - `attack()` - Execute attack
  - `_generate_credentials()` - Generate credential pairs

**Usage from appt:**
```python
from brute_forcer import attack

results = attack(
    host="192.168.1.1",
    usernames=["admin"],
    passwords=["pass1", "pass2"],
    protocol="ssh",
    num_threads=10,
    attack_mode="loop"
)
```

**Data Structures:**
```python
found_credentials = [
    Credential(username="admin", password="password123"),
    ...
]
```

---

### 4. **src/utils.py** - Utility Functions

**Type:** Module  
**Lines:** 142  
**Exports:** Functions and `Logger` class

**Functions:**
- `is_valid_ip(host)` - Validate IP/hostname
- `load_wordlist(filepath)` - Read word list file
- `save_results()` - Save to JSON/CSV
- `print_banner()` - Print application banner
- `parse_target_list()` - Parse targets from file
- `Logger` class - Logging utility

**Used By:**
- `appt` - Multiple functions
- `port_scanner.py` - Validation
- `brute_forcer.py` - Validation

**Key Logic:**
```python
# Load passwords file
passwords = load_wordlist("wordlists/passwords.txt")
# Returns: ["password123", "admin123", ...]

# Save results
save_results(results, "output/report.json", format="json")

# Validate target
if is_valid_ip("192.168.1.1"):
    scan(target)
```

---

### 5. **src/config_manager.py** - Configuration Management

**Type:** Module  
**Lines:** ~450  
**Exports:** `ConfigManager` class, configuration dataclasses

**Classes:**
- `ConfigManager` - Manages configuration and profiles
  - `load_config()` - Load INI settings
  - `load_profiles()` - Load YAML profiles
  - `get_profile(name)` - Get specific profile
  - `merge_args_with_profile()` - Merge CLI args with profile

**Profile Format (YAML):**
```yaml
quick_scan:
  description: "Scan common ports"
  scanner:
    timeout: 2.0
    threads: 50
    ports: "1-10000"

ssh_bruteforce:
  description: "SSH brute force"
  bruteforcer:
    protocol: ssh
    port: 22
    attack_mode: loop
    delay: 0.5
    threads: 20
```

**Usage:**
```python
from config_manager import ConfigManager

config = ConfigManager()
profile = config.get_profile("quick_scan")
# Returns: {"timeout": 2.0, "threads": 50, ...}
```

---

### 6. **src/reporting.py** - Report Generation

**Type:** Module  
**Lines:** ~400  
**Exports:** `ReportGenerator`, `ScanResult`, `CredentialResult`, `AttackSummary`

**Classes:**
- `ReportGenerator` - Main report generator
  - `add_scan_result()` - Add port scan result
  - `add_credential_result()` - Add credential
  - `generate_json_report()` - JSON output
  - `generate_csv_report()` - CSV output
  - `generate_html_report()` - HTML dashboard
  - `generate_xml_report()` - XML output
  - `export_all_formats()` - Export all formats

- Data Classes:
  - `ScanResult` - Port scan information
  - `CredentialResult` - Found credentials
  - `AttackSummary` - Attack statistics
  - `ResultStatus` - Enum for result status

**Usage:**
```python
from reporting import ReportGenerator, ScanResult

reporter = ReportGenerator()

# Add results
reporter.add_scan_result(ScanResult(
    target="192.168.1.1",
    port=22,
    service="SSH"
))

# Generate reports
reporter.generate_json_report("report.json")
reporter.generate_html_report("report.html")

# Export all formats
files = reporter.export_all_formats("scan_results")
```

**Bug Fixes Applied:**
1. ✅ Zero division error in HTML generation (safe success_rate calculation)
2. ✅ CSV export error handling (skip gracefully if no results)
3. ✅ Improved error messages (context and emojis)

---

### 7. **src/exceptions.py** - Logging & Error Handling

**Type:** Module  
**Lines:** ~400  
**Exports:** `EnterpriseLogger`, retry decorators, custom exceptions

**Classes:**
- `EnterpriseLogger` - Advanced logging
  - `info()` - Log info message
  - `warning()` - Log warning
  - `error()` - Log error
  - `audit()` - Log security event
- `RetryConfig` - Retry configuration
- Retry decorators - `@retry` decorator

**Features:**
- Colored output
- Log rotation
- Audit trail
- Structured logging
- Exception tracking

**Usage:**
```python
from exceptions import EnterpriseLogger, retry

logger = EnterpriseLogger()
logger.info("Scan started")
logger.audit("attack", "192.168.1.1", "success")

@retry(max_attempts=3)
def unreliable_operation():
    # Automatically retried on failure
    pass
```

---

## Data Flow Diagrams

### Complete Scan Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                │
│  $ appt scan 192.168.1.1 --quick -o report.json             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────┐
    │              appt script                │
    │                                        │
    │ 1. create_parser()                     │
    │    Parse: target=192.168.1.1          │
    │            quick=True                  │
    │            output=report.json         │
    │                                        │
    │ 2. main()                              │
    │    Route to scan command               │
    │                                        │
    │ 3. Call scan_ports()                   │
    └────────────┬─────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │      port_scanner.scan()               │
    │                                        │
    │ 1. Create PortScanner instance         │
    │    host="192.168.1.1"                 │
    │    timeout=2.0                        │
    │                                        │
    │ 2. Determine ports                     │
    │    quick=True → COMMON_PORTS          │
    │    [21,22,25,53,80,...]               │
    │                                        │
    │ 3. Create 20 worker threads            │
    │                                        │
    │ 4. Queue all ports                     │
    │    Queue: [21, 22, 25, 53, ...]       │
    │                                        │
    │ 5. Workers process queue               │
    │    Each thread:                       │
    │    - Get port from queue               │
    │    - Create socket                     │
    │    - Attempt connect (timeout=2s)     │
    │    - If open: add to open_ports       │
    │    - Fingerprint service              │
    │    - Print: "🟢 22/tcp SSH..."        │
    │                                        │
    │ 6. Return results                      │
    │    [{port:22, service:SSH},            │
    │     {port:80, service:HTTP}, ...]     │
    └────────────┬─────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │      appt save_results()                │
    │      output=report.json                │
    │                                        │
    │ 1. Create output directory             │
    │    mkdir -p output/                    │
    │                                        │
    │ 2. Serialize results to JSON           │
    │    json.dump(results, ...)             │
    │                                        │
    │ 3. Write to file                       │
    │    output/report.json                  │
    └────────────┬─────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │         File System                    │
    │   output/report.json                   │
    │                                        │
    │   {                                    │
    │     "host": "192.168.1.1",             │
    │     "ports": [                         │
    │       {                                │
    │         "port": 22,                    │
    │         "service": "SSH",              │
    │         "version": "OpenSSH 7.4"      │
    │       },                               │
    │       ...                              │
    │     ]                                  │
    │   }                                    │
    └────────────────────────────────────────┘
```

### Complete Brute Force Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                        USER                                  │
│  $ appt brute 192.168.1.100 -u admin -w wordlists/pass.txt  │
│     --protocol ssh -o report.json                            │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────┐
    │           appt script                    │
    │                                          │
    │ 1. Parse args                            │
    │    target=192.168.1.100                 │
    │    username=admin                       │
    │    wordlist=wordlists/passwords.txt    │
    │    protocol=ssh                         │
    │    output=report.json                   │
    │                                          │
    │ 2. Call load_wordlist()                  │
    │    Load passwords from file              │
    │ 3. Call attack()                         │
    └──────────────┬───────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────┐
    │       brute_forcer.attack()              │
    │                                          │
    │ 1. Create BruteForcer instance           │
    │    host=192.168.1.100                   │
    │    protocol=ssh                         │
    │    port=22 (auto-detected)              │
    │                                          │
    │ 2. Generate credentials                 │
    │    usernames: [admin]                   │
    │    passwords: [pass1, pass2, ...]      │
    │    mode: loop                           │
    │    Result: [                            │
    │      Credential(admin, pass1),          │
    │      Credential(admin, pass2),          │
    │      ...                                │
    │    ]                                    │
    │                                          │
    │ 3. Create 10 worker threads              │
    │                                          │
    │ 4. Queue all credentials                │
    │    Queue: [Cred(admin,pass1), ...]     │
    │                                          │
    │ 5. Workers process queue                │
    │    Each thread:                        │
    │    - Get credential from queue           │
    │    - Apply rate limit (delay=0.1s)     │
    │    - Call attempt_login(admin, pass1)  │
    │      └─ Routes to _attempt_ssh()       │
    │        └─ ssh.connect(host, port,      │
    │             user, password)             │
    │    - If result==True:                   │
    │      └─ Print "🟢 ✓ SUCCESS!"          │
    │      └─ Add to found_credentials       │
    │    - If result==False:                  │
    │      └─ Try next credential             │
    │    - If result==None:                   │
    │      └─ Error (retry or skip)          │
    │                                          │
    │ 6. Return found credentials             │
    │    [Credential(admin, password123), ...]│
    └──────────────┬───────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────┐
    │    appt save_results()                   │
    │    output=report.json                   │
    │                                          │
    │ 1. Convert Credential objects to dict   │
    │ 2. json.dump() to file                  │
    │ 3. Write output/report.json             │
    └──────────────┬───────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────┐
    │        File System                       │
    │    output/report.json                   │
    │                                          │
    │    [                                    │
    │      {                                  │
    │        "username": "admin",             │
    │        "password": "password123",       │
    │        "protocol": "ssh"                │
    │      }                                  │
    │    ]                                    │
    └──────────────────────────────────────────┘
```

---

## Module Interaction Matrix

| Module | Calls | Called By | Data Exchange |
|--------|-------|-----------|----------------|
| **appt** | port_scanner, brute_forcer, utils, reporting | User | Arguments → Results → File |
| **port_scanner** | utils, socket, threading | appt, reporting | Hosts, ports → ScanResult[] |
| **brute_forcer** | utils, ftplib/paramiko/requests | appt, reporting | Hosts, creds → Credential[] |
| **utils** | pathlib, json, csv | All modules | File I/O, validation |
| **config_manager** | yaml, pathlib | appt | Profile name → Config dict |
| **reporting** | json, csv, dataclasses | appt | Results → Reports |
| **exceptions** | logging, threading | All modules | Exceptions → Logs |

---

## Important File Relationships

### Configuration Files

**config/default.conf** (INI format)
```ini
[scanner]
timeout = 2.0
threads = 20

[bruteforcer]
delay = 0.1
timeout = 5.0
```

**config/example_profiles.yaml** (YAML format)
```yaml
quick_scan:
  scanner:
    timeout: 2.0
    threads: 50
    ports: "1-10000"
```

### Wordlists

**wordlists/passwords.txt** (29,946 passwords)
- Used by: `appt brute`, BruteForcer class
- Format: One password per line
- Categories: Numeric, years, phrases, doubles, special chars

**wordlists/usernames.txt** (50+ usernames)
- Used by: `appt brute` with `-U` flag
- Format: One username per line
- Examples: admin, root, user, test, etc.

### Output Files

Generated automatically in `output/` directory:
- `scan_*.json` - JSON format scan results
- `scan_*.csv` - CSV format scan results
- `scan_*.html` - Interactive HTML report
- `scan_*.xml` - XML format results

### Logging

**logs/appt.log**
- Generated by: EnterpriseLogger
- Contains: All operations, errors, warnings
- Used for: Debugging, audit trail, compliance

---

## Extension Points

### Adding New Protocols

To add new brute force protocol:

1. Add method to `BruteForcer` class:
   ```python
   def _attempt_ldap(self, username: str, password: str) -> bool:
       # Implementation
   ```

2. Update `attempt_login()` dispatcher:
   ```python
   elif self.protocol == "ldap":
       return self._attempt_ldap(username, password)
   ```

3. Update `_set_default_port()`:
   ```python
   "ldap": 389,
   ```

4. Update CLI parser in `appt`:
   ```python
   --protocol", choices=["ftp", "ssh", ..., "ldap"]
   ```

### Adding New Report Format

To add new output format:

1. Add method to `ReportGenerator`:
   ```python
   def generate_yaml_report(self, filename: str):
       # Implementation
   ```

2. Update `export_all_formats()`:
   ```python
   files.append(self.generate_yaml_report(f"{prefix}.yaml"))
   ```

---

## Summary

**APPT uses a modular architecture with clear separation of concerns:**

- **CLI Layer** (`appt`) - User interface and argument parsing
- **Scanner Layer** (`port_scanner.py`) - Network discovery
- **Attack Layer** (`brute_forcer.py`) - Credential testing
- **Utility Layer** (`utils.py`) - Common functions
- **Configuration Layer** (`config_manager.py`) - Settings management
- **Reporting Layer** (`reporting.py`) - Output generation
- **Infrastructure** (`exceptions.py`) - Logging and error handling

**Data flows:** Arguments → Scanner/Attacker → Results → Reporter → Files

**Each module can be used independently or combined for integrated testing.**

See [USER_MANUAL.md](USER_MANUAL.md) for usage examples and [CODE_WALKTHROUGH.md](CODE_WALKTHROUGH.md) for implementation details.
