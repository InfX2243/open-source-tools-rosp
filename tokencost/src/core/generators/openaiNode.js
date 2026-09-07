export function generateOpenAiNode({ systemPrompt, userPrompt, outputTokens, selectedModel }) {
  const modelId = selectedModel?.id || 'gpt-4o';

  return `import OpenAI from 'openai';

// Initialize client (reads OPENAI_API_KEY from process.env)
const openai = new OpenAI();

async function main() {
  const response = await openai.chat.completions.create({
    model: '${modelId}',
    messages: [
      {
        role: 'system',
        content: ${JSON.stringify(systemPrompt)}
      },
      {
        role: 'user',
        content: ${JSON.stringify(userPrompt)}
      }
    ],
    max_tokens: ${outputTokens},
    temperature: 0.7
  });

  console.log(response.choices[0].message.content);
}

main().catch(console.error);
`;
}
