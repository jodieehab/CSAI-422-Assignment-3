import os
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.environ.get("API_KEY")
BASE_URL = os.environ.get("BASE_URL")
LLM_MODEL = os.environ.get("LLM_MODEL")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

# -------------------------
# Weather Functions
# -------------------------
def get_current_weather(location):
    time.sleep(0.5)
    api_key = os.environ.get("WEATHER_API_KEY")
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no"
    response = requests.get(url)
    data = response.json()

    if "error" in data:
        return f"Error: {data['error']['message']}"

    current = data["current"]

    return json.dumps({
        "location": data["location"]["name"],
        "temperature_c": current["temp_c"],
        "condition": current["condition"]["text"],
        "humidity": current["humidity"],
        "wind_kph": current["wind_kph"],
    })


def get_weather_forecast(location, days=3):
    time.sleep(0.5)
    api_key = os.environ.get("WEATHER_API_KEY")
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={days}&aqi=no"
    response = requests.get(url)
    data = response.json()

    if "error" in data:
        return f"Error: {data['error']['message']}"

    forecast_days = data["forecast"]["forecastday"]
    forecast_list = []

    for day in forecast_days:
        forecast_list.append({
            "date": day["date"],
            "max_temp_c": day["day"]["maxtemp_c"],
            "min_temp_c": day["day"]["mintemp_c"],
            "condition": day["day"]["condition"]["text"],
        })

    return json.dumps({
        "location": data["location"]["name"],
        "forecast": forecast_list,
    })


# -------------------------
# Tools
# -------------------------
weather_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "Get forecast for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "days": {"type": "integer"},
                },
                "required": ["location"],
            },
        },
    },
]

tool_functions = {
    "get_current_weather": get_current_weather,
    "get_weather_forecast": get_weather_forecast,
}

# -------------------------
# Calculator Tool
# -------------------------
def calculator(expression):
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate math expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string"},
            },
            "required": ["expression"],
        },
    },
}

cot_tools = weather_tools + [calculator_tool]
tool_functions["calculator"] = calculator

# -------------------------
# Clean Messages
# -------------------------
def clean_messages(messages):
    cleaned = []
    for msg in messages:
        new_msg = dict(msg)
        if "content" not in new_msg or new_msg["content"] is None:
            new_msg["content"] = ""
        else:
            new_msg["content"] = str(new_msg["content"])
        cleaned.append(new_msg)
    return cleaned


# -------------------------
# Parallel Tool Execution
# -------------------------
def execute_tool_safely(tool_call, tool_functions):
    function_name = tool_call.function.name
    try:
        function_args = json.loads(tool_call.function.arguments)
        result = tool_functions[function_name](**function_args)
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": json.dumps({"success": True, "result": str(result)}),
        }
    except Exception as e:
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": json.dumps({"success": False, "error": str(e)}),
        }


def execute_tools_parallel(tool_calls, tool_functions):
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(execute_tool_safely, tool_call, tool_functions)
            for tool_call in tool_calls
        ]
        return [f.result() for f in futures]


# -------------------------
# Basic Conversation
# -------------------------
def run_conversation(client, system_message="You are a weather assistant."):
    messages = [{"role": "system", "content": system_message}]

    print("Weather Bot: Hello! Ask me about weather.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Weather Bot: Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=clean_messages(messages),
            tools=weather_tools,
        )

        response_message = response.choices[0].message

        assistant_message = {
            "role": "assistant",
            "content": response_message.content or ""
        }

        if response_message.tool_calls:
            assistant_message["tool_calls"] = []
            for tool_call in response_message.tool_calls:
                assistant_message["tool_calls"].append({
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    }
                })

        messages.append(assistant_message)

        if response_message.tool_calls:
            tool_results = execute_tools_parallel(
                response_message.tool_calls,
                tool_functions
            )
            messages.extend(tool_results)

            second_response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=clean_messages(messages),
            )

            print("\nWeather Bot:", second_response.choices[0].message.content, "\n")
        else:
            print("\nWeather Bot:", response_message.content, "\n")


# -------------------------
# Advanced Conversation
# -------------------------
def run_conversation_advanced(client):
    messages = [{"role": "system", "content": "You are an advanced weather assistant."}]

    print("Advanced Weather Bot: Ask complex weather questions.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Advanced Weather Bot: Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        for _ in range(5):
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=clean_messages(messages),
                tools=cot_tools,
            )

            response_message = response.choices[0].message

            assistant_message = {
                "role": "assistant",
                "content": response_message.content or ""
            }

            if response_message.tool_calls:
                assistant_message["tool_calls"] = []
                for tool_call in response_message.tool_calls:
                    assistant_message["tool_calls"].append({
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        }
                    })

            messages.append(assistant_message)

            if response_message.tool_calls:
                tool_results = execute_tools_parallel(
                    response_message.tool_calls,
                    tool_functions
                )
                messages.extend(tool_results)
            else:
                print("\nAdvanced Weather Bot:", response_message.content, "\n")
                break


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    choice = input("Choose agent (1 Basic, 2 Chain-of-Thought, 3 Advanced): ")

    if choice == "1":
        run_conversation(client)
    elif choice == "2":
        run_conversation(client, "Use tools and explain steps.")
    elif choice == "3":
        run_conversation_advanced(client)
    else:
        run_conversation(client)