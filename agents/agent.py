"""
Base agent class.

This module provides the base agent class that all specialized agents inherit from.
"""

from typing import Dict, Any, List, Optional, Type, Callable
import logging
import asyncio
import time
from datetime import datetime
from abc import ABC, abstractmethod

from .framework import AgentFramework, AgentConfig, AgentEvent

logger = logging.getLogger(__name__)


class Agent(ABC):
    """Base class for all agents in the framework."""
    
    def __init__(self, config: AgentConfig):
        """
        Initialize an agent.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.framework: Optional[AgentFramework] = None
        self.state: Dict[str, Any] = {}
        self.last_run_time: Optional[datetime] = None
        self.consecutive_failures = 0
        self.total_runs = 0
        self.successful_runs = 0
    
    def register(self, framework: AgentFramework) -> None:
        """
        Register the agent with a framework.
        
        Args:
            framework: Framework to register with
        """
        self.framework = framework
        framework.register_agent(self)
    
    def unregister(self) -> bool:
        """
        Unregister the agent from its framework.
        
        Returns:
            True if the agent was unregistered, False otherwise
        """
        if self.framework:
            result = self.framework.unregister_agent(self.config.id)
            self.framework = None
            return result
        
        return False
    
    def create_event(self, event_type: str, data: Optional[Dict[str, Any]] = None, target: Optional[str] = None, priority: int = 0) -> AgentEvent:
        """
        Create an event.
        
        Args:
            event_type: Type of the event
            data: Optional data of the event
            target: Optional target of the event
            priority: Optional priority of the event
            
        Returns:
            Created event
        """
        if not self.framework:
            raise ValueError("Agent is not registered with a framework")
        
        return self.framework.create_event(
            event_type=event_type,
            source=self.config.id,
            target=target,
            data=data or {},
            priority=priority
        )
    
    def publish_event(self, event: AgentEvent) -> None:
        """
        Publish an event to the event bus.
        
        Args:
            event: Event to publish
        """
        if not self.framework:
            raise ValueError("Agent is not registered with a framework")
        
        self.framework.publish_event(event)
    
    def subscribe_to_events(self, event_type: str, callback: Callable[[AgentEvent], None]) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to subscribe to
            callback: Callback function to call when an event occurs
        """
        if not self.framework:
            raise ValueError("Agent is not registered with a framework")
        
        self.framework.subscribe_to_events(event_type, callback)
    
    def unsubscribe_from_events(self, event_type: str, callback: Callable[[AgentEvent], None]) -> bool:
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: Type of events to unsubscribe from
            callback: Callback function to remove
            
        Returns:
            True if the callback was unsubscribed, False otherwise
        """
        if not self.framework:
            raise ValueError("Agent is not registered with a framework")
        
        return self.framework.unsubscribe_from_events(event_type, callback)
    
    def get_events(self, event_type: Optional[str] = None, processed: Optional[bool] = None) -> List[AgentEvent]:
        """
        Get events from the event bus.
        
        Args:
            event_type: Optional type of events to get
            processed: Optional filter by processed state
            
        Returns:
            List of events
        """
        if not self.framework:
            raise ValueError("Agent is not registered with a framework")
        
        return self.framework.get_events(event_type, processed)
    
    async def check_dependencies(self) -> bool:
        """
        Check if the agent's dependencies are met.
        
        Returns:
            True if all dependencies are met, False otherwise
        """
        if not self.framework:
            logger.warning(f"Agent {self.config.name} is not registered with a framework, cannot check dependencies")
            return False
        
        for dependency_id in self.config.dependencies:
            dependency = self.framework.get_agent(dependency_id)
            if not dependency:
                logger.warning(f"Agent {self.config.name} depends on {dependency_id}, but it is not registered")
                return False
            
            if not dependency.config.enabled:
                logger.warning(f"Agent {self.config.name} depends on {dependency_id}, but it is disabled")
                return False
        
        return True
    
    async def run(self) -> None:
        """Run the agent."""
        start_time = time.time()
        self.last_run_time = datetime.now()
        self.total_runs += 1
        
        # Check if dependencies are met
        if not await self.check_dependencies():
            self.consecutive_failures += 1
            logger.warning(f"Agent {self.config.name} dependencies not met, skipping run")
            return
        
        try:
            # Run the agent with a timeout
            if self.config.timeout_seconds:
                try:
                    await asyncio.wait_for(self._run(), timeout=self.config.timeout_seconds)
                except asyncio.TimeoutError:
                    self.consecutive_failures += 1
                    logger.error(f"Agent {self.config.name} run timed out after {self.config.timeout_seconds} seconds")
                    return
            else:
                await self._run()
            
            # If we got here, the run was successful
            self.consecutive_failures = 0
            self.successful_runs += 1
            
            # Log success
            duration = time.time() - start_time
            logger.info(f"Agent {self.config.name} run completed successfully in {duration:.2f} seconds")
            
        except Exception as e:
            self.consecutive_failures += 1
            logger.error(f"Agent {self.config.name} run failed: {str(e)}")
            
            # Check if we've reached the maximum number of consecutive failures
            if self.config.max_consecutive_failures and self.consecutive_failures >= self.config.max_consecutive_failures:
                logger.error(f"Agent {self.config.name} has reached the maximum number of consecutive failures ({self.config.max_consecutive_failures}), disabling")
                self.config.enabled = False
    
    @abstractmethod
    async def _run(self) -> None:
        """
        Implement the agent's logic here.
        
        This is the method that subclasses should override to implement their logic.
        """
        pass
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the agent's state.
        
        Returns:
            Dictionary with the agent's state
        """
        return {
            'id': self.config.id,
            'name': self.config.name,
            'description': self.config.description,
            'enabled': self.config.enabled,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'consecutive_failures': self.consecutive_failures,
            'total_runs': self.total_runs,
            'successful_runs': self.successful_runs,
            'success_rate': (self.successful_runs / self.total_runs * 100) if self.total_runs > 0 else 0,
            'state': self.state
        }
    
    def update_state(self, state_updates: Dict[str, Any]) -> None:
        """
        Update the agent's state.
        
        Args:
            state_updates: Dictionary with state updates
        """
        self.state.update(state_updates)
    
    def clear_state(self) -> None:
        """Clear the agent's state."""
        self.state = {}
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.config.name} ({self.config.id})" 