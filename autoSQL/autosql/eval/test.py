import os
import openai
from dotenv import load_dotenv

load_dotenv("../../.env")
openai.api_key = os.getenv("OPENAI_API_KEY")


completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)

print(completion.choices[0].message)
