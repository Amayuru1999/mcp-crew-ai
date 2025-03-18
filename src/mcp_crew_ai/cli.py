import os
import argparse
import yaml
import tempfile
import json
import subprocess
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
import importlib.metadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crew_ai_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp_crew_ai")

def main():
    """
    Main entry point for the MCP Crew AI CLI.
    Parses command line arguments and starts an MCP server with the specified configuration.
    """
    parser = argparse.ArgumentParser(description='MCP Crew AI - Run CrewAI agents through MCP')
    parser.add_argument('--agents', type=str, help='Path to agents YAML file')
    parser.add_argument('--tasks', type=str, help='Path to tasks YAML file')
    parser.add_argument('--topic', type=str, default='Artificial Intelligence', 
                      help='The main topic for the crew to work on')
    parser.add_argument('--process', type=str, default='sequential', 
                      choices=['sequential', 'hierarchical'], 
                      help='Process type: sequential or hierarchical')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--variables', type=str, 
                      help='JSON string or path to JSON file with variables to replace in YAML files')
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    
    args = parser.parse_args()
    
    # Show version and exit if requested
    if args.version:
        try:
            version = importlib.metadata.version("mcp-crew-ai")
            print(f"MCP Crew AI v{version}")
        except importlib.metadata.PackageNotFoundError:
            print("MCP Crew AI (development version)")
        return
        
    # Get version for MCP_CREW_VERSION environment variable
    try:
        version = importlib.metadata.version("mcp-crew-ai")
    except importlib.metadata.PackageNotFoundError:
        version = "0.1.0"
    
    # Process YAML file paths
    agents_path = args.agents
    tasks_path = args.tasks
    
    if not agents_path or not tasks_path:
        logger.error("Both --agents and --tasks arguments are required. Use --help for more information.")
        sys.exit(1)
    
    # Validate that the files exist
    agents_file = Path(agents_path)
    tasks_file = Path(tasks_path)
    
    if not agents_file.exists():
        logger.error(f"Agents file not found: {agents_path}")
        sys.exit(1)
        
    if not tasks_file.exists():
        logger.error(f"Tasks file not found: {tasks_path}")
        sys.exit(1)
    
    # Process variables if provided
    variables = {}
    if args.variables:
        if os.path.isfile(args.variables):
            with open(args.variables, 'r') as f:
                variables = json.load(f)
        else:
            try:
                variables = json.loads(args.variables)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse variables as JSON: {args.variables}")
    
    # Add topic to variables
    variables['topic'] = args.topic
    
    logger.info(f"Starting MCP Crew AI server with:")
    logger.info(f"- Agents file: {agents_file}")
    logger.info(f"- Tasks file: {tasks_file}")
    logger.info(f"- Topic: {args.topic}")
    logger.info(f"- Process type: {args.process}")
    
    # Set environment variables for the server to use
    os.environ["MCP_CREW_AGENTS_FILE"] = str(agents_file.absolute())
    os.environ["MCP_CREW_TASKS_FILE"] = str(tasks_file.absolute())
    os.environ["MCP_CREW_TOPIC"] = args.topic
    os.environ["MCP_CREW_PROCESS"] = args.process
    os.environ["MCP_CREW_VERBOSE"] = "1" if args.verbose else "0"
    os.environ["MCP_CREW_VERSION"] = version
    
    if variables:
        os.environ["MCP_CREW_VARIABLES"] = json.dumps(variables)
        
    # Build MCP command to run the server
    server_module = os.path.join(os.path.dirname(__file__), "server.py")
    cmd = ["mcp", "dev", server_module]
    
    logger.info(f"Executing: {' '.join(cmd)}")
    
    try:
        # Run the MCP server
        subprocess.run(cmd)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        sys.exit(1)


def load_yaml_with_variables(file_path: Path, variables: Dict[str, Any]) -> Dict[str, Any]:
    """Load YAML and replace variables in memory"""
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return {}
    
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Replace all variables in the content
        for key, value in variables.items():
            placeholder = '{' + key + '}'
            content = content.replace(placeholder, str(value))
        
        # Parse the YAML content
        yaml_content = yaml.safe_load(content) or {}
        return yaml_content
    except Exception as e:
        logger.error(f"Error loading YAML file {file_path}: {e}")
        return {}


if __name__ == "__main__":
    main()