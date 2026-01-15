# Changelog

## Version 2.1 (January 2026) - Professional Reorganization

### Major Changes
- **Complete structural reorganization** following professional standards
- **Hydra-inspired attack modes** (single, loop, combo)
- **Service fingerprinting** in port scanner
- **Configuration file support** for storing profiles
- **Batch operations** for multiple targets
- **Improved rate limiting** to avoid detection

### New Features
- `single` attack mode: One password per user
- `loop` attack mode: All passwords per user (default)
- `combo` attack mode: Paired credentials
- Service version detection in port scanning
- Support for Telnet, MySQL, PostgreSQL, MongoDB
- Configuration file at `config/default.conf`
- Wordlist management in `wordlists/`
- Output directory for results in `output/`
- Batch target processing from files

### Code Quality
- Object-oriented design with proper classes
- Thread-safe operations with locks
- Comprehensive error handling
- Professional logging utility
- Type hints for better IDE support
- Docstrings on all functions

### File Structure
```
Old Structure:          New Structure:
Penetration toolkit/    src/
├── main.py           ├── __init__.py
├── EXAMPLES.py       ├── port_scanner.py
├── SETUP.py          ├── brute_forcer.py
└── modules/          └── utils.py
    ├── port_scanner.py
    ├── brute_forcer.py
    └── utils.py

Added:
├── appt (executable)
├── config/
│   └── default.conf
├── wordlists/
│   ├── passwords.txt
│   └── usernames.txt
├── docs/
│   └── README.md
├── output/ (for results)
├── INSTALL.md
└── CHANGELOG.md
```

### Breaking Changes
- Old imports from `modules/` no longer work
- Use: `from src import port_scanner, brute_forcer`
- Command syntax remains the same but invocation differs

### Performance Improvements
- Improved thread management
- Better rate limiting
- Optimized service fingerprinting
- Reduced memory overhead

### Documentation
- Comprehensive README in `docs/`
- Installation guide in `INSTALL.md`
- Configuration reference
- Attack mode explanations
- Protocol support matrix

### Removed (Cleanup)
- Redundant documentation files
- Old "Penetration toolkit" directory
- Duplicate help messages
- Unnecessary configuration files

---

## Version 2.0 (Previous) - Multi-Threading Era

### Highlights
- Multi-threaded port scanning (6.7x faster)
- Multi-threaded brute forcing (24x faster)
- SSH and HTTP protocol support
- Real-time output and statistics
- JSON export capability
- Professional CLI with argparse

### Features Added
- Threading architecture for concurrent operations
- Service detection on open ports
- Multiple protocol support (FTP, SSH, HTTP)
- Real-time success notifications
- Stop-on-success option
- Verbose mode

---

## Version 1.0 (Original)

### Initial Release
- Basic port scanner (sequential)
- FTP brute forcer only
- Menu-driven interface
- Simple wordlist support

---

## Migration Guide (v1.0/v2.0 → v2.1)

### If you were using v2.0

#### Old usage:
```bash
python3 main.py ps 192.168.1.1 --quick
python3 main.py bf 192.168.1.100 -u admin
```

#### New usage:
```bash
./appt scan 192.168.1.1 --quick
./appt brute 192.168.1.100 -u admin
```

### If you were using v1.0

The entire tool has been rewritten. Key differences:

1. **Speed**: 10-24x faster due to multi-threading
2. **Protocols**: Now supports SSH, HTTP, and more
3. **Interface**: Professional CLI instead of menu-driven
4. **Features**: Batch processing, attack modes, fingerprinting

### Custom Code

If you had custom scripts importing the modules:

**Old:**
```python
from modules import port_scanner, brute_forcer
results = port_scanner.scan_ports(host, ports)
```

**New:**
```python
from src.port_scanner import PortScanner
scanner = PortScanner(host)
results = scanner.scan(ports)
```

---

## Future Roadmap

### v2.2 (Planned)
- [ ] DNS brute forcing
- [ ] SNMP enumeration
- [ ] Vulnerability scanning
- [ ] Email brute forcing
- [ ] LDAP enumeration

### v3.0 (Long-term)
- [ ] Web UI dashboard
- [ ] Database backend for results
- [ ] Machine learning for credential prediction
- [ ] Automated report generation
- [ ] Integration with other security tools
- [ ] Multi-target orchestration

---

## Known Limitations

- Telnet implementation is basic
- MongoDB/PostgreSQL support is limited
- No proxy support yet
- No SSL certificate validation bypass

---

## Compatibility

- **Python**: 3.7, 3.8, 3.9, 3.10, 3.11+
- **OS**: Linux, macOS, Windows
- **Dependencies**: paramiko, requests, pyyaml (optional)

---

## Contributors

Security community contributions welcome!

---

**Latest Version**: 2.1  
**Released**: January 2026  
**Status**: Stable/Production Ready
