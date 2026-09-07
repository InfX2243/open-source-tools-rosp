export function generateGeminiJs({ systemPrompt, userPrompt, outputTokens, selectedModel }) {
  const modelId = selectedModel?.provider === 'Google' ? selectedModel.id : 'gemini-1.5-flash';

  return `import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({});

async function main() {
  const response = await ai.models.generateContent({
    model: '${modelId}',
    config: {
      systemInstruction: ${JSON.stringify(systemPrompt)},
      maxOutputTokens: ${outputTokens},
      temperature: 0.7
    },
    contents: ${JSON.stringify(userPrompt)}
  });

  console.log(response.text);
}

main().catch(console.error);
`;
}
