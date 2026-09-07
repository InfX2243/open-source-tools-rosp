/**
 * Tokenizer & Estimation Engine for tokencost
 * Estimates token counts for OpenAI, Anthropic, and Gemini models.
 */

export function countTokens(text) {
  if (!text || typeof text !== 'string') return 0;

  // Split text into tokens based on whitespace, punctuation, and camelCase transitions
  const cleaned = text.trim();
  if (cleaned.length === 0) return 0;

  // Rule 1: Whitespace and punctuation delimiters
  const words = cleaned.split(/\s+/);
  let tokenCount = 0;

  for (let i = 0; i < words.length; i++) {
    const word = words[i];

    // Numbers & hex
    if (/^\d+$/.test(word)) {
      tokenCount += Math.ceil(word.length / 3);
      continue;
    }

    // JSON syntax & symbols like {}, [], "", :, ;, =, ->, =>
    const punctuationMatches = word.match(/[^\w\s]|_/g);
    const punctuationCount = punctuationMatches ? punctuationMatches.length : 0;

    // Normal word characters
    const cleanWord = word.replace(/[^\w\s]|_/g, '');
    let wordTokens = 1;

    if (cleanWord.length > 4) {
      // Average 3.5 - 4 chars per token for long words
      wordTokens = Math.ceil(cleanWord.length / 3.8);
    }

    tokenCount += wordTokens + Math.ceil(punctuationCount * 0.8);
  }

  // Ensure minimum baseline
  return Math.max(1, Math.round(tokenCount));
}

export function getTextStats(text) {
  if (!text) {
    return {
      chars: 0,
      words: 0,
      tokens: 0,
      lines: 0
    };
  }

  const chars = text.length;
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  const tokens = countTokens(text);
  const lines = text.split('\n').length;

  return {
    chars,
    words,
    tokens,
    lines
  };
}
