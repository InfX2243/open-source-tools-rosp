export function generatePythonRequests(req) {
  const method = req.method.toLowerCase();
  const url = req.baseUrl || req.url || 'https://api.example.com/endpoint';
  const activeHeaders = req.headers.filter(h => h.enabled && h.name.toLowerCase() !== 'content-length');
  const activeParams = req.queryParams.filter(p => p.enabled);

  const lines = ['import requests', ''];

  // Query Params
  if (activeParams.length > 0) {
    lines.push('params = {');
    activeParams.forEach(p => {
      lines.push(`    "${p.key}": "${p.value.replace(/"/g, '\\"')}",`);
    });
    lines.push('}');
    lines.push('');
  }

  // Headers
  if (activeHeaders.length > 0) {
    lines.push('headers = {');
    activeHeaders.forEach(h => {
      lines.push(`    "${h.name}": "${h.value.replace(/"/g, '\\"')}",`);
    });
    lines.push('}');
    lines.push('');
  }

  // Body / Payload
  let bodyArg = '';
  if (req.body.type === 'json' && req.body.json) {
    lines.push(`json_data = ${formatPythonDict(req.body.json, 4)}`);
    lines.push('');
    bodyArg = 'json=json_data, ';
  } else if (req.body.type === 'url-encoded' && req.body.urlEncoded.length > 0) {
    lines.push('data = {');
    req.body.urlEncoded.filter(u => u.enabled).forEach(u => {
      lines.push(`    "${u.key}": "${u.value.replace(/"/g, '\\"')}",`);
    });
    lines.push('}');
    lines.push('');
    bodyArg = 'data=data, ';
  } else if (req.body.type === 'form-data' && req.body.formData.length > 0) {
    lines.push('files = {');
    req.body.formData.filter(f => f.enabled).forEach(f => {
      if (f.type === 'file') {
        lines.push(`    "${f.key}": open("${f.value}", "rb"),`);
      } else {
        lines.push(`    "${f.key}": (None, "${f.value.replace(/"/g, '\\"')}"),`);
      }
    });
    lines.push('}');
    lines.push('');
    bodyArg = 'files=files, ';
  } else if (req.body.raw) {
    lines.push(`data = """${req.body.raw}"""`);
    lines.push('');
    bodyArg = 'data=data, ';
  }

  // Auth
  let authArg = '';
  if (req.auth && req.auth.type === 'basic' && req.auth.username) {
    authArg = `auth=("${req.auth.username}", "${req.auth.password}"), `;
  }

  // Build requests call
  const callArgs = [
    `"${url}"`,
    activeParams.length > 0 ? 'params=params' : '',
    activeHeaders.length > 0 ? 'headers=headers' : '',
    bodyArg.trim().replace(/,$/, ''),
    authArg.trim().replace(/,$/, ''),
    req.options.timeout ? `timeout=${req.options.timeout}` : ''
  ].filter(Boolean);

  lines.push(`response = requests.${method}(`);
  callArgs.forEach((arg, idx) => {
    lines.push(`    ${arg}${idx === callArgs.length - 1 ? '' : ','}`);
  });
  lines.push(')');
  lines.push('');
  lines.push('print("Status Code:", response.status_code)');
  lines.push('try:');
  lines.push('    print("Response JSON:", response.json())');
  lines.push('except Exception:');
  lines.push('    print("Response Body:", response.text)');

  return lines.join('\n');
}

function formatPythonDict(obj, indent = 4) {
  const spaces = ' '.repeat(indent);
  if (obj === null) return 'None';
  if (typeof obj === 'boolean') return obj ? 'True' : 'False';
  if (typeof obj === 'number') return obj.toString();
  if (typeof obj === 'string') return `"${obj.replace(/"/g, '\\"')}"`;
  if (Array.isArray(obj)) {
    if (obj.length === 0) return '[]';
    const items = obj.map(item => `${spaces}    ${formatPythonDict(item, indent + 4)}`).join(',\n');
    return `[\n${items}\n${spaces}]`;
  }
  if (typeof obj === 'object') {
    const keys = Object.keys(obj);
    if (keys.length === 0) return '{}';
    const entries = keys.map(k => `${spaces}    "${k}": ${formatPythonDict(obj[k], indent + 4)}`).join(',\n');
    return `{\n${entries}\n${spaces}}`;
  }
  return String(obj);
}
