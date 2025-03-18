from mcp.server.fastmcp import FastMCP
from crewai import Crew, Agent, Task, Process
import yaml
import os
import sys
import io
import contextlib
import json
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crew_ai_server.log"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("mcp_crew_ai_server")

# Initialize server at module level
server = None


@contextlib.contextmanager
def capture_output():
    """Capture stdout and stderr."""
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield new_out, new_err
    finally:
        sys.stdout, sys.stderr = old_out, old_err

def format_output(output):
    """Format the output to make it more readable."""
    # Split by lines and filter out LiteLLM log lines
    lines = output.split('\n')
    filtered_lines = [line for line in lines if not line.strip().startswith('[') or 'LiteLLM' not in line]
    
    # Join the filtered lines back together
    return '\n'.join(filtered_lines)

def kickoff(
    agents_file: str = None, 
    tasks_file: str = None,
    topic: str = None,
    additional_context: dict = None
):
    """
    Execute a CrewAI workflow using YAML configuration files.
    
    Args:
        agents_file: Optional path to override the default agents YAML file
        tasks_file: Optional path to override the default tasks YAML file
        topic: The main topic for the crew to work on
        additional_context: Additional context variables for template formatting
    
    Returns:
        The results from the crew execution
    """
    logger.info(f"Tool kickoff called with: agents_file={agents_file}, tasks_file={tasks_file}, topic={topic}")
    
    # Use default paths if none provided
    agents_path = agents_file if agents_file else str(agents_yaml_path)
    tasks_path = tasks_file if tasks_file else str(tasks_yaml_path)
    
    # Use provided topic or default from environment variable
    current_topic = topic if topic else os.environ.get("MCP_CREW_TOPIC", "Artificial Intelligence")
    
    logger.info(f"Using agents file: {agents_path}")
    logger.info(f"Using tasks file: {tasks_path}")
    logger.info(f"Using topic: {current_topic}")
    
    # Check if files exist
    if not os.path.exists(agents_path):
        logger.error(f"Agent file not found: {agents_path}")
        return {"error": f"Agent file not found: {agents_path}"}
        
    if not os.path.exists(tasks_path):
        logger.error(f"Task file not found: {tasks_path}")
        return {"error": f"Task file not found: {tasks_path}"}
    
    # Template variables
    current_variables = {"topic": current_topic}
    
    # Add additional context if provided
    if additional_context:
        current_variables.update(additional_context)
    
    # Also add variables from command line if they exist
    if variables:
        # Don't overwrite explicit variables with command line ones
        for key, value in variables.items():
            if key not in current_variables:
                current_variables[key] = value
    
    logger.info(f"Template variables: {current_variables}")
    
    # Load agent configurations
    try:
        with open(agents_path, 'r') as f:
            agents_data = yaml.safe_load(f)
        logger.info(f"Loaded agents data: {list(agents_data.keys())}")
    except Exception as e:
        logger.error(f"Error loading agents file: {str(e)}")
        return {"error": f"Error loading agents file: {str(e)}"}
        
    # Create agents
    agents_dict = {}
    for name, config in agents_data.items():
        try:
            # Format template strings in config
            role = config.get("role", "")
            goal = config.get("goal", "")
            backstory = config.get("backstory", "")
            
            # Format with variables if they contain placeholders
            if "{" in role:
                role = role.format(**current_variables)
            if "{" in goal:
                goal = goal.format(**current_variables)
            if "{" in backstory:
                backstory = backstory.format(**current_variables)
            
            logger.info(f"Creating agent: {name}")
            agents_dict[name] = Agent(
                name=name,
                role=role,
                goal=goal,
                backstory=backstory,
                verbose=verbose,
                allow_delegation=True
            )
        except Exception as e:
            logger.error(f"Error creating agent {name}: {str(e)}")
            return {"error": f"Error creating agent {name}: {str(e)}"}
        
    # Load task configurations
    try:
        with open(tasks_path, 'r') as f:
            tasks_data = yaml.safe_load(f)
        logger.info(f"Loaded tasks data: {list(tasks_data.keys())}")
    except Exception as e:
        logger.error(f"Error loading tasks file: {str(e)}")
        return {"error": f"Error loading tasks file: {str(e)}"}
        
    # Create tasks
    tasks_list = []
    for name, config in tasks_data.items():
        try:
            description = config.get("description", "")
            expected_output = config.get("expected_output", "")
            agent_name = config.get("agent")
            
            # Format with variables if they contain placeholders
            if "{" in description:
                description = description.format(**current_variables)
            if "{" in expected_output:
                expected_output = expected_output.format(**current_variables)
            
            if not agent_name or agent_name not in agents_dict:
                logger.error(f"Task {name} has invalid agent: {agent_name}")
                logger.error(f"Available agents: {list(agents_dict.keys())}")
                return {"error": f"Task {name} has invalid agent: {agent_name}"}
                
            logger.info(f"Creating task: {name} for agent: {agent_name}")
            task = Task(
                description=description,
                expected_output=expected_output,
                agent=agents_dict[agent_name]
            )
            
            # Optional output file
            output_file = config.get("output_file")
            if output_file:
                task.output_file = output_file
                
            tasks_list.append(task)
        except Exception as e:
            logger.error(f"Error creating task {name}: {str(e)}")
            return {"error": f"Error creating task {name}: {str(e)}"}
        
    # Create the crew
    logger.info("Creating crew")
    logger.info(f"Number of agents: {len(agents_dict)}")
    logger.info(f"Number of tasks: {len(tasks_list)}")
    
    # Check if we have agents and tasks
    if not agents_dict:
        logger.error("No agents were created")
        return {"error": "No agents were created"}
    if not tasks_list:
        logger.error("No tasks were created")
        return {"error": "No tasks were created"}
        
    try:
        crew = Crew(
            agents=list(agents_dict.values()),
            tasks=tasks_list,
            verbose=verbose,
            process=process_type
        )
        logger.info("Crew created successfully")
    except Exception as e:
        logger.error(f"Error creating crew: {str(e)}")
        return {"error": f"Error creating crew: {str(e)}"}
    
    # Execute the crew with captured output
    try:
        logger.info("Starting crew kickoff with captured output")
        with capture_output() as (out, err):
            result = crew.kickoff()
            
        # Get the captured output
        stdout_content = out.getvalue()
        stderr_content = err.getvalue()
        
        # Format the output to make it more readable
        formatted_stdout = format_output(stdout_content)
        formatted_stderr = format_output(stderr_content)
        
        logger.info("Crew kickoff completed successfully")
        
        # Convert result to string if it's not a simple type
        if not isinstance(result, (str, int, float, bool, list, dict)) and result is not None:
            logger.info(f"Converting result of type {type(result)} to string")
            result = str(result)
        
        # Create a structured response with the agent outputs
        response = {
            "result": result,
            "agent_outputs": formatted_stdout,
            "errors": formatted_stderr if formatted_stderr.strip() else None
        }
        
        # Log a sample of the output for debugging
        if formatted_stdout:
            sample = formatted_stdout[:500] + "..." if len(formatted_stdout) > 500 else formatted_stdout
            logger.info(f"Sample of agent outputs: {sample}")
        
        return response
    except Exception as e:
        logger.error(f"Error in crew kickoff: {str(e)}")
        return {"error": f"Error in crew kickoff: {str(e)}"}


