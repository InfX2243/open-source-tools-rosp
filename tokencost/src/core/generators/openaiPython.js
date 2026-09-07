export function generateOpenAiPython({ systemPrompt, userPrompt, outputTokens, selectedModel }) {
  const modelId = selectedModel?.id || 'gpt-4o';

  return `import os
from openai import OpenAI

# Initialize client (ensure OPENAI_API_KEY is set in your environment)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="${modelId}",
    messages=[
        {
            "role": "system",
            "content": """${systemPrompt.replace(/"""/g, '\\"\\"\\"')}"""
        },
        {
            "role": "user",
            "content": """${userPrompt.replace(/"""/g, '\\"\\"\\"')}"""
        }
    ],
    max_tokens=${outputTokens},
    temperature=0.7
)

print(response.choices[0].message.content)
`;
}
