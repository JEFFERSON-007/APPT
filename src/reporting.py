"""
Enterprise Reporting and Results Management System
Supports multiple output formats with detailed statistics and findings
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ResultStatus(Enum):
    """Result status codes"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"
    SKIPPED = "skipped"


class SeverityLevel(Enum):
    """Severity levels for findings"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ScanResult:
    """Individual scan result"""
    target: str
    port: int
    service: str
    version: Optional[str] = None
    status: str = "open"
    timestamp: str = None
    response_time: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class CredentialResult:
    """Brute force attempt result"""
    target: str
    username: str
    password: str
    protocol: str
    status: ResultStatus = ResultStatus.FAILED
    attempts: int = 1
    response_time: float = 0.0
    timestamp: str = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        
        if isinstance(self.status, str):
            self.status = ResultStatus(self.status)


@dataclass
class AttackSummary:
    """Summary statistics for an attack"""
    attack_type: str  # 'scan' or 'brute_force'
    target: str
    start_time: str
    end_time: str
    duration: float
    total_attempts: int
    successful: int
    failed: int
    errors: int
    success_rate: float
    
    def __post_init__(self):
        if self.success_rate == 0 and self.total_attempts > 0:
            self.success_rate = (self.successful / self.total_attempts) * 100


class ReportGenerator:
    """
    Enterprise report generation
    
    Supports:
    - JSON reports
    - CSV exports
    - HTML reports with statistics
    - XML reports
    - Custom formatting
    """
    
    def __init__(self, output_dir: Path = Path("./output")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: List[Dict[str, Any]] = []
        self.summaries: List[AttackSummary] = []
    
    def add_scan_result(self, result: ScanResult):
        """Add port scan result"""
        self.results.append(asdict(result))
    
    def add_credential_result(self, result: CredentialResult):
        """Add brute force result"""
        data = asdict(result)
        data['status'] = result.status.value
        self.results.append(data)
    
    def add_summary(self, summary: AttackSummary):
        """Add attack summary"""
        self.summaries.append(summary)
    
    def generate_json_report(self, filename: str = None) -> str:
        """Generate JSON report"""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_results': len(self.results),
            'summaries': [asdict(s) for s in self.summaries],
            'results': self.results
        }
        
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(filepath)
    
    def generate_csv_report(self, filename: str = None) -> str:
        """Generate CSV report"""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not self.results:
            raise ValueError("No results to export")
        
        filepath = self.output_dir / filename
        
        # Get all possible keys
        all_keys = set()
        for result in self.results:
            all_keys.update(result.keys())
        
        fieldnames = sorted(list(all_keys))
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
        
        return str(filepath)
    
    def generate_html_report(self, filename: str = None) -> str:
        """Generate comprehensive HTML report"""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        filepath = self.output_dir / filename
        
        # Calculate statistics
        total_results = len(self.results)
        successful = sum(1 for r in self.results if r.get('status') == 'success')
        failed = sum(1 for r in self.results if r.get('status') == 'failed')
        
        # Calculate success rate safely
        success_rate = (successful / total_results * 100) if total_results > 0 else 0.0
        
        # Build HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Penetration Testing Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-box.success {{ background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); color: #333; }}
        .stat-box.failed {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: #333; }}
        .stat-box.total {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.8;
            margin-top: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background-color: #f8f9fa;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
            font-weight: 600;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .success-row {{ background-color: #d4edda; }}
        .failed-row {{ background-color: #f8d7da; }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Penetration Testing Report</h1>
        
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Summary Statistics</h2>
        <div class="stats">
            <div class="stat-box total">
                <div class="stat-number">{total_results}</div>
                <div class="stat-label">Total Results</div>
            </div>
            <div class="stat-box success">
                <div class="stat-number">{successful}</div>
                <div class="stat-label">Successful</div>
            </div>
            <div class="stat-box failed">
                <div class="stat-number">{failed}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-box total">
                <div class="stat-number">{success_rate:.1f}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
        </div>
        
        <h2>Detailed Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Target</th>
                    <th>Service/Protocol</th>
                    <th>Status</th>
                    <th>Timestamp</th>
                    <th>Response Time</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in self.results:
            row_class = 'success-row' if result.get('status') == 'success' else 'failed-row'
            html += f"""                <tr class="{row_class}">
                    <td>{result.get('target', 'N/A')}</td>
                    <td>{result.get('service', result.get('protocol', 'N/A'))}</td>
                    <td><strong>{result.get('status', 'N/A')}</strong></td>
                    <td>{result.get('timestamp', 'N/A')}</td>
                    <td>{result.get('response_time', 0):.3f}s</td>
                </tr>
"""
        
        html += """            </tbody>
        </table>
        
        <div class="footer">
            <p>This report was automatically generated by the Penetration Testing Toolkit.</p>
            <p>For authorized security testing only. Unauthorized access is illegal.</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(filepath, 'w') as f:
            f.write(html)
        
        return str(filepath)
    
    def generate_xml_report(self, filename: str = None) -> str:
        """Generate XML report"""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        
        filepath = self.output_dir / filename
        
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<report>\n'
        xml += f'  <generated_at>{datetime.now().isoformat()}</generated_at>\n'
        xml += f'  <total_results>{len(self.results)}</total_results>\n'
        xml += '  <results>\n'
        
        for result in self.results:
            xml += '    <result>\n'
            for key, value in result.items():
                xml += f'      <{key}>{value}</{key}>\n'
            xml += '    </result>\n'
        
        xml += '  </results>\n'
        xml += '</report>'
        
        with open(filepath, 'w') as f:
            f.write(xml)
        
        return str(filepath)
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary report"""
        return {
            'generated_at': datetime.now().isoformat(),
            'total_summaries': len(self.summaries),
            'summaries': [asdict(s) for s in self.summaries]
        }
    
    def clear_results(self):
        """Clear collected results"""
        self.results.clear()
        self.summaries.clear()
    
    def export_all_formats(self, prefix: str = None) -> List[str]:
        """Export to all supported formats"""
        if prefix is None:
            prefix = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        files = []
        
        # JSON always works (can be empty)
        try:
            files.append(self.generate_json_report(f"{prefix}.json"))
        except Exception as e:
            print(f"⚠️  Error generating JSON: {e}")
        
        # CSV requires data
        try:
            if self.results:
                files.append(self.generate_csv_report(f"{prefix}.csv"))
            else:
                print(f"⚠️  Skipping CSV: No results to export")
        except Exception as e:
            print(f"⚠️  Error generating CSV: {e}")
        
        # HTML always works (shows empty state)
        try:
            files.append(self.generate_html_report(f"{prefix}.html"))
        except Exception as e:
            print(f"⚠️  Error generating HTML: {e}")
        
        # XML always works (can be empty)
        try:
            files.append(self.generate_xml_report(f"{prefix}.xml"))
        except Exception as e:
            print(f"⚠️  Error generating XML: {e}")
        
        return files
