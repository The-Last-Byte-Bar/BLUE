"""
Agents module.

This module provides a framework for intelligent agents that analyze data,
make decisions, and execute actions in the cryptocurrency space.
"""

from .framework import AgentFramework
from .agent import Agent
from .trading import TradingAgent
from .analysis import AnalysisAgent
from .social import SocialAgent
from .scheduler import AgentScheduler

__all__ = [
    'AgentFramework',
    'Agent',
    'TradingAgent',
    'AnalysisAgent',
    'SocialAgent',
    'AgentScheduler'
] 