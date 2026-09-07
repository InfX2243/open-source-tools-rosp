export function generateCurlReq({ systemPrompt, userPrompt, outputTokens, selectedModel }) {
  const modelId = selectedModel?.id || 'gpt-4o';

  const payload = {
    model: modelId,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ],
    max_tokens: outputTokens,
    temperature: 0.7
  };

  return `curl https://api.openai.com/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $OPENAI_API_KEY" \\
  -d '${JSON.stringify(payload, null, 2)}'`;
}
