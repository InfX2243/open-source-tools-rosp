export function generateJavaHttpClient(req) {
  const method = req.method.toUpperCase();
  const url = req.url || 'https://api.example.com/endpoint';
  const activeHeaders = req.headers.filter(h => h.enabled);

  const lines = [
    `import java.io.IOException;`,
    `import java.net.URI;`,
    `import java.net.http.HttpClient;`,
    `import java.net.http.HttpRequest;`,
    `import java.net.http.HttpResponse;`,
    ``,
    `public class Main {`,
    `    public static void main(String[] args) throws IOException, InterruptedException {`,
    `        HttpClient client = HttpClient.newHttpClient();`,
    ``,
    `        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()`,
    `                .uri(URI.create("${url}"));`
  ];

  if (activeHeaders.length > 0) {
    activeHeaders.forEach(h => {
      lines.push(`        requestBuilder.header("${h.name}", "${h.value.replace(/"/g, '\\"')}");`);
    });
  }

  let bodyPublisher = 'HttpRequest.BodyPublishers.noBody()';
  if (req.body.type === 'json' && req.body.json) {
    bodyPublisher = `HttpRequest.BodyPublishers.ofString("${JSON.stringify(req.body.json).replace(/"/g, '\\"')}")`;
  } else if (req.body.raw) {
    bodyPublisher = `HttpRequest.BodyPublishers.ofString("${req.body.raw.replace(/"/g, '\\"')}")`;
  }

  if (method === 'GET') {
    lines.push(`        requestBuilder.GET();`);
  } else if (method === 'POST') {
    lines.push(`        requestBuilder.POST(${bodyPublisher});`);
  } else if (method === 'PUT') {
    lines.push(`        requestBuilder.PUT(${bodyPublisher});`);
  } else if (method === 'DELETE') {
    lines.push(`        requestBuilder.DELETE();`);
  } else {
    lines.push(`        requestBuilder.method("${method}", ${bodyPublisher});`);
  }

  lines.push(``);
  lines.push(`        HttpRequest request = requestBuilder.build();`);
  lines.push(`        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());`);
  lines.push(``);
  lines.push(`        System.out.println("Status: " + response.statusCode());`);
  lines.push(`        System.out.println("Body: " + response.body());`);
  lines.push(`    }`);
  lines.push(`}`);

  return lines.join('\n');
}
