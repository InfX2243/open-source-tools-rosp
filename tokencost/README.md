# TokenCost ⚡

A modern, high-performance, open-source **AI Prompt, Token Cost & Latency Benchmark Playground** built with React 18, Vite, and JavaScript. Accurately estimate token usage in real time, compare pricing across 10+ leading LLMs (OpenAI, Anthropic, Gemini, DeepSeek, Meta), test dynamic variables, and export production SDK boilerplate code.

![Theme](https://img.shields.io/badge/Theme-Emerald%20%26%20Cyan-emerald)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Client--Side-green)
![React](https://img.shields.io/badge/React-18-blue)

> **The Problem**: Once you finalize your prompt, you have to look up the documentation for the OpenAI, Claude, or Gemini Python/Node.js SDK, write imports, format message arrays, and set parameters.  
> **The Solution**: TokenCost gives you 1-click copy-pasteable code for Python, TypeScript, Node.js, LangChain, or cURL with your exact prompt already wired up.
>
> 🎯 **TokenCost is an AI Prompt Lab**: You paste your prompt ➔ see how many tokens it takes ➔ see what it costs on GPT-4o vs Claude vs Gemini ➔ test variables ➔ and copy the Python/JS code directly into your app.

---

## 🚀 Features

- **Live Tokenizer & Prompt Studio**:
  - Dual inputs for **System Prompt** (instructions/persona) and **User Prompt** (query).
  - Real-time token counter, character metrics, word counts, and max output tokens slider.
- **Dynamic Variable Templating Engine**:
  - Automatically identifies `{{variable_name}}` placeholders in prompts.
  - Interactive key-value test bench to test varied user data.
  - Live preview of resolved prompt text with variables interpolated.
- **Multi-Model Cost Matrix & Benchmark**:
  - Real-time pricing calculator for 10+ leading frontier models:
    - **OpenAI**: GPT-4o, GPT-4o-mini, o3-mini
    - **Anthropic**: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
    - **Google**: Gemini 2.0 Flash, Gemini 1.5 Flash, Gemini 1.5 Pro
    - **DeepSeek**: DeepSeek V3, DeepSeek R1
    - **Open-Weights**: Llama 3.3 70B
  - Scale projections: 1 Call, 1,000 Calls (1K), 10,000 Calls (10K), 1,000,000 Calls (1M).
  - Relative cost comparison bar charts and estimated latency metrics.
- **1-Click SDK Exporter (via Dropdown)**:
  - **OpenAI Python SDK** (`openai.chat.completions`)
  - **OpenAI Node.js / TS** (`openai`)
  - **Anthropic Claude Python SDK** (`anthropic.messages`)
  - **Anthropic Claude TypeScript SDK** (`@anthropic-ai/sdk`)
  - **Google Gemini Python SDK** (`google.generativeai`)
  - **Google GenAI JS SDK** (`@google/genai`)
  - **LangChain Python**
  - **cURL HTTP Command**
- **Developer UX & Privacy**:
  - Pre-loaded prompt templates (Support Bot, Structured JSON Extractor, Code Reviewer, RAG QA).
  - 1-click Copy with toast feedback, file download.
  - 100% Client-side privacy (prompts and API inputs never leave your browser).
  - Embed support via `?embed=true` and `postMessage` API.

---

## 💻 Local Development

1. Navigate to the `tokencost` directory:
   ```bash
   cd tokencost
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

4. Build for production:
   ```bash
   npm run build
   ```

---

## 🔗 How to Embed via iframe in Parent React Platforms

### 1. Simple iframe Embedding
Add the `?embed=true` query parameter to hide the standalone navbar:

```jsx
<iframe
  src="http://localhost:5176/?embed=true"
  style={{ width: '100%', height: '800px', border: 'none', borderRadius: '12px' }}
  title="TokenCost Playground"
/>
```

### 2. Passing Prompts Dynamically from Parent Platform

You can pass prompt templates and variable values dynamically using `postMessage`:

```jsx
import React, { useRef } from 'react';

export function PromptCatalog() {
  const iframeRef = useRef(null);

  const sendPromptToTool = (systemText, userText, vars) => {
    if (iframeRef.current) {
      iframeRef.current.contentWindow.postMessage(
        {
          type: 'TOKENCOST_LOAD_PROMPT',
          systemPrompt: systemText,
          userPrompt: userText,
          variables: vars
        },
        '*'
      );
    }
  };

  return (
    <div>
      <button onClick={() => sendPromptToTool(
        'You are an AI billing assistant.', 
        'How much is {{tier}} plan?', 
        { tier: 'Enterprise' }
      )}>
        Load Enterprise Billing Prompt
      </button>

      <iframe
        ref={iframeRef}
        src="http://localhost:5176/?embed=true"
        style={{ width: '100%', height: '800px', border: '1px solid #e2e8f0', borderRadius: '8px' }}
        title="TokenCost"
      />
    </div>
  );
}
```
