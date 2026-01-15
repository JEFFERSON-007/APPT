# Enterprise Deployment Guide

## Pre-Deployment Checklist

- [ ] Security review completed
- [ ] Network access verified
- [ ] Authorization documented
- [ ] Logging infrastructure ready
- [ ] Backup procedures in place
- [ ] Incident response plan reviewed

---

## Deployment Architectures

### 1. Standalone Workstation Deployment

**Best for**: Single operator, focused assessments, local testing

```bash
# Installation
git clone <repo> /opt/pentesting-toolkit
cd /opt/pentesting-toolkit
pip install -r requirements.txt
chmod +x appt

# Quick test
./appt --help

# Create local logs
mkdir -p logs output config/profiles
```

**System Requirements**:
- Python 3.9+
- 2+ GB RAM
- 500 MB disk space
- Network connectivity

---

### 2. Docker Container Deployment

**Best for**: Isolated environment, quick deployment, consistent setup

```bash
# Build image
docker build -t pentest-toolkit:latest .

# Run container
docker run -it \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/wordlists:/app/wordlists \
  pentest-toolkit scan 192.168.1.0/24 --quick

# Run as daemon
docker run -d \
  --name pentesting \
  -v $(pwd)/output:/app/output \
  pentest-toolkit
```

**Dockerfile Optimizations**:
```dockerfile
# Multi-stage build for smaller image
FROM python:3.11-slim as builder
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
```

---

### 3. Kubernetes Deployment

**Best for**: Large-scale assessments, enterprise infrastructure, high availability

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pentesting-toolkit
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pentesting
  template:
    metadata:
      labels:
        app: pentesting
    spec:
      containers:
      - name: toolkit
        image: pentest-toolkit:latest
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "2000m"
        volumeMounts:
        - name: output
          mountPath: /app/output
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: output
        persistentVolumeClaim:
          claimName: output-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: logs-pvc
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
kubectl scale deployment pentesting-toolkit --replicas=5
```

---

### 4. Enterprise Infrastructure Deployment

**Architecture**:
```
┌─────────────────────────────────────────┐
│     Penetration Testing Platform        │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │ Scanner  │  │ Brute    │            │
│  │ Nodes    │  │ Force    │ (Scaled)   │
│  │ (10)     │  │ Nodes(5) │            │
│  └────┬─────┘  └────┬─────┘            │
│       └─────┬───────┘                  │
│             ▼                          │
│  ┌─────────────────────────┐           │
│  │   Central Logger        │           │
│  │  (ELK/Splunk/Datadog)   │           │
│  └────────────┬────────────┘           │
│               ▼                        │
│  ┌─────────────────────────┐           │
│  │   Results Database      │           │
│  │  (PostgreSQL/MongoDB)   │           │
│  └────────────┬────────────┘           │
│               ▼                        │
│  ┌─────────────────────────┐           │
│  │   Dashboard/Reporting   │           │
│  │   (Grafana/Kibana)      │           │
│  └─────────────────────────┘           │
└─────────────────────────────────────────┘
```

**Configuration**:
```yaml
# config/enterprise.yaml
scanner:
  threads: 50
  timeout: 3.0
  output_format: "elasticsearch"

brute_force:
  threads: 20
  connection_pool_size: 100

elasticsearch:
  hosts: ["elasticsearch-1:9200", "elasticsearch-2:9200"]
  cluster_name: "pentest-cluster"
  index_pattern: "pentest-{YYYY.MM.DD}"

monitoring:
  prometheus_enabled: true
  datadog_enabled: true
  custom_webhooks:
    - "https://siem.company.com/api/results"
```

---

## Installation Methods

### Method 1: Pip Installation

```bash
pip install --user pentesting-toolkit
pentesting-toolkit --version
```

### Method 2: From Source

```bash
git clone <repo>
cd pentesting-toolkit
pip install -e .
```

### Method 3: System Package (Linux)

```bash
# Create .deb package
sudo apt install ./pentesting-toolkit_2.1_amd64.deb

