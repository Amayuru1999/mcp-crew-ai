<div align="center">
  <img src="https://github.com/crewAIInc/crewAI/blob/main/docs/crewai_logo.png" alt="CrewAI Logo" />
</div>

# MCP Crew AI Server

MCP Crew AI Server is a lightweight Python-based server designed to run, manage and create CrewAI workflows. This project leverages the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) to communicate with Large Language Models (LLMs) and tools such as Claude Desktop or Cursor IDE, allowing you to orchestrate multi-agent workflows with ease.

## Features

- **Automatic Configuration:** Automatically loads agent and task configurations from two YAML files (`agents.yml` and `tasks.yml`), so you don't need to write custom code for basic setups.
- **Command Line Flexibility:** Pass custom paths to your configuration files via command line arguments (`--agents` and `--tasks`).
- **Seamless Workflow Execution:** Easily run pre-configured workflows through the MCP `run_workflow` tool.
- **Local Development:** Run the server locally in STDIO mode, making it ideal for development and testing.

## Installation

There are several ways to install the MCP Crew AI server:

### Option 1: Install from PyPI (Recommended)

```bash
pip install mcp-crew-ai
```

### Option 2: Install from GitHub

```bash
pip install git+https://github.com/adam-paterson/mcp-crew-ai.git
```

### Option 3: Clone and Install

```bash
git clone https://github.com/adam-paterson/mcp-crew-ai.git
cd mcp-crew-ai
pip install -e .
```

### Requirements

- Python 3.11+
- MCP SDK
- CrewAI
- PyYAML

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
  agent: zookeeper
  output_file: zoo_report.md
```

## Usage

Once installed, you can run the MCP CrewAI server using either of these methods:

### Standard Python Command

```bash
mcp-crew-ai --agents path/to/agents.yml --tasks path/to/tasks.yml
```

### Using UV Execution (uvx)

For a more streamlined experience, you can use the UV execution command:

```bash
uvx mcp-crew-ai --agents path/to/agents.yml --tasks path/to/tasks.yml
```

Or run just the server directly:

```bash
uvx mcp-crew-ai-server
```

This will start the server using default configuration from environment variables.

### Command Line Options

- `--agents`: Path to the agents YAML file (required)
- `--tasks`: Path to the tasks YAML file (required)
- `--topic`: The main topic for the crew to work on (default: "Artificial Intelligence")
- `--process`: Process type to use (choices: "sequential" or "hierarchical", default: "sequential")
- `--verbose`: Enable verbose output
- `--variables`: JSON string or path to JSON file with additional variables to replace in YAML files
- `--version`: Show version information and exit

### Advanced Usage

You can also provide additional variables to be used in your YAML templates:

```bash
mcp-crew-ai --agents examples/agents.yml --tasks examples/tasks.yml --topic "Machine Learning" --variables '{"year": 2025, "focus": "deep learning"}'
```

These variables will replace placeholders in your YAML files. For example, `{topic}` will be replaced with "Machine Learning" and `{year}` with "2025".

## Contributing

Contributions are welcome! Please open issues or submit pull requests with improvements, bug fixes, or new features.

## Licence

This project is licensed under the MIT Licence. See the LICENSE file for details.

Happy workflow orchestration!
