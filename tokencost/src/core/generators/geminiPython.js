export function generateGeminiPython({ systemPrompt, userPrompt, outputTokens, selectedModel }) {
  const modelId = selectedModel?.provider === 'Google' ? selectedModel.id : 'gemini-1.5-flash';

  return `import os
import google.generativeai as genai

# Configure API Key (reads GEMINI_API_KEY from environment)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name="${modelId}",
    system_instruction="""${systemPrompt.replace(/"""/g, '\\"\\"\\"')}""",
    generation_config=genai.GenerationConfig(
        max_output_tokens=${outputTokens},
        temperature=0.7
    )
)

response = model.generate_content("""${userPrompt.replace(/"""/g, '\\"\\"\\"')}""")
print(response.text)
`;
}
