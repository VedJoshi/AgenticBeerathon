"""
Base Agent class for AWS Strands solution
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Configuration for agents"""

    name: str
    description: str
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    max_iterations: int = 10
    timeout: int = 300


class BaseAgent(ABC):
    """Base class for all agents in the system"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
        self.description = config.description
        self.tools = []

    @abstractmethod
    async def execute(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a task with the given context"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass

    def add_tool(self, tool):
        """Add a tool to the agent"""
        self.tools.append(tool)

    def get_tools(self):
        """Get all available tools"""
        return self.tools
