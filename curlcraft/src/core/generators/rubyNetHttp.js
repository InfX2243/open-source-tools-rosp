export function generateRubyNetHttp(req) {
  const method = req.method.toUpperCase();
  const url = req.url || 'https://api.example.com/endpoint';
  const activeHeaders = req.headers.filter(h => h.enabled);

  const lines = [
    `require 'net/http'`,
    `require 'uri'`,
    `require 'json'`,
    ``,
    `uri = URI.parse('${url}')`,
    `http = Net::HTTP.new(uri.host, uri.port)`,
    `http.use_ssl = (uri.scheme == 'https')`,
    ``
  ];

  const rubyMethodMap = {
    'GET': 'Net::HTTP::Get',
    'POST': 'Net::HTTP::Post',
    'PUT': 'Net::HTTP::Put',
    'DELETE': 'Net::HTTP::Delete',
    'PATCH': 'Net::HTTP::Patch',
    'HEAD': 'Net::HTTP::Head'
  };

  const reqClass = rubyMethodMap[method] || 'Net::HTTP::Get';
  lines.push(`request = ${reqClass}.new(uri.request_uri)`);

  if (activeHeaders.length > 0) {
    activeHeaders.forEach(h => {
      lines.push(`request['${h.name}'] = '${h.value.replace(/'/g, "\\'")}'`);
    });
  }

  if (['POST', 'PUT', 'PATCH'].includes(method)) {
    if (req.body.type === 'json' && req.body.json) {
      lines.push(`request.body = JSON.dump(${JSON.stringify(req.body.json)})`);
    } else if (req.body.raw) {
      lines.push(`request.body = '${req.body.raw.replace(/'/g, "\\'")}'`);
    }
  }

  lines.push(``);
  lines.push(`response = http.request(request)`);
  lines.push(`puts "Status: #{response.code}"`);
  lines.push(`puts "Body: #{response.body}"`);

  return lines.join('\n');
}
