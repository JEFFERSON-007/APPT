#!/usr/bin/env python3
"""
Test Suite and Examples
Demonstrates proper usage of the toolkit with enterprise patterns
"""

import unittest
from pathlib import Path
from src.exceptions import (
    EnterpriseLogger, RetryConfig, retry_on_exception,
    InvalidInputException, TargetTimeoutException
)
from src.config_manager import (
    ConfigManager, ToolkitConfig, ScannerConfig, BruteForceConfig,
    ProtocolType, AttackModeType
)
from src.reporting import ReportGenerator, ScanResult, CredentialResult, ResultStatus


class TestExceptionHandling(unittest.TestCase):
    """Test exception handling and logging"""
    
    def setUp(self):
        self.logger = EnterpriseLogger(name="test_toolkit")
    
    def test_logger_creation(self):
        """Test logger creation"""
        self.assertIsNotNone(self.logger.logger)
    
    def test_sensitive_data_masking(self):
        """Test sensitive data masking"""
        text = "password=secretpass user=admin"
        masked = self.logger.mask_sensitive(text)
        self.assertIn("REDACTED", masked)
        self.assertNotIn("secretpass", masked)
    
    def test_audit_logging(self):
        """Test audit logging"""
        self.logger.audit_log(
            action="BRUTE_FORCE_ATTEMPT",
            target="192.168.1.100",
            result="FAILED",
            username="admin",
            attempts=100
        )


class TestConfigManagement(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        self.config_dir = Path("./test_config")
        self.config_dir.mkdir(exist_ok=True)
        self.manager = ConfigManager(self.config_dir)
    
    def test_config_creation(self):
        """Test creating default configuration"""
        config = ToolkitConfig()
        self.assertIsNotNone(config.scanner)
        self.assertIsNotNone(config.brute_force)
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = ToolkitConfig()
        config.scanner.threads = -1  # Invalid
        
        errors = self.manager.validate_config(config)
        self.assertTrue(len(errors) > 0)
    
    def test_config_serialization(self):
        """Test config to dict conversion"""
        config = ToolkitConfig()
        config_dict = config.to_dict()
        
        self.assertIn('scanner', config_dict)
        self.assertIn('brute_force', config_dict)
        self.assertIn('logging', config_dict)
    
    def tearDown(self):
        import shutil
        if self.config_dir.exists():
            shutil.rmtree(self.config_dir)


class TestReporting(unittest.TestCase):
    """Test reporting functionality"""
    
    def setUp(self):
        self.output_dir = Path("./test_output")
        self.output_dir.mkdir(exist_ok=True)
        self.reporter = ReportGenerator(self.output_dir)
    
    def test_add_scan_result(self):
        """Test adding scan result"""
        result = ScanResult(
            target="192.168.1.1",
            port=22,
            service="SSH",
            version="OpenSSH_7.4"
        )
        self.reporter.add_scan_result(result)
        self.assertEqual(len(self.reporter.results), 1)
    
    def test_add_credential_result(self):
        """Test adding credential result"""
        result = CredentialResult(
            target="192.168.1.100",
            username="admin",
            password="password123",
            protocol="ssh",
            status=ResultStatus.SUCCESS
        )
        self.reporter.add_credential_result(result)
        self.assertEqual(len(self.reporter.results), 1)
    
    def test_json_report_generation(self):
        """Test JSON report generation"""
        result = ScanResult(
            target="192.168.1.1",
            port=22,
            service="SSH"
        )
        self.reporter.add_scan_result(result)
        
        filepath = self.reporter.generate_json_report("test_report.json")
        self.assertTrue(Path(filepath).exists())
    
    def tearDown(self):
        import shutil
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)