def initialize():
    """Initialize the server with configuration from environment variables."""
    global server, agents_yaml_path, tasks_yaml_path, topic, process_type_str, verbose, variables_json, variables, process_type
    
    # Log startup
    logger.info("Starting Crew AI Server")
    
    # Create FastMCP server
    server = FastMCP("Crew AI Server", version=os.environ.get("MCP_CREW_VERSION", "0.1.0"))
    
    # Get configuration from environment variables
    agents_yaml_path = os.environ.get("MCP_CREW_AGENTS_FILE", "")
    tasks_yaml_path = os.environ.get("MCP_CREW_TASKS_FILE", "")
    topic = os.environ.get("MCP_CREW_TOPIC", "Artificial Intelligence")
    process_type_str = os.environ.get("MCP_CREW_PROCESS", "sequential")
    verbose = os.environ.get("MCP_CREW_VERBOSE", "0") == "1"
    variables_json = os.environ.get("MCP_CREW_VARIABLES", "")
    
    # Define fallback paths
    if not agents_yaml_path or not tasks_yaml_path:
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        project_root = current_dir.parent.parent
        examples_dir = project_root / "examples"
        
        if not agents_yaml_path:
            agents_yaml_path = str(examples_dir / "agents.yml")
        
        if not tasks_yaml_path:
            tasks_yaml_path = str(examples_dir / "tasks.yml")
    
    # Convert paths to Path objects
    agents_yaml_path = Path(agents_yaml_path)
    tasks_yaml_path = Path(tasks_yaml_path)
    
    logger.info(f"Agents YAML path: {agents_yaml_path} (exists: {agents_yaml_path.exists()})")
    logger.info(f"Tasks YAML path: {tasks_yaml_path} (exists: {tasks_yaml_path.exists()})")
    logger.info(f"Topic: {topic}")
    logger.info(f"Process type: {process_type_str}")
    logger.info(f"Verbose: {verbose}")
    
    # Parse variables
    variables = {"topic": topic}
    if variables_json:
        try:
            additional_vars = json.loads(variables_json)
            variables.update(additional_vars)
            logger.info(f"Loaded additional variables: {list(additional_vars.keys())}")
        except json.JSONDecodeError:
            logger.warning(f"Could not parse variables JSON: {variables_json}")
    
    logger.info(f"Template variables: {variables}")
    
    # Set process type
    process_type = Process.sequential
    if process_type_str.lower() == 'hierarchical':
        process_type = Process.hierarchical
        logger.info("Using hierarchical process")
        
    # Register the kickoff tool
    server.tool()(kickoff)
    
    return server


def main():
    """Run the MCP server as a standalone application."""
    server = initialize()
    
    # If run directly, start the FastMCP server
    if __name__ == "__main__":
        server.run()
    
    return server


# Initialize server when module is imported
initialize()