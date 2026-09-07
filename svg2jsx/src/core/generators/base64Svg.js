import { generateMinifiedSvg } from './minifiedSvg';

export function generateBase64Svg(parsed) {
  const minified = generateMinifiedSvg(parsed);
  let base64 = '';

  try {
    base64 = btoa(unescape(encodeURIComponent(minified)));
  } catch {
    base64 = btoa(minified);
  }

  const dataUri = `data:image/svg+xml;base64,${base64}`;

  const lines = [
    `<!-- HTML <img> Tag -->`,
    `<img src="${dataUri}" alt="icon" width="${parsed.width || 24}" height="${parsed.height || 24}" />`,
    ``,
    `/* CSS Base64 Background */`,
    `.icon-base64 {`,
    `  background-image: url("${dataUri}");`,
    `}`,
    ``,
    `// Raw Base64 Data URI:`,
    `${dataUri}`
  ];

  return lines.join('\n');
}
