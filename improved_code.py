import openai
import json
from dotenv import load_dotenv
import os

load_dotenv()


client = openai.OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

check_spam_tool = {
    "type": "function",
    "function": {
        "name": "check_spam_tool",
        "description": "Determines if an email is spam.",
        "parameters": {
            "type": "object",
            "properties": {
                "is_spam": {
                    "type": "boolean",
                    "description": "Is the email spam?"
                },
                "reason": {
                    "type": "string",
                    "description": "Step-by-step explanation of why it is or isn't spam"
                }
            },
            "required": ["is_spam", "reason"]
        }
    }
}

def check_spam(email: str) -> dict | None:
    messages = [
        {
            "role": "user",
            "content": f"Check if the following email is spam: {email}"
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=messages,
            tools=[check_spam_tool],
            tool_choice="auto",
            temperature = 0.1,
            max_tokens = 100

        )

        tool_result = response.choices[0].message.tool_calls[0].function.arguments
        return json.loads(tool_result)

    except Exception as e:
        print(f"Erro na verificação de spam: {e}")
        return None

email = "hi how r u bro i have million dollar deal just sign here"
result = check_spam(email)

if result:
    print(json.dumps(result, indent=2))
