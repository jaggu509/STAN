import requests

BASE_URL = "http://localhost:8000/chat"
user_id = "user"       # Use one of 'human', 'user', 'ai', 'assistant', 'function', 'tool', 'system', or 'developer'.

print("Welcome to MCP Chat! Type 'exit' to quit.\n")

while True:
    message = input("You: ")
    if message.lower() in ["exit", "quit"]:
        break

    payload = {"user_id": user_id, "message": message}
    try:
        response = requests.post(BASE_URL, json=payload)
        data = response.json()
        print("Agent:", data["reply"])
        print("\n\n")
    except Exception as e:
        print("Error communicating with server:", str(e))
