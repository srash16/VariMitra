import requests
import json

URL = "http://127.0.0.1:8080/v1/chat/completions"

system_prompt = """
You are WariMitra's intent detection assistant.

Understand Marathi, Hindi, and English.

Return ONLY valid JSON.

If the user wants to find a nearby facility, use FIND_NEAREST.

Allowed categories:
WATER
TOILET
MEDICAL
FOOD
ACCOMMODATION
TRANSPORT

Example:
User: मला जवळ पाणी कुठे मिळेल?

Output:
{
  "action": "FIND_NEAREST",
  "parameters": {
    "category": "WATER"
  }
}
"""

user_text = input("Enter your request: ")

payload = {
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text}
    ],
    "temperature": 0,
    "max_tokens": 128
}

response = requests.post(URL, json=payload)
data = response.json()

content = data["choices"][0]["message"]["content"]

try:
    intent = json.loads(content)

    print("WariMitra Intent:")
    print(json.dumps(intent, ensure_ascii=False, indent=2))

except json.JSONDecodeError:
    print("Invalid JSON from LLM:")
    print(content)