<center><img src="https://github.com/crewAIInc/crewAI/blob/main/docs/crewai_logo.png" alt="CrewAI Logo" width="200" /></center>

# MCP Crew AI Server

MCP Crew AI Server is a lightweight Python-based server designed to run, manage and create CrewAI workflows. This project leverages the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) to communicate with Large Language Models (LLMs) and tools such as Claude Desktop or Cursor IDE, allowing you to orchestrate multi-agent workflows with ease.

## Features

- **Automatic Configuration:** Automatically loads agent and task configurations from two YAML files (`agents.yml` and `tasks.yml`), so you don't need to write custom code for basic setups.
- **Command Line Flexibility:** Pass custom paths to your configuration files via command line arguments (`--agents` and `--tasks`).
- **Seamless Workflow Execution:** Easily run pre-configured workflows through the MCP `run_workflow` tool.
- **Local Development:** Run the server locally in STDIO mode, making it ideal for development and testing.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://your.repo.url/mcp-crew-ai.git
   cd mcp-crew-ai
   ```

2. **Install Dependencies:**
   Ensure you have Python 3.10+ installed, then install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

   *This will install the MCP SDK, CrewAI, PyYAML and any other dependencies.*

## Configuration

- **agents.yml:** Define your agents with roles, goals, and backstories.
- **tasks.yml:** Define tasks with descriptions, expected outputs, and assign them to agents.

**Example `agents.yml`:**

```yaml
zookeeper:
  role: Zookeeper
  goal: Manage zoo operations
  backstory: >
    You are a seasoned zookeeper with a passion for wildlife conservation...
```

**Example `tasks.yml`:**

```yaml
write_stories:
  description: >
    Write an engaging zoo update capturing the day's highlights.
  expected_output: 5 engaging stories
  agent_name: zookeeper
```

## Usage

To run the server with the default configuration files located in the project directory:

```bash
mcp dev server.py
```

To run the server with custom configuration files, pass the paths using the `--agents` and `--tasks` options:

```bash
mcp dev server.py -- --agents /path/to/agents.yml --tasks /path/to/tasks.yml
```

The server will start in STDIO mode and expose the `run_workflow` tool, which executes your configured CrewAI workflow.

## Contributing

Contributions are welcome! Please open issues or submit pull requests with improvements, bug fixes, or new features.

## Licence

This project is licensed under the MIT Licence. See the LICENSE file for details.

Happy workflow orchestration!
