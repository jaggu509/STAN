import datetime
import requests
import os
import sqlite3
from langchain.agents import Tool
from fastapi import FastAPI
# from langchain_mcp_adapters.server import MCPToolServer

server = FastAPI(name="CustomServer")

# ----- TOOLS IMPLEMENTATION -----
@server.tool
def get_weather(city: str) -> str:
    """Get weather for a city. Input: city name"""
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY", "your-openweather-api-key")
        res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric")
        data = res.json()
        return f"Weather in {city}: {data['weather'][0]['description']}, Temp: {data['main']['temp']} °C"
    except Exception as e:
        return str(e)

@server.tool
def get_time(_: str = "") -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@server.tool
def add_numbers(inp: str) -> str:
    try:
        a, b = map(float, inp.split())
        return str(a + b)
    except:
        return "Provide two numbers separated by space."

@server.tool
def edit_file(content: str) -> str:
    try:
        with open("local_file.txt", "a") as f:
            f.write(content + "\n")
        return "File edited."
    except Exception as e:
        return str(e)

@server.tool
def sql_query(query: str) -> str:
    conn = sqlite3.connect("mcp_demo.db")
    c = conn.cursor()
    try:
        c.execute(query)
        if query.strip().lower().startswith("select"):
            rows = c.fetchall()
            return str(rows)
        else:
            conn.commit()
            return "Query executed."
    except Exception as e:
        return str(e)
    finally:
        conn.close()

# ----- Register and Run Server -----
# tools = [
#     Tool(name="GetWeather", func=get_weather, description="Get weather for a city. Input: city name"),
#     Tool(name="GetTime", func=get_time, description="Get current time. No input needed"),
#     Tool(name="AddTwoNumbers", func=add_numbers, description="Add two numbers. Input: '3 4'"),
#     Tool(name="EditFile", func=edit_file, description="Append text to a file. Input: text to append"),
#     Tool(name="SQLQuery", func=sql_query, description="Run a SQL query on SQLite DB. Input: query")
# ]

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(server, host="127.0.0.1", port=8003)
    # server = MCPToolServer(tools)
    # server.run()
