/**
 * Formats JSON with specified indentation space or minifies it.
 * @param {string} rawString 
 * @param {number|string} indent - 2, 4, or 'tab' or 'minify'
 * @returns {Object} result object containing formatted string, validity, error details, and stats.
 */
export function formatJSON(rawString, indent = 2) {
  if (!rawString || !rawString.trim()) {
    return {
      formatted: '',
      isValid: true,
      error: null,
      stats: { lines: 0, bytes: 0, depth: 0, keys: 0 },
      parsedObj: null
    };
  }

  const cleanInput = rawString.trim();

  try {
    const parsed = JSON.parse(cleanInput);
    let space = indent;
    if (typeof indent === 'string' && !isNaN(Number(indent))) {
      space = Number(indent);
    } else if (indent === 'tab') {
      space = '\t';
    } else if (indent === 'minify') {
      space = 0;
    }

    const formatted = JSON.stringify(parsed, null, space);
    const stats = calculateJSONStats(parsed, formatted);

    return {
      formatted,
      isValid: true,
      error: null,
      stats,
      parsedObj: parsed
    };
  } catch (err) {
    const errorDetails = parseJSONError(cleanInput, err);
    return {
      formatted: cleanInput,
      isValid: false,
      error: errorDetails,
      stats: {
        lines: cleanInput.split('\n').length,
        bytes: new Blob([cleanInput]).size,
        depth: 0,
        keys: 0
      },
      parsedObj: null
    };
  }
}

/**
 * Parses JSON Error object to extract line number, column, and line snippet.
 */
function parseJSONError(rawInput, error) {
  const message = error.message || 'Invalid JSON format';
  let line = 1;
  let column = 1;

  // Try extracting line and column numbers using common browser parse error formats
  // Chrome / V8 format: "at position 42 (line 3 column 5)" or "at line 3 column 5"
  const lineColMatch = message.match(/line\s+(\d+)\s+column\s+(\d+)/i) || 
                       message.match(/position\s+(\d+)/i);

  if (lineColMatch) {
    if (lineColMatch[1] && lineColMatch[2]) {
      line = parseInt(lineColMatch[1], 10);
      column = parseInt(lineColMatch[2], 10);
    } else if (lineColMatch[1]) {
      const pos = parseInt(lineColMatch[1], 10);
      const linesUpToPos = rawInput.substring(0, pos).split('\n');
      line = linesUpToPos.length;
      column = linesUpToPos[linesUpToPos.length - 1].length + 1;
    }
  }

  const lines = rawInput.split('\n');
  const snippetLine = lines[line - 1] || '';

  return {
    message,
    line,
    column,
    snippet: snippetLine.trim()
  };
}

/**
 * Attempts to automatically repair common malformed JSON syntax.
 * - Single quotes -> Double quotes
 * - Trailing commas -> Removed
 * - Unquoted keys -> Quoted keys
 * - Comments -> Stripped
 */
export function repairJSON(invalidString) {
  if (!invalidString) return '';

  let repaired = invalidString;

  // 1. Replace smart / curly quotes with standard quotes
  repaired = repaired.replace(/[“”]/g, '"').replace(/[‘’]/g, "'");

  // 2. Strips any prepended digits/numbers on any line (handles single/multiple digits before ", {, }, [, ], words)
  let prevText;
  do {
    prevText = repaired;
    repaired = repaired.replace(/^(\s*)\d+(\s*["{\[\}\]\w:-])/gm, '$1$2');
  } while (repaired !== prevText);

  // 3. Remove JavaScript comments (// ... and /* ... */)
  repaired = repaired.replace(/\/\*[\s\S]*?\*\/|([^\\:]|^)\/\/.*$/gm, '$1');

  // 4. Try direct JSON parse
  try {
    const parsed = JSON.parse(repaired);
    return JSON.stringify(parsed, null, 2);
  } catch (e) {
    // Continue deep repair pipeline
  }

  // 5. Try parsing as a JavaScript object literal using isolated Function()
  try {
    const cleanJS = repaired
      .replace(/:\s*True\b/gi, ': true')
      .replace(/:\s*False\b/gi, ': false')
      .replace(/:\s*None\b/gi, ': null')
      .replace(/:\s*undefined\b/gi, ': null');
    const evaluator = new Function('return (' + cleanJS + ')');
    const evaluatedObj = evaluator();
    if (evaluatedObj !== undefined && typeof evaluatedObj === 'object') {
      return JSON.stringify(evaluatedObj, null, 2);
    }
  } catch (e) {
    // Proceed to regex sanitization
  }

  // 6. Convert Python / JS keywords
  repaired = repaired
    .replace(/:\s*True\b/g, ': true')
    .replace(/:\s*False\b/g, ': false')
    .replace(/:\s*None\b/g, ': null')
    .replace(/:\s*undefined\b/g, ': null')
    .replace(/:\s*NaN\b/g, ': null');

  // 7. Fix single quotes around keys & values
  repaired = repaired.replace(/'([^'\\]*(?:\\.[^'\\]*)*)'/g, '"$1"');

  // 8. Quote unquoted object keys
  repaired = repaired.replace(/([{,]\s*)([a-zA-Z0-9_$-]+)\s*:/g, '$1"$2":');

  // 9. Remove trailing commas in objects and arrays (run iteratively for nested cases)
  let prev;
  do {
    prev = repaired;
    repaired = repaired.replace(/,(\s*[\}\]])/g, '$1');
  } while (repaired !== prev);

  // 10. Verify parse after regex fixes
  try {
    const parsed = JSON.parse(repaired);
    return JSON.stringify(parsed, null, 2);
  } catch (e) {
    // 11. Auto-close missing brackets and braces
    let openBraces = (repaired.match(/\{/g) || []).length;
    let closeBraces = (repaired.match(/\}/g) || []).length;
    let openBrackets = (repaired.match(/\[/g) || []).length;
    let closeBrackets = (repaired.match(/\]/g) || []).length;

    while (closeBrackets < openBrackets) {
      repaired += ']';
      closeBrackets++;
    }
    while (closeBraces < openBraces) {
      repaired += '}';
      closeBraces++;
    }

    try {
      const parsedAgain = JSON.parse(repaired);
      return JSON.stringify(parsedAgain, null, 2);
    } catch (err2) {
      return repaired;
    }
  }
}

/**
 * Calculates structural statistics for a parsed JSON object.
 */
function calculateJSONStats(obj, formattedString) {
  let keysCount = 0;
  let maxDepth = 0;

  function traverse(current, currentDepth) {
    if (currentDepth > maxDepth) maxDepth = currentDepth;

    if (current !== null && typeof current === 'object') {
      if (Array.isArray(current)) {
        current.forEach(item => traverse(item, currentDepth + 1));
      } else {
        const keys = Object.keys(current);
        keysCount += keys.length;
        keys.forEach(k => traverse(current[k], currentDepth + 1));
      }
    }
  }

  traverse(obj, 1);

  const lines = formattedString ? formattedString.split('\n').length : 0;
  const bytes = new Blob([formattedString || '']).size;

  return {
    lines,
    bytes,
    depth: maxDepth,
    keys: keysCount
  };
}

/**
 * Format bytes into human readable string (e.g. 1.2 KB)
 */
export function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
