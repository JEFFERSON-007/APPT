"""
Enterprise Configuration Management System
Supports YAML profiles, environment variables, and runtime overrides
"""

import yaml
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum


class ProtocolType(Enum):
    """Supported protocols"""
    SSH = "ssh"
    FTP = "ftp"
    HTTP = "http"
    HTTPS = "https"
    TELNET = "telnet"
    MYSQL = "mysql"
    POSTGRES = "postgres"
    MONGODB = "mongodb"


class AttackModeType(Enum):
    """Attack modes"""
    SINGLE = "single"
    LOOP = "loop"
    COMBO = "combo"


@dataclass
class ScannerConfig:
    """Port scanner configuration"""
    timeout: float = 2.0
    threads: int = 10
    quick_mode: bool = False
    service_detection: bool = True
    os_detection: bool = False
    aggressive: bool = False
    
    # Ports to scan
    ports: str = "1-1000"
    exclude_ports: str = ""
    
    # Output
    output_format: str = "json"  # json, csv, xml, html
    output_file: Optional[str] = None


@dataclass
class BruteForceConfig:
    """Brute force configuration"""
    protocol: ProtocolType = ProtocolType.SSH
    timeout: float = 5.0
    threads: int = 10
    
    # Attack configuration
    attack_mode: AttackModeType = AttackModeType.LOOP
    delay: float = 0.1
    stop_on_success: bool = False
    
    # Wordlists
    usernames_file: Optional[str] = None
    passwords_file: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    
    # Retry and resilience
    max_retries: int = 3
    retry_delay: float = 1.0
    connection_pool_size: int = 10
    
    # Output
    output_format: str = "json"
    output_file: Optional[str] = None
    
    # Safety
    rate_limit: float = 0.1
    max_attempts: Optional[int] = None
    dry_run: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    console_level: str = "INFO"
    file_level: str = "DEBUG"
    log_dir: str = "./logs"
    enable_audit_log: bool = True
    log_file_size_mb: int = 10
    log_backup_count: int = 5


@dataclass
class ToolkitConfig:
    """Complete toolkit configuration"""
    scanner: ScannerConfig = field(default_factory=ScannerConfig)
    brute_force: BruteForceConfig = field(default_factory=BruteForceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # General settings
    verbose: bool = False
    dry_run: bool = False
    version: str = "2.1"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'scanner': asdict(self.scanner),
            'brute_force': asdict(self.brute_force),
            'logging': asdict(self.logging),
            'verbose': self.verbose,
            'dry_run': self.dry_run,
            'version': self.version
        }


