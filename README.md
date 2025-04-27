# AI Blog Multiagent System

## Overview
This project is an AI-driven blog generation system that utilizes multiple agents to create content based on user queries. The system integrates with the Linkup API and uses local LLMs to generate blog posts.

## Prerequisites
- Python 3.11+
- Streamlit
- CrewAI
- Ollama

## Setup Instructions
1. **Environment Setup**
   - Ensure Python 3.11+ is installed.
   - Use `uv` to install Streamlit and CrewAI.
   - Use `brew` or equivalent for Ollama.
   - Verify installations by running version checks for each tool.

2. **Linkup API Setup**
   - Clone the Linkup repository and follow the Docker setup instructions precisely.
   - Ensure the Linkup API is running locally and accessible at `http://localhost:8000`.

3. **Local LLMs with Ollama**
   - Download and run the deepseek and llama3 models using Ollama.
   - Confirm that the models are running correctly before proceeding to agent development.

## Usage
- Run the `agents.py` script to generate a blog post based on a given query.
- Use the `--output` option to specify an output file for the blog post.

## Testing
- Test the entire workflow from topic input to blog download.
- Validate the output for accuracy and adherence to the specified style.

## Contribution
- Use a version control system (e.g., Git) to track changes and collaborate.
- Commit changes with clear messages and follow a branching strategy for development.

## License
This project is licensed under the MIT License. 