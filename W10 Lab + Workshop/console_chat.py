from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPEN_AI_KEY")

if not api_key:
    raise ValueError("Key missing from .env file")

client = OpenAI(api_key=api_key)

print("ChatGPT Console Chat")
print("Type 'quit' to exit\n")

# Initialize messages list with system message
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

print("ChatGPT with Memory. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        break# Add user message to history
    messages.append({"role": "user", "content": user_input})

    # Send ALL messages (entire conversation)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages  # Send full history!
    )

    # Extract AI response
    ai_message = response.choices[0].message.content

    # Add AI response to history
    messages.append({"role": "assistant", "content": ai_message})

    print(f"AI: {ai_message}\n")
