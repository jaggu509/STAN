# Required: pip install langchain openai fastapi uvicorn

import json
from pprint import pprint
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_ollama.chat_models import ChatOllama

from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient




# ----------- LangChain Agent with tools -----------
llm = ChatOllama(model="llama3.2:latest", temperature=0)


client = MultiServerMCPClient(
    {
        # "CustomServer": {
        #     "command": "python",
        #     "args": ["C:/Users/guruj/Desktop/LLMs/demo/DEMO/mcp/custom_server.py"],
        #     "transport": "stdio",
        # },
        "figma_to_react": {
            "url": "http://localhost:3333/mcp",
            "transport": "streamable_http",
        },
        "custom_server": {
            "url": "http://localhost:8003",
            "transport": "streamable_http",
        }
    }
)

# Async wrapper to prepare tools before app starts
agent = None
async def setup_agent():
    global agent
    tools = await client.get_tools()
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt="You are a helpful assistant"
    )

# --------------- FastAPI MCP Server ----------------
app = FastAPI(name="DemoServer")

@app.on_event("startup")
async def on_start():
    await setup_agent()
    
    
class UserInput(BaseModel):
    user_id: str
    message: str

# Optional: In-memory context store
CONTEXT = {}
default_initial_context = [{
    "role": "system",
    "content": "You are a helpful assistant."
  }]

@app.post("/chat")
async def chat(user: UserInput):
    history = CONTEXT.get(user.user_id, default_initial_context)

    history.append(
        {
            'role': user.user_id,
            'content': user.message
        }
    )
    
    # Use agent to process
    response = await agent.ainvoke({"messages": history})
    
    response_message = response["messages"][-1].content
    print(response_message)
        
    # Store history
    history.append({"role": "ai", "content": response_message})

    with open("llm_response.json", "w") as f:
        f.write(json.dumps(history, indent=4))
        
    return {"reply": response_message}

# To run:
# uvicorn thisfile:app --reload --port 8000

# if __name__ == "__main__":
#     import uvicorn
#     print("----------STARTING------------")
#     uvicorn.run(app, reload)