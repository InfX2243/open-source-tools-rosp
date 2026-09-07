export function generatePhpCurl(req) {
  const method = req.method.toUpperCase();
  const url = req.url || 'https://api.example.com/endpoint';
  const activeHeaders = req.headers.filter(h => h.enabled);

  const lines = [
    `<?php`,
    ``,
    `$curl = curl_init();`,
    ``
  ];

  const headersArray = activeHeaders.map(h => `    '${h.name}: ${h.value.replace(/'/g, "\\'")}'`);

  lines.push(`curl_setopt_array($curl, array(`);
  lines.push(`  CURLOPT_URL => '${url}',`);
  lines.push(`  CURLOPT_RETURNTRANSFER => true,`);
  lines.push(`  CURLOPT_ENCODING => '',`);
  lines.push(`  CURLOPT_MAXREDIRS => 10,`);
  lines.push(`  CURLOPT_TIMEOUT => 0,`);
  lines.push(`  CURLOPT_FOLLOWLOCATION => ${req.options.followRedirects ? 'true' : 'false'},`);
  lines.push(`  CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,`);
  lines.push(`  CURLOPT_CUSTOMREQUEST => '${method}',`);

  if (req.body.type === 'json' && req.body.json) {
    lines.push(`  CURLOPT_POSTFIELDS => '${JSON.stringify(req.body.json).replace(/'/g, "\\'")}',`);
  } else if (req.body.raw) {
    lines.push(`  CURLOPT_POSTFIELDS => '${req.body.raw.replace(/'/g, "\\'")}',`);
  }

  if (headersArray.length > 0) {
    lines.push(`  CURLOPT_HTTPHEADER => array(`);
    headersArray.forEach((h, idx) => {
      lines.push(`    ${h}${idx === headersArray.length - 1 ? '' : ','}`);
    });
    lines.push(`  ),`);
  }

  lines.push(`));`);
  lines.push(``);
  lines.push(`$response = curl_exec($curl);`);
  lines.push(`$err = curl_error($curl);`);
  lines.push(``);
  lines.push(`curl_close($curl);`);
  lines.push(``);
  lines.push(`if ($err) {`);
  lines.push(`  echo "cURL Error #:" . $err;`);
  lines.push(`} else {`);
  lines.push(`  echo $response;`);
  lines.push(`}`);

  return lines.join('\n');
}
