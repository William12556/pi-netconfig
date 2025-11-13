import logging
import traceback
from subprocess import check_output, CalledProcessError

# Custom exceptions
class APManagerError(Exception):
    pass

class InterfaceDetectionError(APManagerError):
    pass

class APActivationError(APManagerError):
    pass

class ProfileCreationError(APManagerError):
    pass

# Logger setup
logger = logging.getLogger('APManager')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

class AccessPoint:
    """Manage local WiFi access point for network configuration."""

    def __init__(self):
        self.ap_active = False
        self.interface = self.get_wifi_interface()
        self.mac_address = self.get_mac_address()
        self.ssid = self.generate_ssid()
        self.profile_name = "pi-netconfig-ap"

    def get_wifi_interface(self) -> str:
        """Execute 'nmcli device status', find TYPE=wifi, return DEVICE name."""
        try:
            output = check_output(["nmcli", "device", "status"]).decode("utf-8")
            for line in output.splitlines():
                if "TYPE=wifi" in line:
                    return line.split()[0]
            raise InterfaceDetectionError("No WiFi interface found")
        except CalledProcessError as e:
            logger.error(f"Failed to get WiFi interface: {e}")
            traceback.print_exc()
            raise InterfaceDetectionError("Failed to get WiFi interface") from e
        except Exception as e:
            logger.critical(f"Unexpected error: {e}")
            traceback.print_exc()
            raise APManagerError("Unexpected error") from e

    def get_mac_address(self) -> str:
        """Execute 'nmcli device show {interface}', extract GENERAL.HWADDR."""
        try:
            output = check_output(["nmcli", "device", "show", self.interface]).decode("utf-8")
            for line in output.splitlines():
                if "GENERAL.HWADDR:" in line:
                    return line.split()[1]
            raise APManagerError("Failed to get MAC address")
        except CalledProcessError as e:
            logger.error(f"Failed to get MAC address: {e}")
            traceback.print_exc()
            raise APManagerError("Failed to get MAC address") from e
        except Exception as e:
            logger.critical(f"Unexpected error: {e}")
            traceback.print_exc()
            raise APManagerError("Unexpected error") from e

    def generate_ssid(self) -> str:
        """Format "PiConfig-{last_4_hex}" from MAC address."""
        return f"PiConfig-{self.mac_address[-4:]}"

    def create_ap_profile(self) -> None:
        """Execute nmcli commands to create AP profile with WPA2-PSK."""
        try:
            check_output(["nmcli", "con", "add", "type", "wifi", "ifname", self.interface,
                          "con-name", self.profile_name, "mode", "ap", "ssid", self.ssid])
            check_output(["nmcli", "con", "modify", self.profile_name,
                          "802-11-wireless-security.key-mgmt", "wpa-psk"])
            check_output(["nmcli", "con", "modify", self.profile_name,
                          "802-11-wireless-security.psk", "piconfig123"])
            check_output(["nmcli", "con", "modify", self.profile_name,
                          "ipv4.method", "shared", "ipv4.addresses", "192.168.50.1/24"])
            logger.info("AP profile created successfully")
        except CalledProcessError as e:
            logger.error(f"Failed to create AP profile: {e}")
            traceback.print_exc()
            raise ProfileCreationError("Failed to create AP profile") from e
        except Exception as e:
            logger.critical(f"Unexpected error: {e}")
            traceback.print_exc()
            raise APManagerError("Unexpected error") from e

    def activate_ap(self) -> bool:
        """Execute 'nmcli con up id pi-netconfig-ap', set ap_active=True."""
        try:
            check_output(["nmcli", "con", "up", "id", self.profile_name])
            self.ap_active = True
            logger.info("Access point activated successfully")
        except CalledProcessError as e:
            logger.error(f"Failed to activate access point: {e}")
            traceback.print_exc()
            raise APActivationError("Failed to activate access point") from e
        except Exception as e:
            logger.critical(f"Unexpected error: {e}")
            traceback.print_exc()
            raise APManagerError("Unexpected error") from e
        return self.ap_active

    def deactivate_ap(self) -> None:
        """Execute 'nmcli con down id pi-netconfig-ap', set ap_active=False."""
        try:
            check_output(["nmcli", "con", "down", "id", self.profile_name])
            self.ap_active = False
            logger.info("Access point deactivated successfully")
        except CalledProcessError as e:
            logger.error(f"Failed to deactivate access point: {e}")
            traceback.print_exc()
        except Exception as e:
            logger.critical(f"Unexpected error: {e}")
            traceback.print_exc()

    def fallback_to_open_ap(self) -> bool:
        """Remove security, create open network."""
        try:
            check_output(["nmcli", "con", "modify", self.profile_name,
                          "802-11-wireless-security.key-mgmt", ""])
            logger.warning("Fallback to open access point")
        except CalledProcessError as e:
            logger.error(f"Failed to fallback to open access point: {e}")
            traceback.print_exc()
        except Exception as e:
            logger.critical(f"Unexpected error: {e}")
            traceback.print_exc()
        return self.ap_active

    def is_active(self) -> bool:
        """Return ap_active state."""
        return self.ap_active

# Public functions
def activate_ap() -> bool:
    """Create AccessPoint instance, activate."""
    ap = AccessPoint()
    try:
        ap.create_ap_profile()
        return ap.activate_ap()
    except ProfileCreationError:
        return ap.fallback_to_open_ap()
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        traceback.print_exc()
        raise APManagerError("Unexpected error") from e

def deactivate_ap() -> None:
    """Create AccessPoint instance, deactivate."""
    ap = AccessPoint()
    ap.deactivate_ap()

def get_ap_ssid() -> str:
    """Get current AP SSID."""
    ap = AccessPoint()
    return ap.ssid

def is_active() -> bool:
    """Check if access point is active."""
    ap = AccessPoint()
    return ap.is_active()
