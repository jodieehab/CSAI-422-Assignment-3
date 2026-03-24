Building Conversational Agents with Tool Use and Reasoning Techniques

Name: Jodie Ehab
ID: 2020300627

Project Overview

This project implements a conversational weather assistant that can answer weather-related questions using external tools and reasoning techniques. The assistant can retrieve current weather data, forecast data, perform calculations, compare weather between multiple cities, and solve multi-step weather-related problems.

The system supports:

Tool calling
Chain-of-thought reasoning
Parallel tool execution
Multi-step workflows
Safe tool execution with error handling
Structured outputs for complex queries

Setup Instructions

Create Virtual Environment
Open terminal and run:
python -m venv venv
venv\Scripts\activate
Install Required Libraries
pip install openai python-dotenv requests
Create .env File
Create a file named .env in the project folder and add:
API_KEY=your_groq_api_key
BASE_URL=https://api.groq.com/openai/v1

LLM_MODEL=llama-3.1-8b-instant
WEATHER_API_KEY=your_weather_api_key
Run the Program
python conversational_agent.py

Then choose:
1 → Basic Agent
2 → Chain of Thought Agent
3 → Advanced Agent

Tools Implemented

get_current_weather: Retrieves current weather data
get_weather_forecast: Retrieves weather forecast
calculator: Performs mathematical calculations

Agent Types

Basic Agent
The basic agent can retrieve current weather information using the weather tool.

Example:
User: What is the weather in Cairo?
Assistant: Returns current weather data.

Chain of Thought Agent
This agent uses reasoning and the calculator tool to solve multi-step problems such as temperature differences and averages.

Example:
User: What is the temperature difference between Cairo and London?
Assistant:

Gets Cairo temperature
Gets London temperature
Calculates the difference using calculator
Returns the result
Advanced Agent
The advanced agent supports:
Parallel tool execution
Multi-step reasoning
Complex comparisons
Structured outputs
Error handling

Example:
User: Compare the weather in Cairo, Riyadh, and London.
Assistant:

Calls weather tool for all cities in parallel
Compares temperatures
Returns comparison result

Parallel vs Sequential Tool Execution

Parallel execution improves performance when multiple independent tool calls are required. For example, when comparing weather across multiple cities, the system can request weather data for all cities simultaneously instead of one by one. This reduces total waiting time and improves response speed.

Sequential execution processes tool calls one after another, which increases total response time when many tool calls are needed. Therefore, parallel execution is more efficient for multi-city weather comparisons.

Multi-Step Reasoning

Multi-step reasoning is required for complex queries such as temperature difference between two cities, average temperature over several days, and comparing future and current temperatures.

In these cases, the assistant must:

Retrieve weather data
Perform calculations
Compare results
Generate the final answer

This process requires multiple tool calls and reasoning steps.

Error Handling

The system includes safe tool execution to handle invalid tool names, incorrect arguments, API failures, and JSON parsing errors. This ensures the system does not crash and can continue the conversation safely.

Structured Output

For complex queries, the system can return structured JSON output containing:

Query type
Locations
Summary
Tools used
Final answer

This ensures the output is organized and machine-readable.

Challenges Faced

Some challenges encountered during the implementation include handling API errors and quota limits, ensuring tool calls were executed correctly, implementing parallel tool execution, managing multi-step workflows, and formatting structured outputs correctly.

These challenges were solved by adding error handling, validating tool calls, and using parallel execution with ThreadPoolExecutor.

Conclusion

This project demonstrates how conversational agents can use external tools and reasoning techniques to solve complex problems. The use of parallel execution and multi-step reasoning improves both performance and answer quality, making the assistant more efficient and intelligent.

Example Conversations

Add screenshots here:

Basic Agent Example – Weather in Cairo
Chain of Thought Example – Temperature difference between Cairo and London
Advanced Agent Example – Compare Cairo, Riyadh, and London

Files in Submission

conversational_agent.py
README.md
.env.example

Note: The .env file should not be uploaded because it contains API keys. Instead, upload a file named .env.example with placeholder keys.

Performance Note

Parallel execution was faster than sequential execution when multiple cities were requested. The speed improvement was noticeable when comparing three or more cities because the system retrieved weather data simultaneously instead of waiting for each request sequentially.