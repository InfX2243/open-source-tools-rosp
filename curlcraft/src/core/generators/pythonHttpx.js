export function generatePythonHttpx(req) {
  const method = req.method.toLowerCase();
  const url = req.baseUrl || req.url || 'https://api.example.com/endpoint';
  const activeHeaders = req.headers.filter(h => h.enabled && h.name.toLowerCase() !== 'content-length');
  const activeParams = req.queryParams.filter(p => p.enabled);

  const lines = ['import asyncio', 'import httpx', ''];

  lines.push('async function_make_request():');
  const fnIndent = '    ';

  if (activeParams.length > 0) {
    lines.push(`${fnIndent}params = {`);
    activeParams.forEach(p => {
      lines.push(`${fnIndent}    "${p.key}": "${p.value.replace(/"/g, '\\"')}",`);
    });
    lines.push(`${fnIndent}}`);
    lines.push('');
  }

  if (activeHeaders.length > 0) {
    lines.push(`${fnIndent}headers = {`);
    activeHeaders.forEach(h => {
      lines.push(`${fnIndent}    "${h.name}": "${h.value.replace(/"/g, '\\"')}",`);
    });
    lines.push(`${fnIndent}}`);
    lines.push('');
  }

  let bodyArg = '';
  if (req.body.type === 'json' && req.body.json) {
    lines.push(`${fnIndent}json_data = ${JSON.stringify(req.body.json, null, 4).replace(/\n/g, '\n' + fnIndent)}`);
    lines.push('');
    bodyArg = 'json=json_data, ';
  } else if (req.body.raw) {
    lines.push(`${fnIndent}content = """${req.body.raw}"""`);
    lines.push('');
    bodyArg = 'content=content, ';
  }

  const callArgs = [
    `"${url}"`,
    activeParams.length > 0 ? 'params=params' : '',
    activeHeaders.length > 0 ? 'headers=headers' : '',
    bodyArg.trim().replace(/,$/, '')
  ].filter(Boolean);

  lines.push(`${fnIndent}async with httpx.AsyncClient() as client:`);
  lines.push(`${fnIndent}    response = await client.${method}(`);
  callArgs.forEach((arg, idx) => {
    lines.push(`${fnIndent}        ${arg}${idx === callArgs.length - 1 ? '' : ','}`);
  });
  lines.push(`${fnIndent}    )`);
  lines.push(`${fnIndent}    print("Status:", response.status_code)`);
  lines.push(`${fnIndent}    print("Body:", response.text)`);
  lines.push('');
  lines.push('asyncio.run(function_make_request())');

  return lines.join('\n');
}
