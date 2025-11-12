"""Installer module for pi-netconfig service.

Handles self-installation including systemd service creation, directory setup,
and initial configuration.
"""

import os
import shutil
import subprocess
import sys
from logging import getLogger
from pathlib import Path
from typing import Optional

logger = getLogger('Installer')


class InstallerError(Exception):
    """Base exception for installer operations."""
    pass


class PrivilegeError(InstallerError):
    """Insufficient privileges for installation."""
    pass


class FileSystemError(InstallerError):
    """Directory or file operation failure."""
    pass


class SystemdError(InstallerError):
    """Systemd command execution failure."""
    pass


class InstallationDetector:
    """Check for existing systemd service installation."""
    
    @staticmethod
    def is_service_installed() -> bool:
        """Check if systemd service file exists.
        
        Returns:
            bool: True if service file exists, False otherwise.
        """
        service_path = Path('/etc/systemd/system/pi-netconfig.service')
        exists = service_path.exists()
        logger.debug(f"Service file exists check: {exists}")
        return exists
    
    @staticmethod
    def get_current_script_path() -> Path:
        """Get absolute path of currently executing script.
        
        Returns:
            Path: Absolute path to current script.
        """
        script_path = Path(__file__).resolve()
        logger.debug(f"Current script path: {script_path}")
        return script_path


