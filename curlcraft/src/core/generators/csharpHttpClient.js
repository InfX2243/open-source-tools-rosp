export function generateCsharpHttpClient(req) {
  const method = req.method.toUpperCase();
  const url = req.url || 'https://api.example.com/endpoint';
  const activeHeaders = req.headers.filter(h => h.enabled && h.name.toLowerCase() !== 'content-type');
  const contentTypeHeader = req.headers.find(h => h.name.toLowerCase() === 'content-type');
  const contentType = contentTypeHeader ? contentTypeHeader.value : 'application/json';

  const lines = [
    `using System;`,
    `using System.Net.Http;`,
    `using System.Text;`,
    `using System.Threading.Tasks;`,
    ``,
    `class Program`,
    `{`,
    `    static async Task Main()`,
    `    {`,
    `        using var client = new HttpClient();`,
    `        using var request = new HttpRequestMessage(HttpMethod.${capitalize(method)}, "${url}");`,
    ``
  ];

  if (activeHeaders.length > 0) {
    activeHeaders.forEach(h => {
      lines.push(`        request.Headers.TryAddWithoutValidation("${h.name}", "${h.value.replace(/"/g, '\\"')}");`);
    });
    lines.push(``);
  }

  if (['POST', 'PUT', 'PATCH'].includes(method)) {
    if (req.body.type === 'json' && req.body.json) {
      lines.push(`        request.Content = new StringContent("${JSON.stringify(req.body.json).replace(/"/g, '\\"')}", Encoding.UTF8, "${contentType}");`);
    } else if (req.body.raw) {
      lines.push(`        request.Content = new StringContent("${req.body.raw.replace(/"/g, '\\"')}", Encoding.UTF8, "${contentType}");`);
    }
    lines.push(``);
  }

  lines.push(`        using var response = await client.SendAsync(request);`);
  lines.push(`        var responseBody = await response.Content.ReadAsStringAsync();`);
  lines.push(``);
  lines.push(`        Console.WriteLine($"Status: {response.StatusCode}");`);
  lines.push(`        Console.WriteLine($"Body: {responseBody}");`);
  lines.push(`    }`);
  lines.push(`}`);

  return lines.join('\n');
}

function capitalize(s) {
  if (!s) return 'Get';
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
}
