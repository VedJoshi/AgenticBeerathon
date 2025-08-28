"""
Workflow orchestration for agent interactions
"""
from typing import List, Dict, Any, Optional
from src.agents.base_agent import BaseAgent
import asyncio
import logging

logger = logging.getLogger(__name__)


class WorkflowStep:
    """Represents a single step in a workflow"""
    
    def __init__(self, agent: BaseAgent, task: str, dependencies: Optional[List[str]] = None):
        self.agent = agent
        self.task = task
        self.dependencies = dependencies or []
        self.result = None
        self.completed = False


class Workflow:
    """Orchestrates multiple agents in a workflow"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []
        self.results: Dict[str, Any] = {}
    
    def add_step(self, step: WorkflowStep):
        """Add a step to the workflow"""
        self.steps.append(step)
    
    async def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the workflow"""
        logger.info(f"Starting workflow: {self.name}")
        
        try:
            # Simple sequential execution for now
            for i, step in enumerate(self.steps):
                logger.info(f"Executing step {i+1}: {step.task}")
                
                # Add results from previous steps to context
                step_context = context.copy() if context else {}
                step_context.update(self.results)
                
                # Execute the step
                result = await step.agent.execute(step.task, step_context)
                step.result = result
                step.completed = True
                
                # Store result with step identifier
                self.results[f"step_{i+1}"] = result
                
                logger.info(f"Step {i+1} completed successfully")
            
            logger.info(f"Workflow {self.name} completed successfully")
            return {
                "status": "success",
                "workflow": self.name,
                "results": self.results
            }
            
        except Exception as e:
            logger.error(f"Workflow {self.name} failed: {e}")
            return {
                "status": "error",
                "workflow": self.name,
                "error": str(e),
                "partial_results": self.results
            }
