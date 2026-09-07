export function generateGoHttp(req) {
  const method = req.method.toUpperCase();
  const url = req.url || 'https://api.example.com/endpoint';
  const activeHeaders = req.headers.filter(h => h.enabled);

  const lines = [
    `package main`,
    ``,
    `import (`,
    `\t"fmt"`,
    `\t"io"`,
    `\t"net/http"`
  ];

  let hasBody = false;
  let bodyStr = '';
  if (req.body.type === 'json' && req.body.json) {
    hasBody = true;
    bodyStr = JSON.stringify(req.body.json);
    lines.push(`\t"strings"`);
  } else if (req.body.raw) {
    hasBody = true;
    bodyStr = req.body.raw;
    lines.push(`\t"strings"`);
  }

  lines.push(`)`);
  lines.push(``);
  lines.push(`func main() {`);
  lines.push(`\tclient := &http.Client{}`);
  lines.push(``);

  if (hasBody) {
    lines.push(`\tvar data = strings.NewReader(\`${bodyStr}\`)`);
    lines.push(`\treq, err := http.NewRequest("${method}", "${url}", data)`);
  } else {
    lines.push(`\treq, err := http.NewRequest("${method}", "${url}", nil)`);
  }

  lines.push(`\tif err != nil {`);
  lines.push(`\t\tpanic(err)`);
  lines.push(`\t}`);
  lines.push(``);

  if (activeHeaders.length > 0) {
    activeHeaders.forEach(h => {
      lines.push(`\treq.Header.Set("${h.name}", "${h.value.replace(/"/g, '\\"')}")`);
    });
    lines.push(``);
  }

  if (req.auth && req.auth.type === 'basic' && req.auth.username) {
    lines.push(`\treq.SetBasicAuth("${req.auth.username}", "${req.auth.password}")`);
    lines.push(``);
  }

  lines.push(`\tresp, err := client.Do(req)`);
  lines.push(`\tif err != nil {`);
  lines.push(`\t\tpanic(err)`);
  lines.push(`\t}`);
  lines.push(`\tdefer resp.Body.Close()`);
  lines.push(``);
  lines.push(`\tbodyText, err := io.ReadAll(resp.Body)`);
  lines.push(`\tif err != nil {`);
  lines.push(`\t\tpanic(err)`);
  lines.push(`\t}`);
  lines.push(`\tfmt.Printf("Status: %s\\n", resp.Status)`);
  lines.push(`\tfmt.Printf("Response: %s\\n", bodyText)`);
  lines.push(`}`);

  return lines.join('\n');
}
