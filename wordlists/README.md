# Wordlist Directory

## Overview

This directory contains comprehensive password wordlists for penetration testing.

## Files

### passwords.txt
**Massive expanded wordlist with 29,946 unique passwords**

**File Size**: 178 KB  
**Total Entries**: 29,946 passwords  
**Format**: Plain text (one password per line)

#### Password Categories Included

| Category | Count | Examples |
|----------|-------|----------|
| Numeric Patterns | 20,000+ | 0000-9999 (4-digit), 00000-99999 (5-digit) |
| Year Variations | 425+ | 1950-2035, with !, @, # variants |
| Service Names | 800+ | cisco1-10, linux1-10, mysql1-10, postgres1-10, etc. |
| Phrases | 720+ | letmein0-19, changeme0-19, welcome0-19, etc. |
| Special Characters | 300+ | admin!, admin@, admin#, admin!123, etc. |
| Doubles | 900+ | 100100, 101101...999999, pass100-999, user100-999 |
| Letter+Number | 3,000+ | a100-b199, c100-d199, etc. |
| Common Words | 361 | password, admin, test, linux, ubuntu, etc. |

#### Services Covered

✅ Cisco (cisco1-10, etc.)  
✅ Linux/Unix (linux, ubuntu, debian, centos, fedora, etc.)  
✅ Windows (Administrator, server, gateway, etc.)  
✅ Databases (mysql, postgres, oracle, mongodb, etc.)  
✅ Web Servers (apache, nginx, tomcat, etc.)  
✅ Network (ssh, ftp, smtp, telnet, snmp, etc.)  
✅ Container (docker)  
✅ CI/CD (jenkins)  

#### Patterns Generated

- **Numeric**: 0000 → 99999 (10,000 4-digit + 10,000 5-digit)
- **Years**: 1950 → 2035 with variants (!, @, #, pass prefix)
- **Service+Number**: cisco1, cisco2, ..., cisco10 with special chars
- **Phrases+Number**: letmein0-19, changeme0-19, etc.
- **Double Numbers**: 100100, 101101, 102102, ...999999
- **Letter+Number**: a100-a199, b100-b199, ..., o100-o199

### usernames.txt
**Common system usernames for pair testing**

**File Size**: 5 KB  
**Total Entries**: ~50 common usernames

Includes:
- System accounts (admin, root, guest, test, user, operator)
- Service accounts (www, www-data, apache, nginx, postgres, mysql, mongodb)
- Common users (administrator, backup, support, help, guest)

## Usage

### Single User + Wordlist
```bash
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt
```

### Multiple Users + Wordlist
```bash
./appt brute 192.168.1.100 -U wordlists/usernames.txt -w wordlists/passwords.txt
```

### With Attack Modes

**Single Mode** - One password per user:
```bash
./appt brute 192.168.1.100 -U wordlists/usernames.txt -w wordlists/passwords.txt --attack-mode single
```

**Loop Mode** - All passwords per user (DEFAULT):
```bash
./appt brute 192.168.1.100 -U wordlists/usernames.txt -w wordlists/passwords.txt --attack-mode loop
```

**Combo Mode** - Paired credentials:
```bash
./appt brute 192.168.1.100 -U wordlists/combo.txt -w wordlists/combo.txt --attack-mode combo
```

### Protocols

Works with all protocols supported by the toolkit:
```bash
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --protocol ssh
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --protocol ftp
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --protocol http
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --protocol telnet
./appt brute 192.168.1.100 -u admin -w wordlists/passwords.txt --protocol mysql
```

## Performance Notes

With 29,946 passwords:
- **Single threaded**: ~60-120 seconds per user (depending on protocol & network)
- **10 threads**: ~6-12 seconds per user
- **20 threads**: ~3-6 seconds per user

Configure threads:
```bash
./appt brute 192.168.1.100 -U wordlists/usernames.txt -w wordlists/passwords.txt -T 20
```

## Custom Wordlists

To create your own wordlist:

1. Create a new file (e.g., `custom.txt`)
2. Add one password per line
3. Use it:
```bash
./appt brute 192.168.1.100 -u admin -w wordlists/custom.txt
```

## Combining Wordlists

Merge multiple wordlists:
```bash
cat passwords.txt passwords.txt > combined.txt
# Or with custom lists
cat wordlists/passwords.txt custom.txt > merged.txt
./appt brute 192.168.1.100 -u admin -w wordlists/merged.txt
```

## Notes

- ✅ All passwords are based on **real-world common patterns**
- ✅ Includes defaults for **major OS and services**
- ✅ Cross-platform compatible
- ✅ Sorted alphabetically for consistency
- ✅ Suitable for authorized penetration testing

## Legal Notice

These wordlists are for **authorized security testing only**. Unauthorized access to computer systems is illegal. Always obtain proper authorization before conducting penetration tests.

---

**Wordlist Size**: 178 KB  
**Passwords**: 29,946  
**Last Updated**: January 15, 2026
