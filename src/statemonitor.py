"""StateMonitor Module

Main state machine managing service operational mode transitions between
checking, client, and AP modes.

Design: workspace/design/design-0002-statemonitor.md
Requirements: FR-010, FR-011, FR-013, FR-020, FR-021, FR-022, FR-045
              NFR-007 (thread safety), NFR-008 (error logging)
Traceability: workspace/trace/trace-0001-requirements-traceability-matrix.md

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
"""

import asyncio
import logging
from enum import Enum, auto
from typing import Optional


class SystemState(Enum):
    """System operational states."""
    CHECKING = auto()
    CLIENT = auto()
    AP_MODE = auto()


class StateMonitorError(Exception):
    """Base exception for state monitor operations."""
    pass


class StateTransitionError(StateMonitorError):
    """State transition failure."""
    pass


class ComponentInitializationError(StateMonitorError):
    """Component initialization failure."""
    pass


class StateMachine:
    """State machine coordinating operational mode transitions.
    
    Manages transitions between CHECKING, CLIENT, and AP_MODE states based on
    connection status and coordinates ConnectionManager, APManager, and WebServer
    components.
    
    Attributes:
        connection_manager: Connection testing module
        ap_manager: Access point management module
        web_server: HTTP interface module
        current_state: Current operational state
        failure_count: Consecutive connection failure counter
        shutdown_event: Event signaling shutdown request
        logger: Logger instance for state monitoring
    """
    
    def __init__(self, connection_manager, ap_manager, web_server):
        """Initialize state machine with component dependencies.
        
        Args:
            connection_manager: ConnectionManager instance
            ap_manager: APManager instance
            web_server: WebServer instance
        """
        self.connection_manager = connection_manager
        self.ap_manager = ap_manager
        self.web_server = web_server
        self.current_state: SystemState = SystemState.CHECKING
        self.failure_count: int = 0
        self.shutdown_event: Optional[asyncio.Event] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger('StateMonitor')

    async def initialize(self) -> None:
        """Initialize state machine and component instances.
        
        Creates shutdown event and starts monitoring task.
        
        Raises:
            ComponentInitializationError: If component initialization fails
        """
        self.shutdown_event = asyncio.Event()
        try:
            # Components should already be initialized by their constructors
            # This method exists for future initialization needs
            self.logger.debug("State machine initialization complete")
        except Exception as e:
            raise ComponentInitializationError(
                "Failed to initialize components"
            ) from e
        
        self.monitoring_task = asyncio.create_task(self.monitoring_loop())
        self.logger.info("State monitoring started")

    async def monitoring_loop(self) -> None:
        """Main monitoring loop checking connection status every 30 seconds.
        
        Runs until shutdown_event is set. Handles state transitions based on
        connection status and failure count.
        """
        self.logger.debug("Monitoring loop started")
        
        try:
            while not self.shutdown_event.is_set():
                try:
                    connected = await self.check_connection()
                    self.logger.debug(
                        f"Connection check: {'connected' if connected else 'disconnected'}, "
                        f"state={self.current_state.name}, failures={self.failure_count}"
                    )
                    
                    if connected:
                        if self.current_state != SystemState.CLIENT:
                            await self.transition_to_client()
                        else:
                            # Reset failure count on successful check in CLIENT state
                            self.failure_count = 0
                    else:
                        self.failure_count += 1
                        self.logger.debug(f"Connection failure count: {self.failure_count}")
                        
                        if self.failure_count >= 3 and self.current_state != SystemState.AP_MODE:
                            await self.transition_to_ap_mode()
                            
                except asyncio.CancelledError:
                    self.logger.info("Monitoring loop cancelled")
                    raise
                except Exception as e:
                    await self.handle_state_transition_failure(e)
                
                # Wait 30 seconds before next check
                try:
                    await asyncio.wait_for(
                        self.shutdown_event.wait(),
                        timeout=30.0
                    )
                    # If we get here, shutdown was requested
                    break
                except asyncio.TimeoutError:
                    # Timeout is normal - continue monitoring
                    pass
                    
        except asyncio.CancelledError:
            self.logger.info("Monitoring loop terminated")

    async def check_connection(self) -> bool:
        """Check current connection status.
        
        Returns:
            bool: True if connection is active, False otherwise
        """
        try:
            is_connected = await self.connection_manager.test_connection()
            return is_connected
        except Exception as e:
            self.logger.warning("Connection check failed", exc_info=True)
            return False

    async def transition_to_client(self) -> None:
        """Transition to CLIENT mode.
        
        Deactivates AP mode if active, stops web server, and resets failure count.
        
        Raises:
            StateTransitionError: If transition fails
        """
        try:
            self.logger.info("Transitioning to CLIENT mode")
            
            if self.current_state == SystemState.AP_MODE:
                await self.ap_manager.deactivate_ap()
                await self.web_server.stop_server()
            
            self.current_state = SystemState.CLIENT
            self.failure_count = 0
            self.logger.info("Successfully transitioned to CLIENT mode")
            
        except Exception as e:
            self.logger.error("Failed to transition to CLIENT mode", exc_info=True)
            raise StateTransitionError(
                "Failed to transition to CLIENT mode"
            ) from e

    async def transition_to_ap_mode(self) -> None:
        """Transition to AP_MODE.
        
        Activates access point and starts web server on port 8080.
        
        Raises:
            StateTransitionError: If transition fails
        """
        try:
            self.logger.info("Transitioning to AP_MODE")
            
            await self.ap_manager.activate_ap()
            await self.web_server.start_server()
            
            self.current_state = SystemState.AP_MODE
            self.logger.info("Successfully transitioned to AP_MODE")
            
        except Exception as e:
            self.logger.error("Failed to transition to AP_MODE", exc_info=True)
            raise StateTransitionError(
                "Failed to transition to AP_MODE"
            ) from e

    async def handle_state_transition_failure(self, error: Exception) -> None:
        """Handle state transition failures with recovery attempts.
        
        Args:
            error: Exception that caused the transition failure
        """
        self.logger.error(
            f"State transition failed in {self.current_state.name} state",
            exc_info=True
        )
        
        try:
            # Attempt recovery to current state
            if self.current_state == SystemState.CLIENT:
                self.logger.warning("Attempting recovery to CLIENT state")
                await self.transition_to_client()
            elif self.current_state == SystemState.AP_MODE:
                self.logger.warning("Attempting recovery to AP_MODE state")
                await self.transition_to_ap_mode()
        except Exception as recovery_error:
            self.logger.critical(
                "Failed to recover from state transition failure",
                exc_info=True
            )

    async def shutdown(self) -> None:
        """Gracefully shutdown state machine and all components.
        
        Cancels monitoring task, deactivates AP if active, stops web server,
        and performs cleanup on all components.
        """
        self.logger.info("Initiating shutdown")
        self.shutdown_event.set()
        
        # Cancel monitoring task
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Deactivate components
        try:
            if self.current_state == SystemState.AP_MODE:
                await self.ap_manager.deactivate_ap()
                await self.web_server.stop_server()
        except Exception as e:
            self.logger.warning("Component shutdown failed", exc_info=True)
        
        self.logger.info("Shutdown complete")


async def run(connection_manager, ap_manager, web_server) -> None:
    """Main entry point for state monitoring.
    
    Initializes state machine with provided components and starts monitoring loop.
    
    Args:
        connection_manager: ConnectionManager instance
        ap_manager: APManager instance
        web_server: WebServer instance
        
    Raises:
        StateMonitorError: On critical failures
    """
    logger = logging.getLogger('StateMonitor')
    logger.info("Starting state monitor")
    
    state_machine = StateMachine(connection_manager, ap_manager, web_server)
    
    try:
        await state_machine.initialize()
        
        # Wait for shutdown signal
        await state_machine.shutdown_event.wait()
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.critical("State monitor failed", exc_info=True)
        raise StateMonitorError("State monitor failed") from e
    finally:
        await state_machine.shutdown()
