export function generateHttpie(req) {
  const method = req.method.toUpperCase();
  const url = req.url || 'https://api.example.com/endpoint';
  const activeHeaders = req.headers.filter(h => h.enabled);

  const parts = ['http', method !== 'GET' ? method : '', `'${url}'`].filter(Boolean);

  // Headers
  activeHeaders.forEach(h => {
    parts.push(`'${h.name}:${h.value.replace(/'/g, "\\'")}'`);
  });

  // Auth
  if (req.auth && req.auth.type === 'basic' && req.auth.username) {
    parts.push(`-a '${req.auth.username}:${req.auth.password}'`);
  }

  // JSON Body
  if (req.body.type === 'json' && req.body.json) {
    for (const [k, v] of Object.entries(req.body.json)) {
      if (typeof v === 'string') {
        parts.push(`${k}='${v}'`);
      } else {
        parts.push(`${k}:=${JSON.stringify(v)}`);
      }
    }
  } else if (req.body.raw) {
    return `echo '${req.body.raw.replace(/'/g, "\\'")}' | ${parts.join(' ')}`;
  }

  return parts.join(' \\\n  ');
}
