"""
Agent framework.

This module provides the core framework for creating and managing agents,
including the agent registry, configuration, and communication systems.
"""

from typing import Dict, Any, List, Optional, Type, Callable
import logging
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    enabled: bool = True
    interval_seconds: Optional[int] = None
    timeout_seconds: int = 60
    max_consecutive_failures: int = 3
    dependencies: List[str] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentEvent:
    """Event in the agent framework."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    target: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False
    priority: int = 0


class AgentRegistry:
    """Registry of agents in the framework."""
    
    def __init__(self):
        """Initialize the agent registry."""
        self.agents: Dict[str, 'Agent'] = {}
        self.agent_configs: Dict[str, AgentConfig] = {}
    
    def register_agent(self, agent: 'Agent') -> None:
        """
        Register an agent with the framework.
        
        Args:
            agent: Agent to register
        """
        self.agents[agent.config.id] = agent
        self.agent_configs[agent.config.id] = agent.config
        logger.info(f"Registered agent: {agent.config.name} (ID: {agent.config.id})")
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the framework.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Returns:
            True if the agent was unregistered, False otherwise
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            del self.agents[agent_id]
            del self.agent_configs[agent_id]
            logger.info(f"Unregistered agent: {agent.config.name} (ID: {agent_id})")
            return True
        
        logger.warning(f"Agent not found for unregistration: {agent_id}")
        return False
    
    def get_agent(self, agent_id: str) -> Optional['Agent']:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_id)
    
    def get_agents_by_name(self, name: str) -> List['Agent']:
        """
        Get agents by name.
        
        Args:
            name: Name of the agents to get
            
        Returns:
            List of agent instances
        """
        return [agent for agent in self.agents.values() if agent.config.name == name]
    
    def get_all_agents(self) -> List['Agent']:
        """
        Get all registered agents.
        
        Returns:
            List of all agent instances
        """
        return list(self.agents.values())


class EventBus:
    """Event bus for agent communication."""
    
    def __init__(self):
        """Initialize the event bus."""
        self.listeners: Dict[str, List[Callable[[AgentEvent], None]]] = {}
        self.events: List[AgentEvent] = []
    
    def subscribe(self, event_type: str, callback: Callable[[AgentEvent], None]) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to subscribe to
            callback: Callback function to call when an event occurs
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        
        self.listeners[event_type].append(callback)
        logger.debug(f"Subscribed to event type: {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable[[AgentEvent], None]) -> bool:
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: Type of events to unsubscribe from
            callback: Callback function to remove
            
        Returns:
            True if the callback was unsubscribed, False otherwise
        """
        if event_type in self.listeners and callback in self.listeners[event_type]:
            self.listeners[event_type].remove(callback)
            logger.debug(f"Unsubscribed from event type: {event_type}")
            return True
        
        return False
    
    def publish(self, event: AgentEvent) -> None:
        """
        Publish an event to the bus.
        
        Args:
            event: Event to publish
        """
        self.events.append(event)
        
        if event.type in self.listeners:
            for callback in self.listeners[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event callback: {str(e)}")
        
        # Also notify listeners of "all" events
        if "all" in self.listeners:
            for callback in self.listeners["all"]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in 'all' event callback: {str(e)}")
        
        event.processed = True
        logger.debug(f"Published event: {event.type} (ID: {event.id})")
    
    def get_events(self, event_type: Optional[str] = None, processed: Optional[bool] = None) -> List[AgentEvent]:
        """
        Get events from the bus.
        
        Args:
            event_type: Optional type of events to get
            processed: Optional filter by processed state
            
        Returns:
            List of events
        """
        filtered_events = self.events
        
        if event_type is not None:
            filtered_events = [event for event in filtered_events if event.type == event_type]
        
        if processed is not None:
            filtered_events = [event for event in filtered_events if event.processed == processed]
        
        return filtered_events


class AgentFramework:
    """Core framework for managing agents."""
    
    def __init__(self):
        """Initialize the agent framework."""
        self.registry = AgentRegistry()
        self.event_bus = EventBus()
        
    def register_agent(self, agent: 'Agent') -> None:
        """
        Register an agent with the framework.
        
        Args:
            agent: Agent to register
        """
        agent.framework = self
        self.registry.register_agent(agent)
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the framework.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Returns:
            True if the agent was unregistered, False otherwise
        """
        agent = self.registry.get_agent(agent_id)
        if agent:
            agent.framework = None
        
        return self.registry.unregister_agent(agent_id)
    
    def get_agent(self, agent_id: str) -> Optional['Agent']:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            Agent instance or None if not found
        """
        return self.registry.get_agent(agent_id)
    
    def get_agents_by_name(self, name: str) -> List['Agent']:
        """
        Get agents by name.
        
        Args:
            name: Name of the agents to get
            
        Returns:
            List of agent instances
        """
        return self.registry.get_agents_by_name(name)
    
    def get_all_agents(self) -> List['Agent']:
        """
        Get all registered agents.
        
        Returns:
            List of all agent instances
        """
        return self.registry.get_all_agents()
    
    def create_event(self, event_type: str, source: str, target: Optional[str] = None, data: Optional[Dict[str, Any]] = None, priority: int = 0) -> AgentEvent:
        """
        Create an event.
        
        Args:
            event_type: Type of the event
            source: Source of the event
            target: Optional target of the event
            data: Optional data of the event
            priority: Optional priority of the event
            
        Returns:
            Created event
        """
        event = AgentEvent(
            type=event_type,
            source=source,
            target=target,
            data=data or {},
            priority=priority
        )
        
        return event
    
    def publish_event(self, event: AgentEvent) -> None:
        """
        Publish an event to the event bus.
        
        Args:
            event: Event to publish
        """
        self.event_bus.publish(event)
    
    def subscribe_to_events(self, event_type: str, callback: Callable[[AgentEvent], None]) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to subscribe to
            callback: Callback function to call when an event occurs
        """
        self.event_bus.subscribe(event_type, callback)
    
    def unsubscribe_from_events(self, event_type: str, callback: Callable[[AgentEvent], None]) -> bool:
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: Type of events to unsubscribe from
            callback: Callback function to remove
            
        Returns:
            True if the callback was unsubscribed, False otherwise
        """
        return self.event_bus.unsubscribe(event_type, callback)
    
    def get_events(self, event_type: Optional[str] = None, processed: Optional[bool] = None) -> List[AgentEvent]:
        """
        Get events from the event bus.
        
        Args:
            event_type: Optional type of events to get
            processed: Optional filter by processed state
            
        Returns:
            List of events
        """
        return self.event_bus.get_events(event_type, processed)
    
    async def run_agent(self, agent_id: str) -> bool:
        """
        Run an agent.
        
        Args:
            agent_id: ID of the agent to run
            
        Returns:
            True if the agent was run successfully, False otherwise
        """
        agent = self.registry.get_agent(agent_id)
        if not agent:
            logger.error(f"Agent not found: {agent_id}")
            return False
        
        if not agent.config.enabled:
            logger.warning(f"Agent is disabled: {agent.config.name} (ID: {agent_id})")
            return False
        
        try:
            logger.info(f"Running agent: {agent.config.name} (ID: {agent_id})")
            await agent.run()
            return True
        except Exception as e:
            logger.error(f"Error running agent {agent.config.name} (ID: {agent_id}): {str(e)}")
            return False
    
    async def run_all_agents(self) -> Dict[str, bool]:
        """
        Run all registered agents.
        
        Returns:
            Dictionary mapping agent IDs to success status
        """
        agents = self.registry.get_all_agents()
        
        # Only run enabled agents
        enabled_agents = [agent for agent in agents if agent.config.enabled]
        
        results = {}
        for agent in enabled_agents:
            results[agent.config.id] = await self.run_agent(agent.config.id)
        
        return results 