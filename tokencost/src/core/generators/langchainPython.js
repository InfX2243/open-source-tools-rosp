export function generateLangchainPython({ systemPrompt, userPrompt, outputTokens, selectedModel }) {
  const modelId = selectedModel?.id || 'gpt-4o';

  return `from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Configure model and prompt template
model = ChatOpenAI(model="${modelId}", max_tokens=${outputTokens})

prompt = ChatPromptTemplate.from_messages([
    ("system", """${systemPrompt.replace(/"""/g, '\\"\\"\\"')}"""),
    ("user", """${userPrompt.replace(/"""/g, '\\"\\"\\"')}""")
])

# Build processing chain
chain = prompt | model | StrOutputParser()

result = chain.invoke({})
print(result)
`;
}
