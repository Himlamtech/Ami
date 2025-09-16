import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
start_time = time.time()
response = client.chat.completions.create(
    model="gpt-4.1-nano",
    messages=[
        {
            "role": "user",
            "content": "Give me the most concise answer to the question: explain the pre-commit hook in git",
        }
    ],
    stream=True,
)
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
for chunk in response:
    print(chunk.choices[0].delta.content, end="", flush=True)
