# GitHub Deployment Guide

**Complete Instructions for Uploading APPT to GitHub**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Repository Setup](#repository-setup)
3. [Initial Push](#initial-push)
4. [GitHub Configuration](#github-configuration)
5. [Documentation & Badges](#documentation--badges)
6. [Releases & Versioning](#releases--versioning)
7. [Collaboration Setup](#collaboration-setup)
8. [CI/CD Setup (Optional)](#cicd-setup-optional)
9. [Maintenance](#maintenance)

---

## Prerequisites

### Required Software

1. **Git** (2.0+)
   ```bash
   # Verify installation
   git --version
   ```

2. **GitHub Account**
   - Create account at https://github.com
   - Verify email address
   - Enable 2FA (recommended)

3. **SSH Keys Setup** (Recommended over HTTPS)
   ```bash
   # Generate SSH key
   ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
   
   # Add to SSH agent
   eval $(ssh-agent -s)
   ssh-add ~/.ssh/id_rsa
   
   # Copy public key to clipboard
   cat ~/.ssh/id_rsa.pub
   
   # Add to GitHub: Settings > SSH and GPG keys > New SSH key
   ```

4. **Git Configuration**
   ```bash
   # Configure user identity
   git config --global user.name "Your Name"
   git config --global user.email "your-email@example.com"
   
   # Verify
   git config --global --list
   ```

---

## Repository Setup

### Step 1: Initialize Local Repository

```bash
# Navigate to project directory
cd /home/jeff/Documents/Files/Projects/PENETRATION-TESTING-TOOLKIT

# Initialize git (if not already done)
git init

# Check current status
git status
```

### Step 2: Create .gitignore File

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Logs
*.log
logs/
*.pid

# Output
output/
*.json
*.csv
*.xml

# Testing
.pytest_cache/
.coverage
htmlcov/

# Sensitive
*.key
*.pem
secrets/
.env
EOF
```

### Step 3: Create LICENSE File

**MIT License (Recommended):**

```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

**Alternative Licenses:**
- Apache 2.0: https://www.apache.org/licenses/LICENSE-2.0
- GPL 3.0: https://www.gnu.org/licenses/gpl-3.0.html

### Step 4: Create CONTRIBUTING Guide

```bash
cat > CONTRIBUTING.md << 'EOF'
# Contributing to APPT

Thank you for your interest in contributing!

## How to Contribute

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes and test
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature/your-feature`
6. Submit pull request

## Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update documentation
- Ensure all tests pass

## Reporting Issues

Use GitHub Issues to report bugs:
- Clear description of issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details
EOF
```

### Step 5: Create CHANGELOG.md

```bash
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

## [2.1.0] - 2026-01-15

### Added
- Multi-threaded port scanning with service fingerprinting
- Advanced brute force with Hydra-style attack modes
- Configuration management with YAML profiles
- Multi-format reporting (JSON, CSV, HTML, XML)
- Enterprise logging and error handling
- Docker containerization support

### Changed
- Improved performance with thread pooling
- Enhanced service detection
- Better error messages

### Fixed
- Zero division error in HTML reports
- CSV export error handling
- Improved error context in logging

## [2.0.0] - 2025-06-17

### Added
- Initial multi-threaded port scanner
- Basic brute force functionality
- Multiple protocol support

EOF
```

---

## Initial Push

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in details:
   - **Repository name:** `penetration-testing-toolkit` (or similar)
   - **Description:** "Advanced Penetration Testing Toolkit - Professional security assessment framework"
   - **Public/Private:** Choose based on preference
   - **README:** Don't initialize (we have one)
   - **.gitignore:** Python (we created custom)
   - **License:** MIT (we created custom)
3. Click "Create repository"

### Step 2: Add Remote and Push

```bash
# Add remote repository
git remote add origin https://github.com/yourusername/penetration-testing-toolkit.git

# Or with SSH (recommended):
git remote add origin git@github.com:yourusername/penetration-testing-toolkit.git

# Verify remote
git remote -v

# Stage all files
git add .

# Initial commit
git commit -m "Initial commit: APPT v2.1 - Professional Penetration Testing Toolkit"

# Push to GitHub
git branch -M main  # Rename to main if needed
git push -u origin main
```

### Step 3: Verify Upload

1. Visit https://github.com/yourusername/penetration-testing-toolkit
2. Verify all files are present
3. Check README displays correctly
4. Verify file structure is intact

---

## GitHub Configuration

### Step 1: Repository Settings

1. Go to repository Settings
2. Set default branch to `main`
3. Enable branch protection:
   - Settings > Branches > Branch protection rules
   - Require pull request reviews
   - Dismiss stale reviews
   - Require status checks

### Step 2: Add Topics

1. Settings > General > Topics
2. Add relevant keywords:
   - `security`
   - `penetration-testing`
   - `network-security`
   - `brute-force`
   - `port-scanner`
   - `hydra`
   - `infosec`

### Step 3: Configure Webhooks (Optional)

1. Settings > Webhooks
2. Add webhook for CI/CD if needed
3. Configure branch restrictions

### Step 4: Enable Discussions (Optional)

1. Settings > Features > Discussions
2. Enable for community questions

---

## Documentation & Badges

### Step 1: Create README Badge Section

Add to top of README.md:

```markdown
# Advanced Penetration Testing Toolkit (APPT)

[![GitHub license](https://img.shields.io/github/license/yourusername/penetration-testing-toolkit?style=flat-square)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/penetration-testing-toolkit?style=flat-square)](https://github.com/yourusername/penetration-testing-toolkit/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/penetration-testing-toolkit?style=flat-square)](https://github.com/yourusername/penetration-testing-toolkit/network)
[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue?style=flat-square)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

Professional security assessment framework inspired by Hydra and industry-standard tools.

...rest of README
```

### Step 2: Add Status Badge

Create workflows (if using GitHub Actions):

```bash
mkdir -p .github/workflows
cat > .github/workflows/python-test.yml << 'EOF'
name: Python Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest tests/ -v
EOF
```

### Step 3: Add .github/ISSUE_TEMPLATE

```bash
mkdir -p .github/ISSUE_TEMPLATE

cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug report
about: Create a report to help us improve

---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Command: `./appt ...`
2. Expected: ...
3. Actual: ...

**Environment**
- OS: Linux/Windows/macOS
- Python version: 3.x
- APPT version: 2.1

**Error messages**
```
Paste error here
```

**Screenshots**
If applicable, add screenshots.
EOF

cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature request
about: Suggest an idea

---

**Is your feature related to a problem?**
Description of the problem.

**Describe the solution you'd like**
Description of desired solution.

**Describe alternatives you've considered**
Description of alternatives.

**Additional context**
Any other context.
EOF
```

---

## Releases & Versioning

### Step 1: Create Release

1. Go to GitHub repository
2. Click "Releases" tab
3. Click "Create a new release"
4. Fill in details:
   - **Tag version:** `v2.1.0`
   - **Release title:** `APPT v2.1.0 - Professional Penetration Testing Toolkit`
   - **Description:** (Copy from CHANGELOG.md)
5. Click "Publish release"

### Step 2: Update Version in Code

```bash
# Update version in appt
sed -i "s/__version__ = .*/__version__ = '2.1.0'/g" appt

# Or edit manually
```

### Step 3: Semantic Versioning Guide

```
MAJOR.MINOR.PATCH[-PRERELEASE]

- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

Examples:
  v1.0.0 - First release
  v2.0.0 - Major rewrite
  v2.1.0 - New features
  v2.1.1 - Bug fix
  v3.0.0-alpha.1 - Pre-release
```

---

## Collaboration Setup

### Step 1: Add Collaborators

1. Settings > Manage access > Invite a collaborator
2. Enter GitHub username
3. Set permissions:
   - **Pull requests:** Read & write
   - **Issues:** Read & write
   - **Admin:** Full access

### Step 2: Create Teams (For Organizations)

1. Create organization at https://github.com/organizations/new
2. Invite members
3. Create teams for different roles

### Step 3: Code Review Process

Create standard workflow:

```bash
cat > .github/PULL_REQUEST_TEMPLATE.md << 'EOF'
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change

## Testing
- [ ] Tested on Linux
- [ ] Tested on macOS
- [ ] Tested on Windows

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
EOF
```

---

## CI/CD Setup (Optional)

### GitHub Actions Example

```bash
cat > .github/workflows/lint.yml << 'EOF'
name: Code Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install linting tools
      run: |
        pip install flake8 black isort
    - name: Check formatting
      run: |
        black --check src/
        isort --check-only src/
    - name: Run linter
      run: |
        flake8 src/ --max-line-length=100
EOF
```

---

## Maintenance

### Regular Tasks

1. **Weekly:**
   - Review issues and pull requests
   - Test latest changes
   - Update documentation

2. **Monthly:**
   - Merge pull requests
   - Release minor updates
   - Update dependencies

3. **Quarterly:**
   - Major feature releases
   - Security audits
   - Update changelog

### Keeping Dependencies Updated

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade paramiko

# Update all
pip install --upgrade -r requirements.txt

# Save updated requirements
pip freeze > requirements.txt
```

### Security Updates

```bash
# Check for vulnerabilities
pip install safety
safety check

# Or use GitHub's security alerts
# Settings > Code security and analysis > Enable Dependabot
```

---

## Creating Releases

### Step-by-Step Release Process

```bash
# 1. Update version number
# 2. Update CHANGELOG.md
# 3. Run tests
python -m pytest tests/ -v

# 4. Commit changes
git add .
git commit -m "Release v2.2.0"

# 5. Create git tag
git tag -a v2.2.0 -m "Release version 2.2.0"

# 6. Push to GitHub
git push origin main
git push origin v2.2.0

# 7. Create release on GitHub (UI)
# Go to Releases > Create new release
# Tag: v2.2.0
# Title: APPT v2.2.0
# Description: (from CHANGELOG)
```

---

## Documentation Hosting

### Option 1: GitHub Pages

```bash
# Create docs site from README
# Settings > Pages > Source > main branch /docs folder

# Or use MkDocs:
pip install mkdocs
mkdocs new .
mkdocs serve  # Preview locally
mkdocs build  # Generate static site
```

### Option 2: ReadTheDocs

1. Go to https://readthedocs.org
2. Sign in with GitHub
3. Add project
4. Connect GitHub repository
5. Build documentation automatically

---

## Promoting Your Repository

### GitHub

- Add to GitHub topics
- Create releases with detailed notes
- Pin important issues/discussions
- Update README with examples

### Social Media

```
Twitter:
"Just released APPT v2.1 - Advanced Penetration Testing Toolkit!
🔍 Multi-threaded port scanner
🔓 Professional brute forcer
⚙️ Enterprise features
GitHub: [link]
#infosec #cybersecurity #hacking"

LinkedIn:
Similar professional tone...

Reddit:
Share to /r/cybersecurity, /r/netsec, /r/python
```

### Other Sites

- ProductHunt
- HackerNews
- GitHub Trending
- Awesome lists

---

## Complete Checklist

- [ ] Git initialized locally
- [ ] .gitignore configured
- [ ] LICENSE added
- [ ] README.md complete
- [ ] CONTRIBUTING.md created
- [ ] CHANGELOG.md created
- [ ] GitHub account created
- [ ] Repository created on GitHub
- [ ] SSH keys configured
- [ ] Initial push completed
- [ ] Topics added
- [ ] Branch protection enabled
- [ ] Badges added to README
- [ ] Discussions/Issues templates created
- [ ] Release created
- [ ] Collaborators invited (if applicable)
- [ ] CI/CD configured (if needed)
- [ ] Documentation complete

---

## Troubleshooting

### Authentication Error

```bash
# If HTTPS:
git config --global credential.helper store

# If SSH:
ssh -T git@github.com  # Test connection
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa
```

### Push Rejected

```bash
# Pull latest changes
git pull origin main

# Resolve conflicts if any
git status

# Try push again
git push origin main
```

### Wrong Remote

```bash
# Check current remote
git remote -v

# Change remote
git remote set-url origin https://github.com/newusername/repo.git

# Or remove and add
git remote remove origin
git remote add origin https://github.com/newusername/repo.git
```

---

## Next Steps

1. ✅ Follow this guide to upload to GitHub
2. ✅ Share repository link
3. ✅ Monitor stars and issues
4. ✅ Respond to community contributions
5. ✅ Plan v3.0 features
6. ✅ Consider adding web UI/API

---

**Your APPT project is now ready for the world!** 🚀

For documentation, see:
- [README.md](../README.md) - Overview
- [USER_MANUAL.md](../USER_MANUAL.md) - Usage guide
- [CODE_WALKTHROUGH.md](../CODE_WALKTHROUGH.md) - Implementation details
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System design
