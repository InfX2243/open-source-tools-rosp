export function generateAxios(req) {
  const method = req.method.toLowerCase();
  const url = req.baseUrl || req.url || 'https://api.example.com/endpoint';
  const activeHeaders = req.headers.filter(h => h.enabled && h.name.toLowerCase() !== 'content-length');
  const activeParams = req.queryParams.filter(p => p.enabled);

  const lines = [`import axios from 'axios';`, ``];

  // Config object
  const configProps = [];

  // Params
  if (activeParams.length > 0) {
    const paramsObj = {};
    activeParams.forEach(p => { paramsObj[p.key] = p.value; });
    configProps.push(`  params: ${JSON.stringify(paramsObj, null, 4).replace(/\n/g, '\n  ')}`);
  }

  // Headers
  if (activeHeaders.length > 0) {
    const headersObj = {};
    activeHeaders.forEach(h => { headersObj[h.name] = h.value; });
    configProps.push(`  headers: ${JSON.stringify(headersObj, null, 4).replace(/\n/g, '\n  ')}`);
  }

  // Data
  let dataVal = null;
  if (req.body.type === 'json' && req.body.json) {
    dataVal = JSON.stringify(req.body.json, null, 4);
  } else if (req.body.type === 'url-encoded' && req.body.urlEncoded.length > 0) {
    const urlObj = {};
    req.body.urlEncoded.filter(u => u.enabled).forEach(u => { urlObj[u.key] = u.value; });
    lines.push(`const data = new URLSearchParams(${JSON.stringify(urlObj, null, 2)});`);
    lines.push(``);
    dataVal = `data`;
  } else if (req.body.raw) {
    dataVal = JSON.stringify(req.body.raw);
  }

  lines.push(`async function makeRequest() {`);
  lines.push(`  try {`);

  if (['post', 'put', 'patch'].includes(method)) {
    if (configProps.length > 0) {
      lines.push(`    const response = await axios.${method}('${url}', ${dataVal || 'null'}, {`);
      configProps.forEach((prop, idx) => {
        lines.push(`    ${prop}${idx === configProps.length - 1 ? '' : ','}`);
      });
      lines.push(`    });`);
    } else {
      lines.push(`    const response = await axios.${method}('${url}'${dataVal ? `, ${dataVal}` : ''});`);
    }
  } else if (method === 'get' || method === 'delete' || method === 'head') {
    if (configProps.length > 0) {
      lines.push(`    const response = await axios.${method}('${url}', {`);
      configProps.forEach((prop, idx) => {
        lines.push(`    ${prop}${idx === configProps.length - 1 ? '' : ','}`);
      });
      lines.push(`    });`);
    } else {
      lines.push(`    const response = await axios.${method}('${url}');`);
    }
  } else {
    // Generic axios(config)
    lines.push(`    const response = await axios({`);
    lines.push(`      method: '${method}',`);
    lines.push(`      url: '${url}',`);
    if (dataVal) lines.push(`      data: ${dataVal},`);
    configProps.forEach(prop => lines.push(`    ${prop},`));
    lines.push(`    });`);
  }

  lines.push(``);
  lines.push(`    console.log(response.status);`);
  lines.push(`    console.log(response.data);`);
  lines.push(`    return response.data;`);
  lines.push(`  } catch (error) {`);
  lines.push(`    if (error.response) {`);
  lines.push(`      console.error('Response error:', error.response.status, error.response.data);`);
  lines.push(`    } else {`);
  lines.push(`      console.error('Request error:', error.message);`);
  lines.push(`    }`);
  lines.push(`  }`);
  lines.push(`}`);
  lines.push(``);
  lines.push(`makeRequest();`);

  return lines.join('\n');
}
