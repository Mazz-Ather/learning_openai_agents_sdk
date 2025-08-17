# Complete OpenAI Agents SDK

This repository demonstrates advanced usage of OpenAI Agents SDK with practical examples, organized by topic and complexity. Each folder contains self-contained Python modules illustrating agent configuration, tool integration, context management, hooks, handoffs, and more.

## Folder Structure

- **00_agent/**  
  Basic agent setup and usage.
- **01_RunConfig/**  
  Examples of basic and advanced run configurations.
- **02_tools/**  
  Tool integration at various levels: basic, medium, and advanced.
- **03_hooks/**  
  Custom agent and run hooks for lifecycle event handling.
- **04_handoffs/**  
  Agent handoff patterns for multi-agent workflows.
- **05_guardrails/**  
  (Reserved for guardrails and validation logic.)
- **06_context/**  
  Context passing and local context management.
- **07_dynamic_instruction/**  
  Dynamic agent instructions based on runtime context.
- **08_agent_as_tools/**  
  Using agents as callable tools.
- **xx_projects/**  
  Experimental and project-specific scripts.

## Getting Started

1. **Clone the repository**
   ```sh
   git clone https://github.com/Mazz-Ather/learning_openai_agents_sdk
   cd learning_openai_agents_sdk

2. Install Python 3.13+
Each module uses .python-version for version management.

3. Install dependencies
Each folder contains its own pyproject.toml.
For example, to install dependencies for 02_tools:

4. Set up environment variables
Copy .env to your root directory and provide your API keys:

5. Run examples
Each folder contains scripts you can run directly .
# Key Features
## Agent Creation:

See 00_agent/agent.py for basic agent instantiation.

## Run Configuration:

Explore 01_RunConfig/basic_runconfig.py and 01_RunConfig/advanced_runconfig.py for different run setups.

## Tool Integration:

Basic: 02_tools/basic_tools.py
Medium: 02_tools/medium_level_tools.py
Advanced: 02_tools/advanced_tools.py
Tool use behavior: 02_tools/tool_use_behavior.py
Hooks:

## Agent hooks: 03_hooks/agent_hooks.py

Run hooks: 03_hooks/run_hooks.py

## Context Management:

Local context: 06_context/local_context.py
Dynamic Instructions:

## 07_dynamic_instruction/dynamic_instructons.py

## Agent as Tool:

08_agent_as_tools/agent_as_tool.py
Project Examples:

## xx_projects/fetch_tool.py


### Notes
 -Each module is self-contained and may have its own dependencies.
  -Use the provided .python-version files for consistent Python environments.

License: MIT
Author: Muhammad Mazz Ather