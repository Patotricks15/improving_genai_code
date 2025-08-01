# 1 - What problems do you see with this code?

## 2 Problems I identified:

1) Output format being defined in the prompt
2) Absence of error handling

## Suggested Improvements

### Use tool (function calling) instead of setting the output format in the prompt text

The major advantage is the **maintenance** and **reliability** of the project, ensuring **consistent, valid JSON** and forcing **structure adherence** to **avoid malformed outputs** and **missing fields**.

#### Building the Tool `check_spam_tool`

```python
check_spam_tool = {
    "type": "function",
    "function": {
        "name": "check_spam_tool",
        "description": "Determines whether an email is spam.",
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
```

**Before:**
```python
prompt = f"""
Determine if the email is spam.
Return a valid JSON object:
{{ "is_spam": bool, "reason": str }}
Email: {email}
"""
completion = openai.chat.completions.create(...)
res = completion.choices[0].message.content
```

**After:**
```python
tools = [{
  "type": "function",
  "function": {
    "name": "check_spam_tool",
    ...
  }
}]
response = client.chat.completions.create(
    model=..., messages=..., tools=tools, tool_choice="auto"
)
result = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
```

### Define required fields via JSON Schema

**Before:**
```text
Return a valid JSON object with the format:
    {{
        is_spam: is the email spam? // bool
        reason: think step by step, why is it spam or not spam? // str
    }}
```

**After:**
```json
"parameters": {
  "type": "object",
  "properties": {
    "is_spam": { "type": "boolean" },
    "reason": { "type": "string" }
  },
  "required": ["is_spam", "reason"]
}
```

### Use `.tool_calls[0].function.arguments` instead of extracting JSON from text content

**Before:**
```python
res = completion.choices[0].message.content
parsed = json.loads(res)
```

**After:**
```python
tool_result = response.choices[0].message.tool_calls[0].function.arguments
result = json.loads(tool_result)
```

Reference: [Introducing Structured Outputs in the API | OpenAI](https://openai.com/index/introducing-structured-outputs-in-the-api/)


## Absence of Error Handling

Insert the logic in a `try-except` block to prevent the script from **crashing in production**.

**Before:**
```python
res = json.loads(completion.choices[0].message.content)
```

**After:**
```python
try:
    result = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
except Exception as e:
    print(f"Spam check error: {e}")
    return None
```

---

# 2 - What ideas do you have to make it better?

## Control the Temperature parameter

Temperature is a number that **controls the randomness** of an LLM’s outputs. Most APIs limit the value to be from 0 to 1 or some similar range to keep the outputs in semantically coherent bounds. ([A Comprehensive Guide to LLM Temperature 🔥🌡️ | Towards Data Science](https://towardsdatascience.com/a-comprehensive-guide-to-llm-temperature/)).

We can ensure a consistent result by **lowering the temperature value**. It can be extremely important in cases of ambiguity, **preventing different outputs for the same input message**

## Model Selection

For this simple task, we can use a **cheaper model** and run some tests to verify if the responses are the same, but at a lower cost.

**Before:**
```python
completion = openai.chat.completions.create(
    model="gpt-4o-mini",
    temperature=1.0,
    ...
)
```

**After:**
```python
response = client.chat.completions.create(
    model="gpt-4.1-nano-2025-04-14",
    temperature=0.1,
    ...
)
```
| Model              | Version                  | Input Cost (per 1M tokens) | Output Cost (per 1M tokens) |
|-------------------|--------------------------|-----------------------------|------------------------------|
| gpt-4o-mini        | gpt-4o-mini-2024-07-18   | $0.15                       | $0.60                        |
| gpt-4.1-nano       | gpt-4.1-nano-2025-04-14  | $0.10                       | $0.40                        |

Reference: [Pricing - OpenAI API](https://platform.openai.com/docs/pricing)
