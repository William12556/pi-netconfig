import subprocess
import socket
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
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
    def scan_networks() -> List[NetworkInfo]:
        try:
            output = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY,FREQ', 'dev', 'wifi', 'list'])
            networks = []
            for line in output.decode().splitlines():
                ssid, signal_strength, security, frequency = line.strip().split(':')
                networks.append(NetworkInfo(ssid, int(signal_strength), security, frequency))
            networks = list({n.ssid: n for n in networks}.values())
            return sorted(networks, key=lambda x: x.signal_strength, reverse=True)
        except subprocess.CalledProcessError as e:
            logger.error(f'Failed to scan networks: {e}', exc_info=True)
            raise NetworkScanError('Failed to scan networks') from e

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
