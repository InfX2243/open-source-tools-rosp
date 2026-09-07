export function generateFetch(req) {
  const method = req.method.toUpperCase();
  const url = req.url || 'https://api.example.com/endpoint';
  const activeHeaders = req.headers.filter(h => h.enabled);

  const lines = [];

  // Build headers object
  const hasHeaders = activeHeaders.length > 0;
  if (hasHeaders) {
    lines.push(`const headers = {`);
    activeHeaders.forEach(h => {
      lines.push(`  '${h.name}': '${h.value.replace(/'/g, "\\'")}',`);
    });
    lines.push(`};`);
    lines.push(``);
  }

  // Build body
  let bodyCode = null;
  if (req.body.type === 'json' && req.body.json) {
    bodyCode = `JSON.stringify(${JSON.stringify(req.body.json, null, 2)})`;
  } else if (req.body.type === 'form-data' && req.body.formData.length > 0) {
    lines.push(`const formData = new FormData();`);
    req.body.formData.filter(f => f.enabled).forEach(f => {
      if (f.type === 'file') {
        lines.push(`// formData.append('${f.key}', fileInput.files[0], '${f.value}');`);
      } else {
        lines.push(`formData.append('${f.key}', '${f.value.replace(/'/g, "\\'")}');`);
      }
    });
    lines.push(``);
    bodyCode = `formData`;
  } else if (req.body.type === 'url-encoded' && req.body.urlEncoded.length > 0) {
    lines.push(`const body = new URLSearchParams({`);
    req.body.urlEncoded.filter(u => u.enabled).forEach(u => {
      lines.push(`  '${u.key}': '${u.value.replace(/'/g, "\\'")}',`);
    });
    lines.push(`}).toString();`);
    lines.push(``);
    bodyCode = `body`;
  } else if (req.body.raw) {
    bodyCode = JSON.stringify(req.body.raw);
  }

  // Options object
  const options = [];
  if (method !== 'GET') {
    options.push(`  method: '${method}',`);
  }
  if (hasHeaders) {
    options.push(`  headers,`);
  }
  if (bodyCode) {
    options.push(`  body: ${bodyCode},`);
  }

  // Assemble full fetch snippet
  lines.push(`async function makeRequest() {`);
  lines.push(`  try {`);
  if (options.length > 0) {
    lines.push(`    const response = await fetch('${url}', {`);
    options.forEach(opt => lines.push(`    ${opt}`));
    lines.push(`    });`);
  } else {
    lines.push(`    const response = await fetch('${url}');`);
  }
  lines.push(``);
  lines.push(`    if (!response.ok) {`);
  lines.push(`      throw new Error(\`HTTP error! status: \${response.status}\`);`);
  lines.push(`    }`);
  lines.push(``);
  lines.push(`    const data = await response.json();`);
  lines.push(`    console.log(data);`);
  lines.push(`    return data;`);
  lines.push(`  } catch (error) {`);
  lines.push(`    console.error('Request failed:', error);`);
  lines.push(`  }`);
  lines.push(`}`);
  lines.push(``);
  lines.push(`makeRequest();`);

  return lines.join('\n');
}