# Or .rpm
sudo rpm -i ./pentesting-toolkit-2.1.x86_64.rpm
```

### Method 4: Conda Environment

```bash
conda create -n pentesting python=3.11
conda activate pentesting
pip install -r requirements.txt
```

---

## Security Hardening

### 1. Filesystem Permissions

```bash
# Restrict config files
chmod 600 config/*.yaml

# Restrict logs
chmod 750 logs/
chmod 640 logs/*.log

# Restrict output
chmod 750 output/
chmod 640 output/*
```

### 2. Firewall Configuration

```bash
# Allow outbound connections only to authorized targets
sudo iptables -A OUTPUT -d 192.168.1.0/24 -p tcp --dport 22 -j ACCEPT
sudo iptables -A OUTPUT -d 10.0.0.0/8 -p tcp --dport 80 -j ACCEPT
sudo iptables -P OUTPUT DROP
```

### 3. System Hardening

```bash
# Run as non-root user
sudo useradd -m -s /bin/false pentest
sudo chown -R pentest:pentest /opt/pentesting-toolkit

# Limit resource usage
ulimit -n 10000   # File descriptors
ulimit -u 100     # Processes
```

### 4. Network Isolation

```bash
# Create isolated VPC/subnet for scanning
# Configure through VPN tunnel
# Log all outbound connections
```

---

## Monitoring & Maintenance

### Performance Monitoring

```bash
# Watch system resources
watch -n 1 'ps aux | grep appt'

# Monitor network connections
netstat -an | grep ESTABLISHED | wc -l

# Check disk usage
df -h logs/ output/
```

### Log Monitoring

```bash
# Real-time log viewing
tail -f logs/toolkit.log

# Audit log monitoring
tail -f logs/toolkit_audit.log | grep "FAILED"

# Error tracking
grep ERROR logs/toolkit.log | head -20
```

### Backup Strategy

```bash
# Daily backup of results
0 2 * * * tar czf backups/output-$(date +\%Y\%m\%d).tar.gz output/

# Log rotation (automatic via logging module)
# Audit logs retained for 90 days
logrotate -f /etc/logrotate.d/pentesting-toolkit
```

---

## Troubleshooting Deployment

### Issue: "Module not found"

```bash
# Verify installation
python3 -c "from src import port_scanner; print('OK')"

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Issue: "Permission denied"

```bash
# Check ownership
ls -la appt

# Fix permissions
chmod +x appt
sudo chown $USER:$USER -R .
```

### Issue: "Connection refused"

```bash
# Check network connectivity
ping 192.168.1.1

# Verify DNS resolution
nslookup target.com

# Test port access
nc -zv 192.168.1.100 22
```

### Issue: "Memory/CPU overload"

```bash
# Reduce thread count
./appt scan 192.168.1.0/24 -T 5

# Increase timeout
./appt scan 192.168.1.0/24 --timeout 10

# Use rate limiting
./appt brute 192.168.1.100 --delay 2.0
```

---

## Post-Deployment

### 1. Initial Testing

```bash
# Test scanner
./appt scan 127.0.0.1 --quick

# Test brute forcer (local lab only)
./appt brute 192.168.100.1 -u test -w wordlists/passwords.txt --dry-run

# Verify logging
tail logs/toolkit.log
```

### 2. Configuration Tuning

```bash
# Create custom profile for your environment
cp config/example_profiles.yaml config/my_profile.yaml

# Edit with your parameters
nano config/my_profile.yaml

# Test profile
./appt scan 192.168.1.0/24 --profile my_profile
```

### 3. Team Training

- [ ] Document approved targets
- [ ] Train operators on usage
- [ ] Establish rules of engagement
- [ ] Review audit logs
- [ ] Implement approval workflow

---

## Scaling Considerations

### Small Deployment (1-10 targets)
- Single instance sufficient
- Local logging adequate
- Manual result review

### Medium Deployment (10-100 targets)
- 3-5 scanner instances
- Centralized logging (ELK)
- Automated reporting

### Large Deployment (100+ targets)
- 10+ instances with load balancer
- Elasticsearch cluster
- Real-time dashboards
- Automated response integration

---

## Support & SLAs

For enterprise deployments, ensure:

- 24/7 logging infrastructure
- Regular backup testing
- Incident response procedures
- Performance baselines
- Security audit trails
- Compliance documentation

---

**Last Updated**: January 15, 2026  
**Version**: 2.1-Enterprise
