export function encodeSvgForDataUri(svgString) {
  if (!svgString) return '';

  return svgString
    .replace(/[\n\r\t]+/g, ' ')
    .replace(/\s{2,}/g, ' ')
    .replace(/"/g, "'")
    .replace(/%/g, '%25')
    .replace(/#/g, '%23')
    .replace(/\{/g, '%7B')
    .replace(/\}/g, '%7D')
    .replace(/</g, '%3C')
    .replace(/>/g, '%3E')
    .replace(/\s/g, '%20');
}

export function generateCssDataUri(parsed, options = {}) {
  const { className = 'svg-icon-bg' } = options;
  const rawSvg = parsed.cleanedSvg;
  const encoded = encodeSvgForDataUri(rawSvg);
  const dataUri = `data:image/svg+xml,${encoded}`;

  const lines = [
    `/* CSS Background Data-URI */`,
    `.${className} {`,
    `  width: ${parsed.width || 24}px;`,
    `  height: ${parsed.height || 24}px;`,
    `  background-image: url("${dataUri}");`,
    `  background-repeat: no-repeat;`,
    `  background-size: contain;`,
    `  background-position: center;`,
    `  display: inline-block;`,
    `}`,
    ``,
    `/* CSS Mask (Enables dynamic color changes via background-color) */`,
    `.${className}-mask {`,
    `  width: ${parsed.width || 24}px;`,
    `  height: ${parsed.height || 24}px;`,
    `  background-color: currentColor;`,
    `  -webkit-mask-image: url("${dataUri}");`,
    `  mask-image: url("${dataUri}");`,
    `  -webkit-mask-repeat: no-repeat;`,
    `  mask-repeat: no-repeat;`,
    `  -webkit-mask-size: contain;`,
    `  mask-size: contain;`,
    `  -webkit-mask-position: center;`,
    `  mask-position: center;`,
    `  display: inline-block;`,
    `}`
  ];

  return lines.join('\n');
}