class ExampleUsage:
    """Example usage patterns for enterprise deployment"""
    
    @staticmethod
    def example_quick_scan():
        """Example: Quick reconnaissance scan"""
        print("\n=== Example 1: Quick Reconnaissance Scan ===\n")
        
        config = ToolkitConfig(
            scanner=ScannerConfig(
                quick_mode=True,
                threads=10,
                timeout=2.0,
                output_format="json"
            ),
            logging=LoggingConfig(level="INFO")
        )
        
        print(f"✓ Configured scanner with {config.scanner.threads} threads")
        print(f"✓ Quick mode: {config.scanner.quick_mode}")
        print(f"✓ Output format: {config.scanner.output_format}")
    
    @staticmethod
    def example_secure_bruteforce():
        """Example: Secure brute force with proper error handling"""
        print("\n=== Example 2: Secure Brute Force Attack ===\n")
        
        config = ToolkitConfig(
            brute_force=BruteForceConfig(
                protocol=ProtocolType.SSH,
                attack_mode=AttackModeType.LOOP,
                threads=5,
                delay=1.0,  # 1 second between attempts
                max_retries=3,
                stop_on_success=True
            )
        )
        
        print(f"✓ Protocol: {config.brute_force.protocol.value}")
        print(f"✓ Attack mode: {config.brute_force.attack_mode.value}")
        print(f"✓ Delay: {config.brute_force.delay}s (stealth)")
        print(f"✓ Retries: {config.brute_force.max_retries}")
    
    @staticmethod
    def example_with_logging():
        """Example: Proper logging and error handling"""
        print("\n=== Example 3: Enterprise Logging ===\n")
        
        logger = EnterpriseLogger(
            name="pentest_toolkit",
            log_dir=Path("./logs"),
            console_level=LogLevel.INFO,
            file_level=LogLevel.DEBUG,
            audit_log=True
        )
        
        logger.logger.info("Scan initiated")
        logger.audit_log(
            action="PORT_SCAN",
            target="192.168.1.0/24",
            result="SUCCESS",
            ports_scanned=1000
        )
        logger.logger.warning("High-risk finding: Open admin panel detected")
        
        print("✓ Logging configured with:")
        print("  - Console output (INFO level)")
        print("  - File logging (DEBUG level)")
        print("  - Audit trail (security events)")
    
    @staticmethod
    def example_report_generation():
        """Example: Generate comprehensive reports"""
        print("\n=== Example 4: Report Generation ===\n")
        
        reporter = ReportGenerator(Path("./output"))
        
        # Simulate scan results
        for port in [22, 80, 443, 3306]:
            result = ScanResult(
                target="192.168.1.100",
                port=port,
                service=["SSH", "HTTP", "HTTPS", "MySQL"][port // 80] if port != 3306 else "MySQL",
                status="open"
            )
            reporter.add_scan_result(result)
        
        # Generate reports in multiple formats
        files = reporter.export_all_formats("example_report")
        print(f"✓ Generated {len(files)} reports:")
        for f in files:
            print(f"  - {f}")
    
    @staticmethod
    def example_profile_management():
        """Example: Configuration profile management"""
        print("\n=== Example 5: Profile Management ===\n")
        
        manager = ConfigManager(Path("./config"))
        
        # Create example profiles
        print("✓ Creating example profiles...")
        manager.create_default_profiles()
        
        print("\n✓ Available profiles:")
        profiles = ['quick_scan', 'thorough_scan', 'ssh_bruteforce', 
                   'web_bruteforce', 'stealth_mode']
        for profile in profiles:
            print(f"  - {profile}")
        
        print("\n✓ Load profile with:")
        print("  config = manager.load_profile('ssh_bruteforce')")


if __name__ == '__main__':
    import sys
    from src.exceptions import LogLevel
    from src.config_manager import LoggingConfig
    
    # Run tests
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        unittest.main(argv=[''], exit=False)
    
    # Run examples
    print("\n" + "="*60)
    print("ENTERPRISE PENETRATION TESTING TOOLKIT - EXAMPLES")
    print("="*60)
    
    ExampleUsage.example_quick_scan()
    ExampleUsage.example_secure_bruteforce()
    ExampleUsage.example_with_logging()
    ExampleUsage.example_report_generation()
    ExampleUsage.example_profile_management()
    
    print("\n" + "="*60)
    print("For unit tests, run: python examples.py test")
    print("="*60 + "\n")