class ConfigManager:
    """
    Enterprise configuration management
    
    Supports:
    - YAML profiles
    - JSON configs
    - Environment variables
    - Runtime overrides
    - Validation
    """
    
    def __init__(self, config_dir: Path = Path("./config")):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.default_config = ToolkitConfig()
    
    def load_profile(self, profile_name: str) -> ToolkitConfig:
        """Load a named configuration profile"""
        profile_file = self.config_dir / f"{profile_name}.yaml"
        
        if not profile_file.exists():
            raise FileNotFoundError(f"Profile not found: {profile_file}")
        
        with open(profile_file, 'r') as f:
            config_dict = yaml.safe_load(f) or {}
        
        return self._dict_to_config(config_dict)
    
    def load_from_env(self) -> ToolkitConfig:
        """Load configuration from environment variables"""
        config = ToolkitConfig()
        
        # Scanner settings
        if env_val := os.getenv('PTK_SCANNER_TIMEOUT'):
            config.scanner.timeout = float(env_val)
        if env_val := os.getenv('PTK_SCANNER_THREADS'):
            config.scanner.threads = int(env_val)
        
        # Brute force settings
        if env_val := os.getenv('PTK_BF_PROTOCOL'):
            config.brute_force.protocol = ProtocolType(env_val)
        if env_val := os.getenv('PTK_BF_THREADS'):
            config.brute_force.threads = int(env_val)
        
        # Logging
        if env_val := os.getenv('PTK_LOG_LEVEL'):
            config.logging.level = env_val
        
        return config
    
    def save_profile(self, profile_name: str, config: ToolkitConfig):
        """Save configuration as a profile"""
        profile_file = self.config_dir / f"{profile_name}.yaml"
        
        with open(profile_file, 'w') as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False)
    
    def create_default_profiles(self):
        """Create example profiles"""
        profiles = {
            'quick_scan': ToolkitConfig(
                scanner=ScannerConfig(quick_mode=True, threads=20)
            ),
            'thorough_scan': ToolkitConfig(
                scanner=ScannerConfig(
                    quick_mode=False,
                    aggressive=True,
                    service_detection=True,
                    threads=10
                )
            ),
            'ssh_bruteforce': ToolkitConfig(
                brute_force=BruteForceConfig(
                    protocol=ProtocolType.SSH,
                    attack_mode=AttackModeType.LOOP,
                    threads=5
                )
            ),
            'web_bruteforce': ToolkitConfig(
                brute_force=BruteForceConfig(
                    protocol=ProtocolType.HTTP,
                    attack_mode=AttackModeType.LOOP,
                    threads=10
                )
            ),
            'stealth_mode': ToolkitConfig(
                brute_force=BruteForceConfig(
                    delay=2.0,
                    threads=1,
                    rate_limit=0.5
                ),
                scanner=ScannerConfig(
                    timeout=5.0,
                    threads=1
                )
            )
        }
        
        for name, config in profiles.items():
            self.save_profile(name, config)
    
    def merge_configs(self, *configs: ToolkitConfig) -> ToolkitConfig:
        """Merge multiple configurations (later overrides earlier)"""
        result = ToolkitConfig()
        
        for config in configs:
            if config is None:
                continue
            
            # Merge scanner
            for key in ['timeout', 'threads', 'quick_mode', 'service_detection',
                        'os_detection', 'aggressive', 'ports', 'exclude_ports',
                        'output_format', 'output_file']:
                if hasattr(config.scanner, key):
                    setattr(result.scanner, key, getattr(config.scanner, key))
            
            # Merge brute force
            for key in ['protocol', 'timeout', 'threads', 'attack_mode', 'delay',
                        'stop_on_success', 'usernames_file', 'passwords_file',
                        'username', 'password', 'max_retries', 'retry_delay',
                        'connection_pool_size', 'output_format', 'output_file',
                        'rate_limit', 'max_attempts', 'dry_run']:
                if hasattr(config.brute_force, key):
                    setattr(result.brute_force, key, getattr(config.brute_force, key))
            
            # Merge logging
            for key in ['level', 'console_level', 'file_level', 'log_dir',
                        'enable_audit_log', 'log_file_size_mb', 'log_backup_count']:
                if hasattr(config.logging, key):
                    setattr(result.logging, key, getattr(config.logging, key))
            
            # Merge general
            result.verbose = config.verbose or result.verbose
            result.dry_run = config.dry_run or result.dry_run
        
        return result
    
    def validate_config(self, config: ToolkitConfig) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Scanner validation
        if config.scanner.threads < 1:
            errors.append("Scanner threads must be >= 1")
        if config.scanner.timeout <= 0:
            errors.append("Scanner timeout must be > 0")
        
        # Brute force validation
        if config.brute_force.threads < 1:
            errors.append("Brute force threads must be >= 1")
        if config.brute_force.timeout <= 0:
            errors.append("Brute force timeout must be > 0")
        if config.brute_force.delay < 0:
            errors.append("Brute force delay cannot be negative")
        
        # File validation
        if config.brute_force.usernames_file:
            if not Path(config.brute_force.usernames_file).exists():
                errors.append(f"Usernames file not found: {config.brute_force.usernames_file}")
        
        if config.brute_force.passwords_file:
            if not Path(config.brute_force.passwords_file).exists():
                errors.append(f"Passwords file not found: {config.brute_force.passwords_file}")
        
        return errors
    
    @staticmethod
    def _dict_to_config(config_dict: Dict[str, Any]) -> ToolkitConfig:
        """Convert dictionary to ToolkitConfig"""
        config = ToolkitConfig()
        
        if 'scanner' in config_dict:
            for key, value in config_dict['scanner'].items():
                if hasattr(config.scanner, key):
                    setattr(config.scanner, key, value)
        
        if 'brute_force' in config_dict:
            for key, value in config_dict['brute_force'].items():
                if key == 'protocol' and isinstance(value, str):
                    value = ProtocolType(value)
                elif key == 'attack_mode' and isinstance(value, str):
                    value = AttackModeType(value)
                if hasattr(config.brute_force, key):
                    setattr(config.brute_force, key, value)
        
        if 'logging' in config_dict:
            for key, value in config_dict['logging'].items():
                if hasattr(config.logging, key):
                    setattr(config.logging, key, value)
        
        config.verbose = config_dict.get('verbose', False)
        config.dry_run = config_dict.get('dry_run', False)
        
        return config
