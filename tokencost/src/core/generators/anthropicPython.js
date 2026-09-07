export function generateAnthropicPython({ systemPrompt, userPrompt, outputTokens, selectedModel }) {
  const modelId = selectedModel?.provider === 'Anthropic' ? selectedModel.id : 'claude-3-5-sonnet-20241022';

  return `import os
import anthropic

# Initialize client (reads ANTHROPIC_API_KEY from environment)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="${modelId}",
    max_tokens=${outputTokens},
    system="""${systemPrompt.replace(/"""/g, '\\"\\"\\"')}""",
    messages=[
        {
            "role": "user",
            "content": """${userPrompt.replace(/"""/g, '\\"\\"\\"')}"""
        }
    ]
)

print(message.content[0].text)
`;
}
