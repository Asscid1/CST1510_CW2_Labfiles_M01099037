from openai import OpenAI
import os 
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPEN_AI_KEY")

if not api_key:
    raise ValueError("Key missing from .env file")

client = OpenAI(api_key=api_key)

# 2. Create the request
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is an API?"}
    ]
)

# 3. Extract the response
answer = response.choices[0].message.content

# 4. Display the result
print(answer)


