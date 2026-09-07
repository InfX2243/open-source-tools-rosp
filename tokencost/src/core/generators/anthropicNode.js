export function generateAnthropicNode({ systemPrompt, userPrompt, outputTokens, selectedModel }) {
  const modelId = selectedModel?.provider === 'Anthropic' ? selectedModel.id : 'claude-3-5-sonnet-20241022';

  return `import Anthropic from '@anthropic-ai/sdk';

// Initialize client (reads ANTHROPIC_API_KEY from process.env)
const anthropic = new Anthropic();

async function main() {
  const message = await anthropic.messages.create({
    model: '${modelId}',
    max_tokens: ${outputTokens},
    system: ${JSON.stringify(systemPrompt)},
    messages: [
      {
        role: 'user',
        content: ${JSON.stringify(userPrompt)}
      }
    ]
  });

  console.log(message.content[0].text);
}

main().catch(console.error);
`;
}
