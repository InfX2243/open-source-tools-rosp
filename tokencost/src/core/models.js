/**
 * Model Pricing & Spec Database for tokencost
 * Prices per 1,000,000 tokens (USD)
 */

export const LLM_MODELS = [
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: 'OpenAI',
    badgeClass: 'badgeOpenai',
    inputPricePer1M: 2.50,
    outputPricePer1M: 10.00,
    contextWindow: 128000,
    latency: 'Fast (~600ms TTFT)',
    description: 'Flagship omni model with high intelligence and vision.'
  },
  {
    id: 'gpt-4o-mini',
    name: 'GPT-4o mini',
    provider: 'OpenAI',
    badgeClass: 'badgeOpenai',
    inputPricePer1M: 0.15,
    outputPricePer1M: 0.60,
    contextWindow: 128000,
    latency: 'Ultra Fast (~300ms TTFT)',
    description: 'Fast, lightweight and ultra cost-efficient small model.'
  },
  {
    id: 'o3-mini',
    name: 'o3-mini',
    provider: 'OpenAI',
    badgeClass: 'badgeOpenai',
    inputPricePer1M: 1.10,
    outputPricePer1M: 4.40,
    contextWindow: 200000,
    latency: 'Reasoning (~1.5s TTFT)',
    description: 'High-speed reasoning model specialized in STEM and coding.'
  },
  {
    id: 'claude-3-5-sonnet',
    name: 'Claude 3.5 Sonnet',
    provider: 'Anthropic',
    badgeClass: 'badgeAnthropic',
    inputPricePer1M: 3.00,
    outputPricePer1M: 15.00,
    contextWindow: 200000,
    latency: 'Fast (~700ms TTFT)',
    description: 'Industry benchmark for coding, analysis, and visual reasoning.'
  },
  {
    id: 'claude-3-5-haiku',
    name: 'Claude 3.5 Haiku',
    provider: 'Anthropic',
    badgeClass: 'badgeAnthropic',
    inputPricePer1M: 0.80,
    outputPricePer1M: 4.00,
    contextWindow: 200000,
    latency: 'Ultra Fast (~250ms TTFT)',
    description: 'High speed, high throughput small model.'
  },
  {
    id: 'gemini-2-flash',
    name: 'Gemini 2.0 Flash',
    provider: 'Google',
    badgeClass: 'badgeGoogle',
    inputPricePer1M: 0.10,
    outputPricePer1M: 0.40,
    contextWindow: 1048576,
    latency: 'Realtime (~200ms TTFT)',
    description: 'Next-gen multimodal workhorse with 1M context.'
  },
  {
    id: 'gemini-1-5-pro',
    name: 'Gemini 1.5 Pro',
    provider: 'Google',
    badgeClass: 'badgeGoogle',
    inputPricePer1M: 1.25,
    outputPricePer1M: 5.00,
    contextWindow: 2097152,
    latency: 'Moderate (~900ms TTFT)',
    description: 'Massive 2M token context window for large document reasoning.'
  },
  {
    id: 'deepseek-v3',
    name: 'DeepSeek V3',
    provider: 'DeepSeek',
    badgeClass: 'badgeDeepseek',
    inputPricePer1M: 0.14,
    outputPricePer1M: 0.28,
    contextWindow: 64000,
    latency: 'Fast (~500ms TTFT)',
    description: 'Open-weights architecture with extreme cost efficiency.'
  },
  {
    id: 'deepseek-r1',
    name: 'DeepSeek R1',
    provider: 'DeepSeek',
    badgeClass: 'badgeDeepseek',
    inputPricePer1M: 0.55,
    outputPricePer1M: 2.19,
    contextWindow: 64000,
    latency: 'Reasoning (~2.0s TTFT)',
    description: 'Open reasoning model with chain-of-thought verification.'
  },
  {
    id: 'llama-3-3-70b',
    name: 'Llama 3.3 70B',
    provider: 'Meta',
    badgeClass: 'badgeMeta',
    inputPricePer1M: 0.40,
    outputPricePer1M: 0.40,
    contextWindow: 128000,
    latency: 'Fast (~400ms TTFT)',
    description: 'State-of-the-art open weights flagship model.'
  }
];

export function calculateCost(model, inputTokens, outputTokens, requestVolume = 1) {
  const inputCost = (inputTokens / 1_000_000) * model.inputPricePer1M;
  const outputCost = (outputTokens / 1_000_000) * model.outputPricePer1M;
  const singleCost = inputCost + outputCost;

  return {
    inputCost: inputCost * requestVolume,
    outputCost: outputCost * requestVolume,
    totalCost: singleCost * requestVolume,
    singleCost: singleCost
  };
}
