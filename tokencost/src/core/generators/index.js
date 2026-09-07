import { generateOpenAiPython } from './openaiPython';
import { generateOpenAiNode } from './openaiNode';
import { generateAnthropicPython } from './anthropicPython';
import { generateAnthropicNode } from './anthropicNode';
import { generateGeminiPython } from './geminiPython';
import { generateGeminiJs } from './geminiJs';
import { generateLangchainPython } from './langchainPython';
import { generateCurlReq } from './curlReq';

export const SDK_TARGETS = [
  {
    id: 'openai-python',
    name: 'OpenAI',
    library: 'Python SDK (openai)',
    category: 'OpenAI',
    prismLang: 'python',
    extension: 'py',
    generator: generateOpenAiPython
  },
  {
    id: 'openai-node',
    name: 'OpenAI',
    library: 'Node.js / TS (openai)',
    category: 'OpenAI',
    prismLang: 'javascript',
    extension: 'js',
    generator: generateOpenAiNode
  },
  {
    id: 'anthropic-python',
    name: 'Anthropic Claude',
    library: 'Python SDK (anthropic)',
    category: 'Anthropic',
    prismLang: 'python',
    extension: 'py',
    generator: generateAnthropicPython
  },
  {
    id: 'anthropic-node',
    name: 'Anthropic Claude',
    library: 'TypeScript (@anthropic-ai/sdk)',
    category: 'Anthropic',
    prismLang: 'javascript',
    extension: 'ts',
    generator: generateAnthropicNode
  },
  {
    id: 'gemini-python',
    name: 'Google Gemini',
    library: 'Python SDK (google-generativeai)',
    category: 'Google',
    prismLang: 'python',
    extension: 'py',
    generator: generateGeminiPython
  },
  {
    id: 'gemini-js',
    name: 'Google Gemini',
    library: 'JavaScript (@google/genai)',
    category: 'Google',
    prismLang: 'javascript',
    extension: 'js',
    generator: generateGeminiJs
  },
  {
    id: 'langchain-python',
    name: 'LangChain',
    library: 'Python (langchain-openai)',
    category: 'Framework',
    prismLang: 'python',
    extension: 'py',
    generator: generateLangchainPython
  },
  {
    id: 'curl-req',
    name: 'cURL',
    library: 'HTTP REST API',
    category: 'CLI',
    prismLang: 'bash',
    extension: 'sh',
    generator: generateCurlReq
  }
];

export function generateSdkCode(targetId, context) {
  const target = SDK_TARGETS.find(t => t.id === targetId) || SDK_TARGETS[0];
  try {
    return target.generator(context);
  } catch (err) {
    return `// Failed to generate code for ${target.name} (${target.library}):\n// ${err.message}`;
  }
}
