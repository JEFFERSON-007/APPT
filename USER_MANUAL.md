# Advanced Penetration Testing Toolkit (APPT) - User Manual

**Version:** 2.0 (Enterprise Edition)  
**Last Updated:** January 2026  
**Author:** Cybersecurity Engineering Team

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Installation by Platform](#installation-by-platform)
3. [Quick Start Guide](#quick-start-guide)
4. [Port Scanner Usage](#port-scanner-usage)
5. [Brute Forcer Usage](#brute-forcer-usage)
6. [Advanced Features](#advanced-features)
7. [Configuration Profiles](#configuration-profiles)
8. [Reporting and Output](#reporting-and-output)
9. [Troubleshooting](#troubleshooting)
10. [Security Best Practices](#security-best-practices)

---

## Getting Started

### What is APPT?

Advanced Penetration Testing Toolkit (APPT) is a professional security assessment framework inspired by industry-standard tools like Hydra. It provides:

- **Multi-threaded port scanning** with service detection
- **Advanced brute force attacks** with multiple protocols
- **Real-time feedback** and progress tracking
- **Professional reporting** (JSON, CSV, HTML, XML)
- **Enterprise-grade logging** and configuration management
- **Docker support** for containerized deployment

### System Requirements

- **Python:** 3.7 or higher
- **OS:** Linux, Windows (with WSL2), or macOS
- **RAM:** Minimum 512MB (recommended 2GB+)
- **Network:** Direct access to target systems
- **Permissions:** Root/Administrator access for socket operations

### Supported Platforms

| Platform | Support | Notes |
|----------|---------|-------|
| **Linux** | ✅ Full | Tested on Ubuntu 20.04+, CentOS, Debian |
| **macOS** | ✅ Full | Tested on macOS 10.15+ |
| **Windows (WSL2)** | ✅ Full | Requires Windows Subsystem for Linux 2 |
| **Windows (Native)** | ⚠️ Limited | Some features may require modifications |
| **Docker** | ✅ Full | Docker Compose included |

---

## Installation by Platform

### Linux / macOS Installation

#### Step 1: Install Python

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# macOS (with Homebrew)
brew install python3

# Verify installation
python3 --version  # Should show 3.7 or higher
```

#### Step 2: Clone Repository

```bash
cd ~/Documents
git clone https://github.com/yourusername/penetration-testing-toolkit.git
cd penetration-testing-toolkit
```

#### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
```

#### Step 4: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python3 -c "import sys; print('✅ Python OK'); import paramiko; print('✅ Paramiko OK')"
```

#### Step 5: Make Executable

```bash
chmod +x appt

# Verify executable
./appt --help
```

#### Step 6: Add to PATH (Optional)

```bash
# Copy to system path for global access
sudo cp appt /usr/local/bin/appt
sudo chmod +x /usr/local/bin/appt

# Now you can run from anywhere
appt --help
```

---

### Windows Installation (WSL2)

#### Step 1: Enable WSL2

```powershell
# Run PowerShell as Administrator
wsl --install

# Restart computer
Restart-Computer
```

#### Step 2: Install Ubuntu

```powershell
# Download Ubuntu from Microsoft Store, or:
wsl --install -d Ubuntu-22.04
```

#### Step 3: Open WSL2 Terminal

```bash
# All Linux commands apply here
python3 --version
```

#### Step 4: Follow Linux Installation Steps

```bash
# Inside WSL2 terminal:
sudo apt-get update
sudo apt-get install python3 python3-pip git
cd ~/Documents
git clone https://github.com/yourusername/penetration-testing-toolkit.git
cd penetration-testing-toolkit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x appt
./appt --help
```

---

### Windows Installation (Native Python)

#### Step 1: Install Python

Download from https://www.python.org/downloads/ (3.7+)

Check "Add Python to PATH" during installation

#### Step 2: Open Command Prompt

```cmd
# Verify Python
python --version

# Verify pip
pip --version
```

#### Step 3: Clone Repository

```cmd
cd %USERPROFILE%\Documents
git clone https://github.com/yourusername/penetration-testing-toolkit.git
cd penetration-testing-toolkit
```

#### Step 4: Install Dependencies

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 5: Run APPT

```cmd
python appt --help

# Or create batch file (appt.bat):
@echo off
python "%~dp0appt" %*
```

---

### Docker Installation

#### Prerequisites

- Docker Desktop or Docker Engine installed
- Docker Compose (included with Desktop)

#### Setup

```bash
# Build Docker image
docker-compose build

# Verify
docker-compose images

# Run container
docker-compose up -d

# Access container
docker exec -it appt-container bash
```

#### Using APPT in Docker

```bash
# Scan from container
docker exec -it appt-container ./appt scan 192.168.1.1

# Mount local wordlists
docker-compose exec appt ./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt

# View results
docker exec appt cat output/report.json
```

---

## Quick Start Guide

### Basic Port Scanning

```bash
# Scan default ports (1-1000)
./appt scan 192.168.1.1

# Quick scan (common ports only)
./appt scan 192.168.1.1 --quick

# Scan with custom range
./appt scan 192.168.1.1 -p 1-10000

# Specific ports
./appt scan 192.168.1.1 -p 22,80,443,3306

# With custom timeout
./appt scan 192.168.1.1 --timeout 5

# JSON output
./appt scan 192.168.1.1 --json -o results.json

# Verbose mode
./appt scan 192.168.1.1 -v

# Multiple threads
./appt scan 192.168.1.1 -t 100
```

### Basic Brute Forcing

```bash
# FTP brute force (default)
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt

# SSH brute force
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --protocol ssh

# HTTP brute force
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --protocol http --port 80

# Multiple usernames
./appt brute 192.168.1.100 -U wordlists/usernames.txt -w wordlists/passwords.txt

# Stop on first success
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --stop-on-success

# With custom delay
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --delay 1.0

# Combo mode (username:password pairs)
./appt brute 192.168.1.100 --attack-mode combo -w combo.txt

# Verbose output
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt -v
```

---

## Port Scanner Usage

### Syntax

```bash
./appt scan <target> [OPTIONS]
```

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--ports` | `-p` | string | `1-1000` | Port range: `1-1000`, `1-65535`, or list `80,443,22` |
| `--quick` | `-q` | flag | - | Scan only common ports (fast) |
| `--timeout` | `-T` | float | `2` | Connection timeout in seconds |
| `--threads` | `-t` | int | `20` | Number of threads (higher = faster) |
| `--verbose` | `-v` | flag | - | Detailed output |
| `--json` | - | flag | - | JSON format output |
| `--output` | `-o` | file | - | Save results to file |

### Examples

```bash
# Complete network scan
./appt scan 192.168.1.0/24

# Scan with aggressive threading
./appt scan 192.168.1.1 -t 200 --timeout 1

# Scan all ports
./appt scan 192.168.1.1 -p 1-65535 --quick

# Scan from file (one IP per line)
./appt scan targets.txt -q

# Save to JSON
./appt scan 192.168.1.1 --json -o scan_results.json

# Combine with brute force workflow
./appt scan 192.168.1.1 -q -o open_ports.json
# Then brute force the services found
```

### Understanding Output

```
🟢 22   /tcp  SSH             OpenSSH 7.4
🟢 80   /tcp  HTTP            Apache/2.4.6
🟢 443  /tcp  HTTPS           nginx/1.14.0
🟢 3306 /tcp  MySQL           MySQL 5.7.31-0
```

- 🟢 = Open port (service detected)
- 🔴 = Closed port
- ⏱️ = Timeout
- ❌ = Error

---

## Brute Forcer Usage

### Syntax

```bash
./appt brute <target> [OPTIONS]
```

### Core Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--username` | `-u` | string | - | Single username |
| `--userlist` | `-U` | file | - | Wordlist of usernames |
| `--wordlist` | `-w` | file | `wordlists/passwords.txt` | Password wordlist |
| `--protocol` | - | enum | `ftp` | Protocol: ftp, ssh, http, https, telnet, mysql, postgres |
| `--port` | `-p` | int | - | Port number (auto-detected if not provided) |
| `--attack-mode` | - | enum | `loop` | Attack mode: single, loop, combo |
| `--delay` | - | float | `0.1` | Delay between attempts (seconds) |
| `--threads` | `-t` | int | `20` | Concurrent threads |
| `--timeout` | `-T` | float | `5` | Connection timeout |
| `--stop-on-success` | - | flag | - | Stop after first successful credential |
| `--verbose` | `-v` | flag | - | Detailed output |
| `--output` | `-o` | file | - | Save results to file |

### Supported Protocols

#### FTP
```bash
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --protocol ftp
# Default port: 21
```

#### SSH
```bash
./appt brute 192.168.1.100 -u root -w wordlists/passwords.txt --protocol ssh
# Default port: 22
```

#### HTTP/HTTPS
```bash
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --protocol http --port 8080
# Default ports: 80 (HTTP), 443 (HTTPS)
```

#### MySQL/PostgreSQL
```bash
./appt brute 192.168.1.100 -u root -w wordlists/passwords.txt --protocol mysql
# Default MySQL port: 3306
```

#### Telnet
```bash
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --protocol telnet
# Default port: 23
```

### Attack Modes

#### SINGLE Mode
One password per user (password tested against all users, then move to next password)

```bash
./appt brute 192.168.1.100 -U wordlists/usernames.txt -w wordlists/passwords.txt --attack-mode single
```

**Process:**
```
Try password1 with user1
Try password1 with user2
Try password1 with user3
Try password2 with user1
Try password2 with user2
...
```

#### LOOP Mode (Default)
All passwords for each user (user1 tries all passwords, then user2)

```bash
./appt brute 192.168.1.100 -U wordlists/usernames.txt -w wordlists/passwords.txt --attack-mode loop
```

**Process:**
```
Try user1:password1
Try user1:password2
Try user1:password3
Try user2:password1
Try user2:password2
...
```

#### COMBO Mode
Use pre-paired user:password combinations

```bash
# First create combo.txt with format: user1:pass1
#                                      user2:pass2
./appt brute 192.168.1.100 --attack-mode combo -w combo.txt
```

---

## Advanced Features

### Batch Processing

Attack multiple targets in one command:

```bash
# Create targets.txt (one IP per line)
cat > targets.txt << EOF
192.168.1.1
192.168.1.2
192.168.1.100
EOF

# Scan all targets
./appt scan targets.txt -q --threads 100

# Brute force all targets
./appt brute targets.txt -u admin -w wordlists/passwords.txt --protocol ssh
```

### Configuration Profiles

Store attack parameters in YAML profiles:

```bash
# Use predefined profile
./appt brute 192.168.1.100 --profile stealth_mode

# List available profiles
./appt --list-profiles

# Create custom profile
cat > config/my_profile.yaml << EOF
protocol: ssh
port: 22
delay: 2.0
threads: 5
timeout: 10
rate_limit: 1.0
EOF
```

### Rate Limiting

Avoid detection with configurable delays:

```bash
# 1 second delay between attempts
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --delay 1.0

# Burst mode (fast but risky)
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --delay 0.01

# Stealth mode (slow and careful)
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --delay 5.0
```

### Output Formats

```bash
# JSON (recommended for automation)
./appt scan 192.168.1.1 --json -o results.json

# CSV (spreadsheet friendly)
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt -o results.csv

# HTML (interactive reports)
./appt scan 192.168.1.1 --html -o report.html

# Text (human readable)
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt -o results.txt
```

---

## Configuration Profiles

### Using Enterprise Profiles

Located in `config/example_profiles.yaml`

```bash
# Quick scan (common ports)
./appt scan 192.168.1.1 --profile quick_scan

# Thorough scan (all ports, slower)
./appt scan 192.168.1.1 --profile thorough_scan

# SSH brute force
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt --profile ssh_bruteforce

# Stealth mode (slow, careful, detection avoidance)
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt --profile stealth_mode

# Web application attack
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt --profile web_bruteforce
```

### Creating Custom Profiles

```yaml
# config/custom_profile.yaml
name: "Custom Attack Profile"
description: "Optimized for specific environment"

scanner:
  timeout: 3.0
  threads: 50
  ports: "1-10000"

bruteforcer:
  protocol: ssh
  port: 22
  attack_mode: loop
  delay: 0.5
  threads: 20
  timeout: 5.0
  rate_limit: true

reporting:
  format: json
  output_dir: output/
  include_summary: true
```

---

## Reporting and Output

### Report Generation

Automatic report generation after scans/attacks:

```bash
# Scan with all report formats
./appt scan 192.168.1.1 --output-all

# Results in:
# - output/scan_192.168.1.1.json
# - output/scan_192.168.1.1.csv
# - output/scan_192.168.1.1.html
# - output/scan_192.168.1.1.xml
```

### Report Formats

#### JSON
```json
{
  "scan_summary": {
    "target": "192.168.1.1",
    "start_time": "2026-01-15T10:00:00",
    "end_time": "2026-01-15T10:05:00",
    "duration": 300.0,
    "open_ports": 4,
    "closed_ports": 996,
    "success_rate": 0.4
  },
  "open_ports": [
    {
      "port": 22,
      "service": "SSH",
      "version": "OpenSSH 7.4",
      "state": "open"
    }
  ]
}
```

#### CSV
```
port,service,version,state
22,SSH,OpenSSH 7.4,open
80,HTTP,Apache/2.4.6,open
443,HTTPS,nginx/1.14.0,open
```

#### HTML
Interactive dashboard with:
- Real-time progress visualization
- Service summary charts
- Detailed port listings
- Timeline statistics

#### XML
Structured output for log aggregation:
```xml
<scan_report>
  <metadata>
    <target>192.168.1.1</target>
    <timestamp>2026-01-15T10:00:00</timestamp>
  </metadata>
  <results>
    <port>
      <number>22</number>
      <service>SSH</service>
    </port>
  </results>
</scan_report>
```

---

## Troubleshooting

### Connection Issues

#### "Connection refused" Error
```bash
# Check if target is reachable
ping 192.168.1.1

# Check if port is open
telnet 192.168.1.1 22

# Increase timeout
./appt scan 192.168.1.1 --timeout 5
```

#### "Permission denied" Error
```bash
# Required for raw sockets on Linux
sudo ./appt scan 192.168.1.1

# Or run entire command with sudo
sudo -E ./appt scan 192.168.1.1
```

### Performance Issues

#### Slow Scanning
```bash
# Increase threads
./appt scan 192.168.1.1 -t 200

# Reduce timeout
./appt scan 192.168.1.1 --timeout 1

# Use quick mode
./appt scan 192.168.1.1 --quick
```

#### Memory Issues
```bash
# Reduce threads
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt -t 5

# Process in batches
./appt scan targets.txt -q -t 20 < first_100_targets.txt
```

### Module Import Errors

#### "No module named 'paramiko'"
```bash
# Install missing dependency
pip install paramiko

# Or install all requirements
pip install -r requirements.txt
```

#### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Wordlist Issues

#### "Wordlist file not found"
```bash
# Check file exists
ls -la wordlists/passwords.txt

# Expand path
./appt brute 192.168.1.1 -u admin -w $(pwd)/wordlists/passwords.txt
```

#### Custom Wordlists
```bash
# Create custom wordlist
cat > custom_passwords.txt << EOF
password123
admin123
letmein
qwerty123
EOF

./appt brute 192.168.1.1 -u admin -w custom_passwords.txt
```

### Docker Issues

#### "Docker daemon is not running"
```bash
# Start Docker
sudo systemctl start docker  # Linux
open /Applications/Docker.app  # macOS

# Verify
docker ps
```

#### "Permission denied while trying to connect to Docker daemon"
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Restart Docker
sudo systemctl restart docker
```

### Network Issues

#### Scan timing out
```bash
# Check network connectivity
traceroute 192.168.1.1

# Reduce scan scope
./appt scan 192.168.1.1 -p 80,443,22

# Use longer timeout
./appt scan 192.168.1.1 --timeout 10
```

#### High failure rate
```bash
# Enable verbose mode to see errors
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt -v

# Reduce rate of attempts
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt --delay 2.0
```

---

## Security Best Practices

### Before Running APPT

1. **Get Authorization**
   - Always obtain written permission before testing
   - Document scope of testing
   - Have clear rules of engagement (RoE)

2. **Network Isolation**
   ```bash
   # Only test on authorized systems
   # Use VPN for remote testing
   # Avoid public networks
   ```

3. **Target Verification**
   ```bash
   # Verify IP addresses
   nslookup target.example.com
   ping target.example.com
   ```

### During Operations

4. **Monitor System Impact**
   ```bash
   # Use reasonable thread counts
   ./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt -t 10

   # Implement rate limiting
   ./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt --delay 1.0
   ```

5. **Log Everything**
   ```bash
   # Save detailed reports
   ./appt scan 192.168.1.1 --json -o scan_report.json -v

   # Enable audit logging
   export APPT_LOG_LEVEL=DEBUG
   ```

6. **Use Non-Destructive Testing**
   - Scanning only reads network state
   - Brute forcing only attempts authentication
   - No modification or deletion operations

### After Testing

7. **Secure Results**
   ```bash
   # Encrypt sensitive files
   gpg -c output/results.json

   # Restrict permissions
   chmod 600 output/*.json

   # Store in secure location
   ```

8. **Clean Up**
   ```bash
   # Remove logs from target systems
   # Document all findings
   # Provide complete report
   ```

### Compliance

9. **Legal Requirements**
   - Follow local cybersecurity laws
   - Comply with GDPR/CCPA for data
   - Maintain confidentiality agreements
   - Document all testing activities

10. **Ethical Guidelines**
    - Respect system availability
    - Don't access unauthorized data
    - Disclose findings responsibly
    - Use least privilege principle

### Operational Security (OpSec)

```bash
# Use random delay between attempts
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt --profile stealth_mode

# Randomize user agent (HTTP only)
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt --randomize-user-agent

# Distribute load over time
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt --stagger 10s

# Use proxy/VPN
# (Configure before running APPT)
```

---

## Getting Help

### Help Commands

```bash
# General help
./appt --help

# Scan command help
./appt scan --help

# Brute force command help
./appt brute --help

# Version information
./appt --version
```

### Useful Resources

- **Documentation:** See `docs/` directory
- **Examples:** `examples.py` - Working code samples
- **Architecture:** `docs/ARCHITECTURE.md` - Design details
- **API Reference:** `docs/API_REFERENCE.md` - All classes and methods
- **Troubleshooting:** This manual's troubleshooting section

### Reporting Issues

```bash
# Collect system information
python3 --version
pip list | grep -E 'paramiko|requests|pyyaml'
cat /etc/os-release  # Linux
system_profiler SPSoftwareDataType  # macOS

# Run with verbose mode
./appt scan 192.168.1.1 -v

# Check logs
tail -100 logs/appt.log
```

---

## Appendix: Common Commands Reference

### Port Scanning

```bash
# Quick scan
./appt scan 192.168.1.1 --quick

# Full scan (1-65535)
./appt scan 192.168.1.1 -p 1-65535

# Specific ports
./appt scan 192.168.1.1 -p 22,80,443,3306,5432

# Fast scan with many threads
./appt scan 192.168.1.1 --quick -t 200

# Slow, careful scan
./appt scan 192.168.1.1 -p 1-10000 -t 5 --timeout 5

# Batch scan
./appt scan targets.txt --quick
```

### Brute Forcing

```bash
# SSH with single user
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt --protocol ssh

# FTP with user list
./appt brute 192.168.1.1 -U wordlists/usernames.txt -w wordlists/passwords.txt

# HTTP web form
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt --protocol http

# MySQL database
./appt brute 192.168.1.1 -u root -w wordlists/passwords.txt --protocol mysql

# Combo attack
./appt brute 192.168.1.1 --attack-mode combo -w combo.txt

# Stop on first match
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt --stop-on-success
```

### Output & Reporting

```bash
# Save to file (auto-format)
./appt scan 192.168.1.1 -o results.json

# JSON output
./appt scan 192.168.1.1 --json -o results.json

# CSV output
./appt brute 192.168.1.1 -u admin -w wordlists/passwords.txt -o results.csv

# All formats
./appt scan 192.168.1.1 --output-all
```

---

**End of User Manual**

For additional information, see:
- `README.md` - Project overview
- `ARCHITECTURE.md` - Technical design
- `API_REFERENCE.md` - Code documentation
- `CODE_WALKTHROUGH.md` - Line-by-line explanation
