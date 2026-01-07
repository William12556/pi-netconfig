"""ConnectionManager Module

WiFi client mode connection management including scanning, configuration, and
connectivity testing.

Design: workspace/design/design-0003-connectionmanager.md
Requirements: FR-012, FR-030, FR-031, FR-032, FR-033, FR-034, FR-060, FR-061, FR-062
              NFR-007 (thread safety), NFR-008 (error logging)
Traceability: workspace/trace/trace-0001-requirements-traceability-matrix.md

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
"""

import subprocess
import socket
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict
import logging
from datetime import datetime
import threading

@dataclass
class NetworkInfo:
    ssid: str
    signal_strength: int
    security: str
    frequency: str

class ConnectionManagerError(Exception):
    pass

class ConfigurationError(ConnectionManagerError):
    pass

class NetworkScanError(ConnectionManagerError):
    pass

logger = logging.getLogger('ConnectionManager')

class ConnectionTester:
    @staticmethod
    def test_connection() -> bool:
        for host in ['8.8.8.8', '1.1.1.1']:
            try:
                socket.create_connection((host, 53), timeout=1)
                return True
            except socket.error:
                pass
        return False

class NetworkScanner:
    @staticmethod
    def scan_networks() -> List[Dict[str, str]]:
        """Scan available WiFi networks.
        
        Returns:
            List[Dict]: List of network dictionaries with ssid, signal, security
        """
        try:
            output = subprocess.check_output(
                ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi', 'list'],
                stderr=subprocess.DEVNULL
            )
            networks = []
            seen_ssids = set()
            
            for line in output.decode().splitlines():
                parts = line.strip().split(':')
                if len(parts) >= 3:
                    ssid = parts[0]
                    signal = parts[1]
                    security = parts[2] if parts[2] else 'Open'
                    
                    # Skip duplicates and empty SSIDs
                    if ssid and ssid not in seen_ssids:
                        seen_ssids.add(ssid)
                        networks.append({
                            'ssid': ssid,
                            'signal': signal,
                            'security': security
                        })
            
            # Sort by signal strength (descending)
            networks.sort(key=lambda x: int(x['signal']), reverse=True)
            return networks
            
        except subprocess.CalledProcessError as e:
            logger.error(f'Failed to scan networks: {e}', exc_info=True)
            raise NetworkScanError('Failed to scan networks') from e
    
    @staticmethod
    def get_current_ssid() -> Optional[str]:
        """Get currently connected network SSID.
        
        Returns:
            Optional[str]: Connected SSID or None if not connected
        """
        try:
            output = subprocess.check_output(
                ['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi'],
                stderr=subprocess.DEVNULL
            )
            
            for line in output.decode().splitlines():
                parts = line.strip().split(':')
                if len(parts) >= 2 and parts[0] == 'yes':
                    return parts[1]
            
            return None
            
        except subprocess.CalledProcessError as e:
            logger.warning(f'Failed to get current SSID: {e}')
            return None

class ConfigManager:
    CONFIG_PATH = Path('/etc/pi-netconfig/config.json')
    _lock = threading.Lock()

    @staticmethod
    def configure_network(ssid: str, password: str) -> bool:
        with ConfigManager._lock:
            if not (1 <= len(ssid) <= 32) or any(c in ssid for c in ';,&|$`\\\'"'):
                raise ConfigurationError('Invalid SSID')
            if not (8 <= len(password) <= 63):
                raise ConfigurationError('Invalid password')
            try:
                subprocess.run(['nmcli', 'con', 'delete', 'id', ssid], check=False)
                subprocess.run(['nmcli', 'con', 'add', 'type', 'wifi', 'ssid', ssid, 'wifi-sec.key-mgmt', 'wpa-psk', 'wifi-sec.psk', password], check=True)
                subprocess.run(['nmcli', 'con', 'up', 'id', ssid], check=True)
                ConfigManager.persist_configuration(ssid)
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f'Failed to configure network: {e}', exc_info=True)
                raise ConfigurationError('Failed to configure network') from e

    @staticmethod
    def persist_configuration(ssid: str):
        with ConfigManager._lock:
            config = {'configured_ssid': ssid, 'last_connected': datetime.now().isoformat(), 'ap_password': 'piconfig123'}
            ConfigManager.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(ConfigManager.CONFIG_PATH, 'w') as f:
                json.dump(config, f)

    @staticmethod
    def load_configuration() -> Optional[str]:
        with ConfigManager._lock:
            if ConfigManager.CONFIG_PATH.exists():
                with open(ConfigManager.CONFIG_PATH) as f:
                    config = json.load(f)
                return config['configured_ssid']
            return None

class ConnectionManager:
    """Facade class providing unified interface to connection management.
    
    Coordinates ConnectionTester, NetworkScanner, and ConfigManager to provide
    the interface expected by StateMonitor and other consumers.
    """
    
    def __init__(self):
        """Initialize ConnectionManager facade."""
        self._tester = ConnectionTester()
        self._scanner = NetworkScanner()
        self._config = ConfigManager()
        logger.debug('ConnectionManager initialized')
    
    async def test_connection(self) -> bool:
        """Test active internet connectivity.
        
        Returns:
            bool: True if internet connection is active
            
        Raises:
            ConnectionManagerError: On critical connectivity test failure
        """
        try:
            return self._tester.test_connection()
        except Exception as e:
            logger.error(f'Connection test failed: {e}', exc_info=True)
            raise ConnectionManagerError('Connection test failed') from e
    
    def scan_networks(self) -> List[Dict[str, str]]:
        """Scan for available WiFi networks.
        
        Returns:
            List[Dict]: Available networks sorted by signal strength
            
        Raises:
            NetworkScanError: On network scan failure
        """
        try:
            return self._scanner.scan_networks()
        except NetworkScanError:
            raise
        except Exception as e:
            logger.error(f'Network scan failed: {e}', exc_info=True)
            raise NetworkScanError('Network scan failed') from e
    
    def get_current_ssid(self) -> Optional[str]:
        """Get currently connected network SSID.
        
        Returns:
            Optional[str]: Connected SSID or None if not connected
        """
        try:
            return self._scanner.get_current_ssid()
        except Exception as e:
            logger.warning(f'Failed to get current SSID: {e}')
            return None
    
    def configure_network(self, ssid: str, password: str) -> bool:
        """Configure and activate WiFi connection.
        
        Args:
            ssid: Target network SSID
            password: Network password
            
        Returns:
            bool: True if configuration successful
            
        Raises:
            ConfigurationError: On validation or configuration failure
        """
        try:
            return self._config.configure_network(ssid, password)
        except ConfigurationError:
            raise
        except Exception as e:
            logger.error(f'Network configuration failed: {e}', exc_info=True)
            raise ConfigurationError('Network configuration failed') from e
    
    def load_configuration(self) -> Optional[str]:
        """Load last configured network SSID.
        
        Returns:
            Optional[str]: Configured SSID or None if not configured
            
        Raises:
            ConnectionManagerError: On configuration load failure
        """
        try:
            return self._config.load_configuration()
        except Exception as e:
            logger.error(f'Configuration load failed: {e}', exc_info=True)
            raise ConnectionManagerError('Configuration load failed') from e
