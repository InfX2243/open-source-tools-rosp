/**
 * Variable Templating Engine for tokencost
 * Extracts {{variable_name}} placeholders and resolves dynamic test values.
 */

export function extractVariables(text) {
  if (!text || typeof text !== 'string') return [];

  const matches = text.match(/\{\{([a-zA-Z0-9_-]+)\}\}/g);
  if (!matches) return [];

  const unique = new Set();
  const vars = [];

  matches.forEach(m => {
    const name = m.replace(/[\{\}]/g, '').trim();
    if (!unique.has(name)) {
      unique.add(name);
      vars.push(name);
    }
  });

  return vars;
}

export function interpolatePrompt(templateText, variableMap = {}) {
  if (!templateText) return '';

  return templateText.replace(/\{\{([a-zA-Z0-9_-]+)\}\}/g, (match, varName) => {
    if (varName in variableMap && variableMap[varName] !== '') {
      return variableMap[varName];
    }
    return match; // Leave placeholder if unfilled
  });
}
