"""Installer module for pi-netconfig service.

Handles self-installation including systemd service creation, directory setup,
and initial configuration with venv-based package deployment.

Design: workspace/design/design-0001-installer.md
Requirements: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007
              NFR-007 (thread safety), NFR-008 (error logging)
Traceability: workspace/trace/trace-0001-requirements-traceability-matrix.md

Copyright (c) 2025 William Watson. Licensed under the MIT License.
"""

import argparse
import os
import subprocess
import sys
from logging import getLogger
from pathlib import Path

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


class VenvDetector:
    """Validate virtual environment execution context and package installation."""

    @staticmethod
    def is_venv() -> bool:
        """Check if running inside a virtual environment.

        Returns:
            bool: True if running in venv, False otherwise.
        """
        is_venv = sys.prefix != sys.base_prefix
        logger.debug(f"Virtual environment check: {is_venv} (prefix={sys.prefix}, base_prefix={sys.base_prefix})")
        return is_venv

    @staticmethod
    def get_venv_python() -> Path:
        """Get absolute path to the venv Python interpreter.

        Returns:
            Path: Absolute path to Python executable.
        """
        python_path = Path(sys.executable)
        logger.debug(f"Venv Python path: {python_path}")
        return python_path

    @staticmethod
    def validate_package_installed() -> bool:
        """Verify that pi_netconfig package is importable.

        Returns:
            bool: True if package can be imported, False otherwise.
        """
        try:
            import pi_netconfig
            logger.debug("Package pi_netconfig successfully imported")
            return True
        except ImportError as e:
            logger.debug(f"Package pi_netconfig not importable: {e}")
            return False


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
            - /etc/pi-netconfig/
            - /var/log/

        Raises:
            FileSystemError: If directory creation fails.
        """
        directories = [
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
    def generate_venv_systemd_unit(venv_python: Path) -> str:
        """Generate systemd unit file content with venv Python path.

        Args:
            venv_python: Absolute path to venv Python interpreter.

        Returns:
            str: Complete systemd unit file content.
        """
        unit_content = f"""[Unit]
Description=Pi Network Configuration Service
After=network.target
Wants=network.target

[Service]
Type=simple
ExecStart={venv_python} -m pi_netconfig.main
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
User=root

[Install]
WantedBy=multi-user.target
"""
        logger.debug(f"Generated systemd unit file content with venv Python: {venv_python}")
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
        """Remove created service file (best-effort).

        Logs warnings for cleanup failures but does not raise exceptions.
        """
        logger.warning("Rollback initiated")

        service_path = '/etc/systemd/system/pi-netconfig.service'

        try:
            logger.debug(f"Attempting to remove: {service_path}")
            if os.path.exists(service_path):
                os.remove(service_path)
                logger.debug(f"Removed file: {service_path}")
        except Exception as e:
            logger.warning(f"Rollback cleanup failed for {service_path}: {e}")


def install() -> bool:
    """Main installation entry point.

    Coordinates installation detection, privilege verification, venv validation,
    and installation steps. Performs rollback on failure.

    Returns:
        bool: True if installation successful, False otherwise.

    Raises:
        PrivilegeError: If not running as root.
        InstallerError: If not running in venv or package not installed.
    """
    try:
        logger.info("Installation started")

        # Check if already installed
        if InstallationDetector.is_service_installed():
            logger.info("Service already installed, skipping installation")
            return True

        # Verify privileges
        SystemdInstaller.verify_root_privileges()

        # Validate venv context
        if not VenvDetector.is_venv():
            error_msg = "Installation must be run from within a virtual environment. Please activate venv and retry."
            print(error_msg, file=sys.stderr)
            logger.error(error_msg)
            raise InstallerError(error_msg)

        # Validate package installed
        if not VenvDetector.validate_package_installed():
            error_msg = "Package pi_netconfig is not installed in the current environment. Please pip install the package and retry."
            print(error_msg, file=sys.stderr)
            logger.error(error_msg)
            raise InstallerError(error_msg)

        # Get venv Python path
        venv_python = VenvDetector.get_venv_python()

        # Execute installation steps
        SystemdInstaller.create_directories()
        unit_content = SystemdInstaller.generate_venv_systemd_unit(venv_python)
        SystemdInstaller.install_systemd_unit(unit_content)
        SystemdInstaller.enable_and_start_service()

        logger.info("Installation successful")
        return True

    except PrivilegeError:
        # Already logged and printed, don't rollback
        return False
    except InstallerError:
        # Venv or package validation error, don't rollback
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
# when service not detected. Expects root privileges and venv execution context.
# Returns bool for success/failure.


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Pi-Netconfig installer - systemd service installation'
    )
    parser.add_argument('--install', action='store_true', required=True,
                        help='Execute installation')
    parser.add_argument('--systemd-mode', action='store_true', required=True,
                        help='Install as systemd service')
    
    args = parser.parse_args()
    
    try:
        result = install()
        if result:
            print('Installation complete. Service enabled and started.')
            sys.exit(0)
        else:
            print('Installation failed. See errors above.')
            sys.exit(1)
    except Exception as e:
        print(f'Installation failed: {e}')
        sys.exit(1)
