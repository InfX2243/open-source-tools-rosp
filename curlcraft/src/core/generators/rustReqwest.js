export function generateRustReqwest(req) {
  const method = req.method.toLowerCase();
  const url = req.baseUrl || req.url || 'https://api.example.com/endpoint';
  const activeHeaders = req.headers.filter(h => h.enabled && h.name.toLowerCase() !== 'content-length');

  const lines = [
    `// Add to Cargo.toml:`,
    `// [dependencies]`,
    `// reqwest = { version = "0.11", features = ["json"] }`,
    `// tokio = { version = "1", features = ["full"] }`,
    ``,
    `use reqwest::header::{HeaderMap, HeaderValue, HeaderName};`,
    `use std::str::FromStr;`,
    ``,
    `#[tokio::main]`,
    `async fn main() -> Result<(), Box<dyn std::error::Error>> {`,
    `    let client = reqwest::Client::new();`,
    ``
  ];

  if (activeHeaders.length > 0) {
    lines.push(`    let mut headers = HeaderMap::new();`);
    activeHeaders.forEach(h => {
      lines.push(`    headers.insert(HeaderName::from_str("${h.name}")?, HeaderValue::from_static("${h.value.replace(/"/g, '\\"')}"));`);
    });
    lines.push(``);
  }

  lines.push(`    let response = client.${method}("${url}")`);
  if (activeHeaders.length > 0) {
    lines.push(`        .headers(headers)`);
  }

  if (req.body.type === 'json' && req.body.json) {
    lines.push(`        .body(r#"${JSON.stringify(req.body.json)}"#)`);
  } else if (req.body.raw) {
    lines.push(`        .body(r#"${req.body.raw}"#)`);
  }

  if (req.auth && req.auth.type === 'basic' && req.auth.username) {
    lines.push(`        .basic_auth("${req.auth.username}", Some("${req.auth.password}"))`);
  }

  lines.push(`        .send()`);
  lines.push(`        .await?;`);
  lines.push(``);
  lines.push(`    println!("Status: {}", response.status());`);
  lines.push(`    let body = response.text().await?;`);
  lines.push(`    println!("Response: {}", body);`);
  lines.push(`    Ok(())`);
  lines.push(`}`);

  return lines.join('\n');
}
