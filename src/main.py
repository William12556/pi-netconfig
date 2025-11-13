#!/usr/bin/env python3
"""
Pi Network Configuration Tool - Service Controller

Application entry point managing execution mode detection, installer invocation,
logging configuration, and systemd service lifecycle.

Copyright (c) 2025 William Watson. Licensed under the MIT License.
"""

import asyncio
import logging
import os
import signal
import sys
import traceback
from pathlib import Path
from typing import Optional

from installer import Installer
from state_monitor import StateMonitor


# Exception hierarchy
class ServiceControllerError(Exception):
    """Base exception for ServiceController errors."""
    pass


class LoggingConfigurationError(ServiceControllerError):
    """Raised when logging cannot be configured."""
    pass


class PrivilegeError(ServiceControllerError):
    """Raised when insufficient privileges detected."""
    pass


# Global shutdown event
shutdown_event: Optional[asyncio.Event] = None
state_monitor: Optional[StateMonitor] = None
logger = logging.getLogger('ServiceController')


def detect_execution_mode() -> str:
    """
    Determine execution mode based on service file existence and environment.
    
    Returns:
        str: 'bootstrap' if service not installed
             'service' if running under systemd
             'manual' if service installed but not under systemd
    
    Execution Modes:
        - bootstrap: No service file exists, first-time setup needed
        - service: Service file exists, INVOCATION_ID set (systemd context)
        - manual: Service file exists, no INVOCATION_ID (manual execution)
    """
    try:
        logger.debug("Detecting execution mode")
        
        # Check if service is installed
        service_installed = Installer.is_service_installed()
        logger.debug(f"Service installed: {service_installed}")
        
        if not service_installed:
            logger.debug("Mode: bootstrap (service not installed)")
            return 'bootstrap'
        
        # Check if running under systemd
        invocation_id = os.environ.get('INVOCATION_ID')
        logger.debug(f"INVOCATION_ID: {invocation_id}")
        
        if invocation_id:
            logger.debug("Mode: service (systemd context)")
            return 'service'
        else:
            logger.debug("Mode: manual (service installed, not systemd)")
            return 'manual'
    
    except Exception as e:
        logger.error(f"Error detecting execution mode: {e}")
        logger.debug(traceback.format_exc())
        return 'manual'  # Safe fallback


def verify_root_privileges() -> bool:
    """
    Check if process is running with root privileges.
    
    Returns:
        bool: True if effective UID is 0 (root), False otherwise
    """
    try:
        is_root = os.geteuid() == 0
        logger.debug(f"Root privileges: {is_root} (UID: {os.geteuid()})")
        return is_root
    except Exception as e:
        logger.error(f"Error checking root privileges: {e}")
        logger.debug(traceback.format_exc())
        return False


def configure_logging(mode: str) -> None:
    """
    Configure logging infrastructure.
    
    Args:
        mode: Execution mode ('bootstrap', 'service', 'manual')
    
    Raises:
        LoggingConfigurationError: If log file cannot be created/written
    
    Configuration:
        - File handler: /var/log/pi-netconfig.log (INFO level)
        - Console handler: stdout (DEBUG level, manual mode only)
        - Format: timestamp - logger - level - message
    """
    try:
        # Create log directory if needed
        log_path = Path('/var/log/pi-netconfig.log')
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # File handler (all modes)
        try:
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
            logger.info(f"File logging configured: {log_path}")
        except (OSError, PermissionError) as e:
            # If file logging fails, we can't log this error to file
            # Fall back to stderr
            print(f"ERROR: Cannot write to log file {log_path}: {e}", file=sys.stderr)
            raise LoggingConfigurationError(f"Cannot configure file logging: {e}")
        
        # Console handler (manual mode only)
        if mode == 'manual':
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
            logger.debug("Console logging configured for manual mode")
        
        logger.info("Logging configuration complete")
    
    except LoggingConfigurationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error configuring logging: {e}")
        logger.debug(traceback.format_exc())
        raise LoggingConfigurationError(f"Logging configuration failed: {e}")


def signal_handler(signum: int, frame) -> None:
    """
    Handle shutdown signals (SIGTERM, SIGINT).
    
    Args:
        signum: Signal number received
        frame: Current stack frame
    
    Behavior:
        - Logs signal receipt
        - Sets global shutdown_event to trigger graceful shutdown
        - Non-blocking, allows asyncio event loop to complete current operations
    """
    global shutdown_event
    
    signal_name = signal.Signals(signum).name
    logger.info(f"Received signal {signal_name} ({signum}), initiating shutdown")
    
    if shutdown_event:
        shutdown_event.set()
    else:
        logger.warning("Shutdown event not initialized, forcing exit")
        sys.exit(0)


