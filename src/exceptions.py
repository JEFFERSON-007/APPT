"""
Enterprise-Grade Exception Handling and Logging Module
Implements best practices for error handling, retry logic, and audit logging
"""

import logging
import logging.handlers
import sys
import time
import functools
import traceback
from typing import Any, Callable, Optional, Dict, Tuple
from pathlib import Path
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    AUDIT = 25  # Custom level between WARNING and ERROR


class EnterpriseLogger:
    """
    Enterprise-grade logging with:
    - Multiple handlers (console, file, audit)
    - Structured logging
    - Sensitive data masking
    - Log rotation
    - Audit trail
    """
    
    def __init__(
        self,
        name: str = "toolkit",
        log_dir: Path = Path("./logs"),
        console_level: LogLevel = LogLevel.INFO,
        file_level: LogLevel = LogLevel.DEBUG,
        audit_log: bool = True
    ):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create main logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Add custom audit level
        logging.addLevelName(LogLevel.AUDIT.value, "AUDIT")
        self.logger.audit = functools.partial(
            self.logger.log, LogLevel.AUDIT.value
        )
        
        # Console handler
        self._add_console_handler(console_level)
        
        # File handlers with rotation
        self._add_file_handlers(file_level, audit_log)
    
    def _add_console_handler(self, level: LogLevel):
        """Add console handler with colored output"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level.value)
        
        # Color codes
        colors = {
            logging.DEBUG: '\033[36m',      # Cyan
            logging.INFO: '\033[92m',       # Green
            logging.WARNING: '\033[93m',    # Yellow
            logging.ERROR: '\033[91m',      # Red
            logging.CRITICAL: '\033[95m',   # Magenta
            LogLevel.AUDIT.value: '\033[94m'  # Blue
        }
        reset = '\033[0m'
        
        class ColorFormatter(logging.Formatter):
            def format(self, record):
                color = colors.get(record.levelno, '')
                record.levelname = f"{color}{record.levelname}{reset}"
                return super().format(record)
        
        formatter = ColorFormatter(
            '[%(asctime)s] %(levelname)-10s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _add_file_handlers(self, level: LogLevel, audit_log: bool):
        """Add file handlers with rotation"""
        # Main log file
        log_file = self.log_dir / f"{self.name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(level.value)
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(file_handler)
        
        # Audit log file
        if audit_log:
            audit_file = self.log_dir / f"{self.name}_audit.log"
            audit_handler = logging.handlers.RotatingFileHandler(
                audit_file,
                maxBytes=10*1024*1024,
                backupCount=10
            )
            audit_handler.setLevel(LogLevel.AUDIT.value)
            audit_handler.setFormatter(logging.Formatter(
                '[%(asctime)s] AUDIT | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            self.logger.addHandler(audit_handler)
    
    def audit_log(self, action: str, target: str, result: str, **metadata):
        """Log security-relevant actions"""
        msg = f"ACTION={action} | TARGET={target} | RESULT={result}"
        for key, value in metadata.items():
            msg += f" | {key}={value}"
        self.logger.audit(msg)
    
    def mask_sensitive(self, text: str, keywords: list = None) -> str:
        """Mask sensitive data in logs"""
        if keywords is None:
            keywords = ['password', 'secret', 'token', 'key', 'passwd']
        
        for keyword in keywords:
            # Replace anything that looks like a password after this keyword
            import re
            pattern = f"({keyword})[=:'\"]?([^\\s,)'\"]*)"
            text = re.sub(pattern, r"\1=***REDACTED***", text, flags=re.IGNORECASE)
        
        return text


class RetryConfig:
    """Configuration for retry behavior"""
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter


def retry_on_exception(
    config: RetryConfig = None,
    exceptions: Tuple = (Exception,),
    logger: EnterpriseLogger = None
):
    """
    Decorator for retry logic with exponential backoff
    
    Usage:
        @retry_on_exception(
            config=RetryConfig(max_attempts=3),
            exceptions=(ConnectionError, TimeoutError),
            logger=logger
        )
        def attempt_login(host, user, password):
            ...
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            delay = config.initial_delay
            
            while attempt < config.max_attempts:
                try:
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    attempt += 1
                    
                    if attempt >= config.max_attempts:
                        if logger:
                            logger.logger.error(
                                f"Failed after {config.max_attempts} attempts: {str(e)}"
                            )
                        raise
                    
                    # Calculate next delay with jitter
                    next_delay = delay * config.backoff_factor
                    next_delay = min(next_delay, config.max_delay)
                    
                    if config.jitter:
                        import random
                        next_delay *= (0.5 + random.random())
                    
                    if logger:
                        logger.logger.warning(
                            f"Attempt {attempt} failed: {str(e)}. "
                            f"Retrying in {next_delay:.1f}s..."
                        )
                    
                    time.sleep(next_delay)
                    delay = next_delay
        
        return wrapper
    return decorator


class SecurityException(Exception):
    """Base exception for security-related errors"""
    pass


class InvalidInputException(SecurityException):
    """Raised when input validation fails"""
    pass


class TargetTimeoutException(SecurityException):
    """Raised when target connection times out"""
    pass


class AuthenticationException(SecurityException):
    """Raised when authentication fails"""
    pass


class ServiceException(SecurityException):
    """Raised when service unavailable"""
    pass


class ValidationError(SecurityException):
    """Raised when validation fails"""
    pass


def safe_execute(
    func: Callable,
    logger: EnterpriseLogger = None,
    default_return: Any = None,
    raise_exception: bool = False
) -> Any:
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        logger: Logger instance for error logging
        default_return: Value to return on exception
        raise_exception: Re-raise exception after logging
    
    Returns:
        Function result or default_return
    """
    try:
        return func()
    except Exception as e:
        if logger:
            logger.logger.error(
                f"Error executing {func.__name__}: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
        
        if raise_exception:
            raise
        
        return default_return
