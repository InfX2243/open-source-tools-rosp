/**
 * CurlCraft - Robust cURL Command Parser
 * Parses command-line cURL strings into a structured AST / request model.
 */

// Tokenizes shell command string respecting quotes (single, double) and escape characters
export function tokenizeCurl(cmd) {
  if (!cmd || typeof cmd !== 'string') return [];

  // Normalize multi-line continuations (\ in bash/zsh, ` in powershell, ^ in cmd)
  let normalized = cmd
    .replace(/\\\r?\n/g, ' ')
    .replace(/`\r?\n/g, ' ')
    .replace(/\^\r?\n/g, ' ')
    .trim();

  const tokens = [];
  let current = '';
  let inSingleQuote = false;
  let inDoubleQuote = false;
  let isEscaped = false;

  for (let i = 0; i < normalized.length; i++) {
    const char = normalized[i];

    if (isEscaped) {
      current += char;
      isEscaped = false;
      continue;
    }

    if (char === '\\' && !inSingleQuote) {
      isEscaped = true;
      continue;
    }

    if (char === "'" && !inDoubleQuote) {
      inSingleQuote = !inSingleQuote;
      continue;
    }

    if (char === '"' && !inSingleQuote) {
      inDoubleQuote = !inDoubleQuote;
      continue;
    }

    if (/\s/.test(char) && !inSingleQuote && !inDoubleQuote) {
      if (current.length > 0) {
        tokens.push(current);
        current = '';
      }
      continue;
    }

    current += char;
  }

  if (current.length > 0) {
    tokens.push(current);
  }

  return tokens;
}

/**
 * Parses query string from URL into an array of { key, value, enabled }
 */
export function parseQueryParams(url) {
  const params = [];
  try {
    const queryIndex = url.indexOf('?');
    if (queryIndex === -1) return params;

    const queryString = url.slice(queryIndex + 1);
    const searchParams = new URLSearchParams(queryString);

    for (const [key, value] of searchParams.entries()) {
      params.push({ id: Math.random().toString(36).substr(2, 9), key, value, enabled: true });
    }
  } catch {
    // Ignore URL parsing errors on partial inputs
  }
  return params;
}

/**
 * Parses raw cURL command into structured object
 */
export function parseCurl(curlString) {
  const result = {
    raw: curlString,
    method: 'GET',
    url: '',
    baseUrl: '',
    headers: [],
    queryParams: [],
    auth: null, // { type: 'basic' | 'bearer', username, password, token }
    body: {
      type: 'none', // 'none' | 'json' | 'form-data' | 'url-encoded' | 'raw'
      raw: '',
      json: null,
      formData: [], // [{ key, value, type: 'text' | 'file' }]
      urlEncoded: [] // [{ key, value }]
    },
    cookies: [],
    options: {
      compressed: false,
      insecure: false,
      followRedirects: false,
      timeout: null,
      userAgent: null,
      referer: null
    },
    warnings: [],
    isValid: false
  };

  if (!curlString || !curlString.trim()) {
    return result;
  }

  const tokens = tokenizeCurl(curlString);
  if (tokens.length === 0) return result;

  // Verify command starts with curl (or curl.exe)
  const firstToken = tokens[0].toLowerCase();
  const isCurl = firstToken === 'curl' || firstToken === 'curl.exe';

  let i = isCurl ? 1 : 0;
  let explicitMethod = false;
  const rawDataTokens = [];

  while (i < tokens.length) {
    const token = tokens[i];

    // Method flag: -X, --request
    if (token === '-X' || token === '--request') {
      if (i + 1 < tokens.length) {
        result.method = tokens[i + 1].toUpperCase();
        explicitMethod = true;
        i += 2;
        continue;
      }
    }

    // Headers: -H, --header
    if (token === '-H' || token === '--header') {
      if (i + 1 < tokens.length) {
        const headerStr = tokens[i + 1];
        const colonIdx = headerStr.indexOf(':');
        if (colonIdx > 0) {
          const name = headerStr.slice(0, colonIdx).trim();
          const value = headerStr.slice(colonIdx + 1).trim();

          // Check if header is authorization
          if (name.toLowerCase() === 'authorization') {
            if (value.toLowerCase().startsWith('bearer ')) {
              result.auth = {
                type: 'bearer',
                token: value.slice(7).trim()
              };
            } else if (value.toLowerCase().startsWith('basic ')) {
              result.auth = {
                type: 'basic',
                token: value.slice(6).trim()
              };
            }
          }

          result.headers.push({
            id: Math.random().toString(36).substr(2, 9),
            name,
            value,
            enabled: true
          });
        }
        i += 2;
        continue;
      }
    }

    // Basic Auth: -u, --user
    if (token === '-u' || token === '--user') {
      if (i + 1 < tokens.length) {
        const authStr = tokens[i + 1];
        const [username, ...pwdParts] = authStr.split(':');
        result.auth = {
          type: 'basic',
          username: username || '',
          password: pwdParts.join(':') || ''
        };
        i += 2;
        continue;
      }
    }

    // User Agent: -A, --user-agent
    if (token === '-A' || token === '--user-agent') {
      if (i + 1 < tokens.length) {
        result.options.userAgent = tokens[i + 1];
        result.headers.push({
          id: Math.random().toString(36).substr(2, 9),
          name: 'User-Agent',
          value: tokens[i + 1],
          enabled: true
        });
        i += 2;
        continue;
      }
    }

    // Referer: -e, --referer
    if (token === '-e' || token === '--referer') {
      if (i + 1 < tokens.length) {
        result.options.referer = tokens[i + 1];
        result.headers.push({
          id: Math.random().toString(36).substr(2, 9),
          name: 'Referer',
          value: tokens[i + 1],
          enabled: true
        });
        i += 2;
        continue;
      }
    }

    // Cookie: -b, --cookie
    if (token === '-b' || token === '--cookie') {
      if (i + 1 < tokens.length) {
        const cookieStr = tokens[i + 1];
        result.cookies.push(cookieStr);
        result.headers.push({
          id: Math.random().toString(36).substr(2, 9),
          name: 'Cookie',
          value: cookieStr,
          enabled: true
        });
        i += 2;
        continue;
      }
    }

    // Data flags: -d, --data, --data-raw, --data-binary, --data-ascii
    if (
      token === '-d' ||
      token === '--data' ||
      token === '--data-raw' ||
      token === '--data-binary' ||
      token === '--data-ascii'
    ) {
      if (i + 1 < tokens.length) {
        rawDataTokens.push({ type: 'raw', value: tokens[i + 1] });
        if (!explicitMethod && result.method === 'GET') {
          result.method = 'POST';
        }
        i += 2;
        continue;
      }
    }

    // URL-encoded data: --data-urlencode
    if (token === '--data-urlencode') {
      if (i + 1 < tokens.length) {
        rawDataTokens.push({ type: 'urlencode', value: tokens[i + 1] });
        if (!explicitMethod && result.method === 'GET') {
          result.method = 'POST';
        }
        i += 2;
        continue;
      }
    }

    // Multipart Form: -F, --form, --form-string
    if (token === '-F' || token === '--form' || token === '--form-string') {
      if (i + 1 < tokens.length) {
        const formStr = tokens[i + 1];
        const eqIdx = formStr.indexOf('=');
        if (eqIdx > 0) {
          const key = formStr.slice(0, eqIdx);
          const val = formStr.slice(eqIdx + 1);
          const isFile = val.startsWith('@');
          result.body.formData.push({
            id: Math.random().toString(36).substr(2, 9),
            key,
            value: isFile ? val.slice(1) : val,
            type: isFile ? 'file' : 'text',
            enabled: true
          });
          result.body.type = 'form-data';
        }
        if (!explicitMethod && result.method === 'GET') {
          result.method = 'POST';
        }
        i += 2;
        continue;
      }
    }

    // Compressed: --compressed
    if (token === '--compressed') {
      result.options.compressed = true;
      i++;
      continue;
    }

    // Insecure SSL: -k, --insecure
    if (token === '-k' || token === '--insecure') {
      result.options.insecure = true;
      i++;
      continue;
    }

    // Follow Redirects: -L, --location
    if (token === '-L' || token === '--location') {
      result.options.followRedirects = true;
      i++;
      continue;
    }

    // Timeout: -m, --max-time
    if (token === '-m' || token === '--max-time') {
      if (i + 1 < tokens.length) {
        result.options.timeout = parseFloat(tokens[i + 1]);
        i += 2;
        continue;
      }
    }

    // URL detection (token not starting with dash or flag)
    if (!token.startsWith('-') && !result.url) {
      result.url = token;
      i++;
      continue;
    }

    // Move to next token if unrecognized option
    i++;
  }

  // Parse Body Data
  if (rawDataTokens.length > 0) {
    const combinedData = rawDataTokens.map(d => d.value).join('&');
    result.body.raw = combinedData;

    // Check Content-Type header
    const contentTypeHeader = result.headers.find(
      h => h.name.toLowerCase() === 'content-type'
    );
    const contentType = contentTypeHeader ? contentTypeHeader.value.toLowerCase() : '';

    // Check if JSON
    let isJson = false;
    try {
      const parsedJson = JSON.parse(combinedData);
      if (typeof parsedJson === 'object' && parsedJson !== null) {
        result.body.json = parsedJson;
        result.body.type = 'json';
        isJson = true;
      }
    } catch {
      isJson = false;
    }

    if (!isJson) {
      if (contentType.includes('application/x-www-form-urlencoded') || combinedData.includes('=')) {
        // Try parsing URL encoded
        const pairs = combinedData.split('&');
        const urlEncodedList = [];
        for (const pair of pairs) {
          const [k, ...v] = pair.split('=');
          if (k) {
            urlEncodedList.push({
              id: Math.random().toString(36).substr(2, 9),
              key: decodeURIComponent(k),
              value: decodeURIComponent(v.join('=') || ''),
              enabled: true
            });
          }
        }
        if (urlEncodedList.length > 0) {
          result.body.urlEncoded = urlEncodedList;
          result.body.type = 'url-encoded';
        } else {
          result.body.type = 'raw';
        }
      } else {
        result.body.type = 'raw';
      }
    }
  }

  // Normalize URL & Query Params
  if (result.url) {
    let cleanUrl = result.url.replace(/^['"]|['"]$/g, '');
    if (!/^https?:\/\//i.test(cleanUrl) && !cleanUrl.startsWith('localhost')) {
      cleanUrl = 'https://' + cleanUrl;
    }
    result.url = cleanUrl;

    const queryIndex = cleanUrl.indexOf('?');
    if (queryIndex !== -1) {
      result.baseUrl = cleanUrl.slice(0, queryIndex);
      result.queryParams = parseQueryParams(cleanUrl);
    } else {
      result.baseUrl = cleanUrl;
    }
    result.isValid = true;
  }

  return result;
}