class SystemdInstaller:
    """Perform installation steps and systemd configuration."""
    
    @staticmethod
    def verify_root_privileges() -> bool:
        """Verify running as root user.
        
        Returns:
            bool: True if running as root (UID 0).
            
        Raises:
            PrivilegeError: If not running as root.
        """
        is_root = os.geteuid() == 0
        logger.debug(f"Root privilege check: {is_root}")
        if not is_root:
            print("Installation requires root privileges. Run with sudo.", file=sys.stderr)
            raise PrivilegeError("Installation requires root privileges. Run with sudo.")
        return True
    
    @staticmethod
    def create_directories() -> None:
        """Create required installation directories.
        
        Creates:
            - /usr/local/bin/pi-netconfig/
            - /etc/pi-netconfig/
            - /var/log/
            
        Raises:
            FileSystemError: If directory creation fails.
        """
        directories = [
            '/usr/local/bin/pi-netconfig',
            '/etc/pi-netconfig',
            '/var/log'
        ]
        
        for dir_path in directories:
            try:
                logger.debug(f"Creating directory: {dir_path}")
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                os.chmod(dir_path, 0o755)
                logger.debug(f"Directory created with 755 permissions: {dir_path}")
            except Exception as e:
                logger.error(f"Failed to create directory {dir_path}: {e}", exc_info=True)
                raise FileSystemError(f"Failed to create directory {dir_path}: {e}")
    
    @staticmethod
    def copy_application(script_path: Path) -> None:
        """Copy application script to installation location.
        
        Args:
            script_path: Path to source script file.
            
        Raises:
            FileSystemError: If copy operation fails.
        """
        dest_path = '/usr/local/bin/pi-netconfig/main.py'
        try:
            logger.debug(f"Copying {script_path} to {dest_path}")
            shutil.copy2(script_path, dest_path)
            os.chmod(dest_path, 0o755)
            logger.info(f"Application copied to {dest_path}")
        except Exception as e:
            logger.error(f"Failed to copy application: {e}", exc_info=True)
            raise FileSystemError(f"Failed to copy application: {e}")
    
    @staticmethod
    def generate_systemd_unit() -> str:
        """Generate systemd unit file content.
        
        Returns:
            str: Complete systemd unit file content.
        """
        unit_content = """[Unit]
Description=Pi Network Configuration Service
After=network.target
Wants=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/local/bin/pi-netconfig/main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
User=root

[Install]
WantedBy=multi-user.target
"""
        logger.debug("Generated systemd unit file content")
        return unit_content
    
    @staticmethod
    def install_systemd_unit(unit_content: str) -> None:
        """Write unit file and reload systemd daemon.
        
        Args:
            unit_content: Systemd unit file content.
            
        Raises:
            SystemdError: If unit file write or daemon-reload fails.
        """
        unit_path = '/etc/systemd/system/pi-netconfig.service'
        try:
            logger.debug(f"Writing systemd unit file to {unit_path}")
            with open(unit_path, 'w') as f:
                f.write(unit_content)
            logger.info(f"Systemd unit file written to {unit_path}")
            
            logger.debug("Executing: systemctl daemon-reload")
            result = subprocess.run(
                ['systemctl', 'daemon-reload'],
                capture_output=True,
                text=True,
                check=True
            )
            logger.debug("systemctl daemon-reload completed")
        except subprocess.CalledProcessError as e:
            logger.error(f"systemctl daemon-reload failed: {e.stderr}", exc_info=True)
            raise SystemdError(f"systemctl daemon-reload failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Failed to install systemd unit: {e}", exc_info=True)
            raise SystemdError(f"Failed to install systemd unit: {e}")
    
    @staticmethod
    def enable_and_start_service() -> None:
        """Enable and start systemd service.
        
        Raises:
            SystemdError: If enable or start commands fail.
        """
        try:
            logger.debug("Executing: systemctl enable pi-netconfig")
            subprocess.run(
                ['systemctl', 'enable', 'pi-netconfig'],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Service enabled")
            
            logger.debug("Executing: systemctl start pi-netconfig")
            subprocess.run(
                ['systemctl', 'start', 'pi-netconfig'],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Service started")
        except subprocess.CalledProcessError as e:
            logger.error(f"systemctl command failed: {e.stderr}", exc_info=True)
            raise SystemdError(f"systemctl command failed: {e.stderr}")
    
    @staticmethod
    def rollback_installation() -> None:
        """Remove created files and directories (best-effort).
        
        Logs warnings for cleanup failures but does not raise exceptions.
        """
        logger.warning("Rollback initiated")
        
        paths_to_remove = [
            '/etc/systemd/system/pi-netconfig.service',
            '/usr/local/bin/pi-netconfig'
        ]
        
        for path in paths_to_remove:
            try:
                logger.debug(f"Attempting to remove: {path}")
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    logger.debug(f"Removed directory: {path}")
                elif os.path.exists(path):
                    os.remove(path)
                    logger.debug(f"Removed file: {path}")
            except Exception as e:
                logger.warning(f"Rollback cleanup failed for {path}: {e}")


def install() -> bool:
    """Main installation entry point.
    
    Coordinates installation detection, privilege verification, and
    installation steps. Performs rollback on failure.
    
    Returns:
        bool: True if installation successful, False otherwise.
    """
    try:
        logger.info("Installation started")
        
        # Check if already installed
        if InstallationDetector.is_service_installed():
            logger.info("Service already installed, skipping installation")
            return True
        
        # Verify privileges
        SystemdInstaller.verify_root_privileges()
        
        # Execute installation steps
        SystemdInstaller.create_directories()
        script_path = InstallationDetector.get_current_script_path()
        SystemdInstaller.copy_application(script_path)
        unit_content = SystemdInstaller.generate_systemd_unit()
        SystemdInstaller.install_systemd_unit(unit_content)
        SystemdInstaller.enable_and_start_service()
        
        logger.info("Installation successful")
        return True
        
    except PrivilegeError:
        # Already logged and printed, don't rollback
        return False
    except (FileSystemError, SystemdError) as e:
        logger.error(f"Installation failed: {e}", exc_info=True)
        SystemdInstaller.rollback_installation()
        logger.critical("Installation failed after rollback")
        return False
    except Exception as e:
        logger.critical(f"Unexpected installation failure: {e}", exc_info=True)
        SystemdInstaller.rollback_installation()
        return False


# INTEGRATION: Import install() from installer module. Call from ServiceController 
# when service not detected. Expects root privileges. Returns bool for success/failure.
