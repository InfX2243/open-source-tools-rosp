export function generateNodeFetch(req) {
  const method = req.method.toUpperCase();
  const url = req.url || 'https://api.example.com/endpoint';
  const activeHeaders = req.headers.filter(h => h.enabled);

  const lines = [
    `// Node.js 18+ includes native global fetch`,
    ``
  ];

  const hasHeaders = activeHeaders.length > 0;
  if (hasHeaders) {
    lines.push(`const headers = new Headers();`);
    activeHeaders.forEach(h => {
      lines.push(`headers.append('${h.name}', '${h.value.replace(/'/g, "\\'")}');`);
    });
    lines.push(``);
  }

  let bodyCode = null;
  if (req.body.type === 'json' && req.body.json) {
    bodyCode = `JSON.stringify(${JSON.stringify(req.body.json, null, 2)})`;
  } else if (req.body.raw) {
    bodyCode = JSON.stringify(req.body.raw);
  }

  lines.push(`const requestOptions = {`);
  lines.push(`  method: '${method}',`);
  if (hasHeaders) lines.push(`  headers: headers,`);
  if (bodyCode) lines.push(`  body: ${bodyCode},`);
  lines.push(`  redirect: '${req.options.followRedirects ? 'follow' : 'manual'}'`);
  lines.push(`};`);
  lines.push(``);
  lines.push(`fetch('${url}', requestOptions)`);
  lines.push(`  .then(response => response.text())`);
  lines.push(`  .then(result => console.log(result))`);
  lines.push(`  .catch(error => console.error('Error:', error));`);

  return lines.join('\n');
}
