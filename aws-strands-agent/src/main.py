"""
Main application entry point
"""
import asyncio
import logging
from src.utils.config import Config
from src.agents.base_agent import BaseAgent, AgentConfig
from src.tools.aws_tools import AWSBedrockTool, AWSS3Tool
from src.workflows.orchestrator import Workflow, WorkflowStep

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SampleAgent(BaseAgent):
    """Sample agent implementation"""
    
    async def execute(self, task: str, context=None):
        """Execute a task"""
        logger.info(f"Agent {self.name} executing task: {task}")
        
        # Mock execution
        result = {
            "agent": self.name,
            "task": task,
            "status": "completed",
            "output": f"Mock result for task: {task}"
        }
        
        if context:
            result["context_received"] = True
            
        return result
    
    def get_capabilities(self):
        """Return agent capabilities"""
        return ["text_processing", "data_analysis", "aws_integration"]


async def main():
    """Main application function"""
    try:
        # Validate configuration
        Config.validate_config()
        logger.info("Configuration validated successfully")
        
        # Create sample agent
        agent_config = AgentConfig(
            name="sample_agent",
            description="A sample agent for demonstration",
            model_id=Config.BEDROCK_MODEL_ID
        )
        agent = SampleAgent(agent_config)
        
        # Add tools to agent
        bedrock_tool = AWSBedrockTool(Config.AWS_REGION)
        s3_tool = AWSS3Tool(Config.AWS_REGION)
        agent.add_tool(bedrock_tool)
        agent.add_tool(s3_tool)
        
        # Create and execute a simple workflow
        workflow = Workflow("demo_workflow", "Demonstration workflow")
        
        step1 = WorkflowStep(agent, "Analyze the input data")
        step2 = WorkflowStep(agent, "Generate recommendations based on analysis")
        
        workflow.add_step(step1)
        workflow.add_step(step2)
        
        # Execute workflow
        context = {"input_data": "Sample hackathon data for AWS Strands solution"}
        result = await workflow.execute(context)
        
        logger.info("Workflow execution completed")
        logger.info(f"Result: {result}")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