def register_signal_handlers() -> None:
    """
    Register signal handlers for graceful shutdown.
    
    Registers:
        - SIGTERM (15): systemd service stop
        - SIGINT (2): Ctrl+C / keyboard interrupt
    
    Both signals trigger the same graceful shutdown sequence.
    """
    try:
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        logger.info("Signal handlers registered (SIGTERM, SIGINT)")
    except Exception as e:
        logger.error(f"Error registering signal handlers: {e}")
        logger.debug(traceback.format_exc())
        raise ServiceControllerError(f"Signal handler registration failed: {e}")


async def graceful_shutdown() -> None:
    """
    Coordinate graceful shutdown of all components.
    
    Behavior:
        - Calls StateMonitor.shutdown()
        - Waits up to 10 seconds for cleanup completion
        - Best-effort, no exceptions raised
        - Logs completion or timeout
    """
    global state_monitor
    
    logger.info("Initiating graceful shutdown")
    
    try:
        if state_monitor:
            logger.debug("Shutting down StateMonitor")
            shutdown_task = asyncio.create_task(state_monitor.shutdown())
            
            try:
                await asyncio.wait_for(shutdown_task, timeout=10.0)
                logger.info("StateMonitor shutdown complete")
            except asyncio.TimeoutError:
                logger.warning("StateMonitor shutdown timeout (10s)")
        else:
            logger.debug("No StateMonitor to shutdown")
        
        logger.info("Graceful shutdown complete")
    
    except Exception as e:
        logger.error(f"Error during graceful shutdown: {e}")
        logger.debug(traceback.format_exc())


async def run_service() -> None:
    """
    Run main service loop.
    
    Behavior:
        1. Creates global shutdown event
        2. Initializes StateMonitor
        3. Starts StateMonitor.run()
        4. Waits for shutdown signal
        5. Coordinates graceful shutdown
    
    Raises:
        ServiceControllerError: If StateMonitor initialization fails
    """
    global shutdown_event, state_monitor
    
    try:
        logger.info("Starting service")
        
        # Create shutdown event
        shutdown_event = asyncio.Event()
        logger.debug("Shutdown event created")
        
        # Initialize StateMonitor
        logger.debug("Initializing StateMonitor")
        state_monitor = StateMonitor()
        
        # Start StateMonitor
        logger.debug("Starting StateMonitor")
        monitor_task = asyncio.create_task(state_monitor.run())
        
        # Wait for shutdown signal
        logger.info("Service running, waiting for shutdown signal")
        await shutdown_event.wait()
        
        # Graceful shutdown
        logger.info("Shutdown signal received")
        await graceful_shutdown()
        
        # Wait for monitor task to complete
        try:
            await asyncio.wait_for(monitor_task, timeout=2.0)
        except asyncio.TimeoutError:
            logger.warning("StateMonitor task did not complete within timeout")
        
        logger.info("Service stopped")
    
    except Exception as e:
        logger.critical(f"Fatal error in service loop: {e}")
        logger.debug(traceback.format_exc())
        raise ServiceControllerError(f"Service execution failed: {e}")


def main() -> int:
    """
    Application entry point.
    
    Returns:
        int: Exit code (0 = success, 1 = error)
    
    Execution Flow:
        1. Detect execution mode (bootstrap/service/manual)
        2. Bootstrap mode:
           - Verify root privileges
           - Call Installer.install()
           - Exit with installer result
        3. Service mode:
           - Configure logging
           - Verify root privileges
           - Register signal handlers
           - Run service event loop
        4. Return appropriate exit code
    """
    try:
        # Detect execution mode
        mode = detect_execution_mode()
        
        # Bootstrap mode: install and exit
        if mode == 'bootstrap':
            print("Bootstrap mode: Installing service")
            
            if not verify_root_privileges():
                print("ERROR: Root privileges required for installation", file=sys.stderr)
                return 1
            
            success = Installer.install()
            if success:
                print("Installation successful")
                print("Start service: sudo systemctl start pi-netconfig")
                return 0
            else:
                print("ERROR: Installation failed", file=sys.stderr)
                return 1
        
        # Service/Manual mode: configure and run
        configure_logging(mode)
        
        logger.info(f"Pi Network Configuration Tool starting (mode: {mode})")
        logger.info(f"Python {sys.version}")
        
        # Verify root privileges
        if not verify_root_privileges():
            logger.critical("Root privileges required")
            print("ERROR: Must run as root (use sudo)", file=sys.stderr)
            return 1
        
        # Register signal handlers
        register_signal_handlers()
        
        # Run service event loop
        asyncio.run(run_service())
        
        logger.info("Application exiting normally")
        return 0
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        return 0
    
    except ServiceControllerError as e:
        logger.critical(f"Service controller error: {e}")
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        logger.debug(traceback.format_exc())
        print(f"CRITICAL ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
