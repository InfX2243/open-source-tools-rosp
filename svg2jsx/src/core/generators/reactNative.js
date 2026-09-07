import { toPascalCase } from '../svgParser';

export function generateReactNative(parsed, options = {}) {
  const { componentName = 'SvgIcon', isDefaultExport = true } = options;
  const name = toPascalCase(componentName);
  const viewBox = parsed.viewBox || '0 0 24 24';

  // Capitalize all SVG tag names for React Native SVG
  const tagMap = {
    path: 'Path',
    circle: 'Circle',
    rect: 'Rect',
    line: 'Line',
    polygon: 'Polygon',
    polyline: 'Polyline',
    ellipse: 'Ellipse',
    g: 'G',
    defs: 'Defs',
    clipPath: 'ClipPath',
    linearGradient: 'LinearGradient',
    radialGradient: 'RadialGradient',
    stop: 'Stop',
    text: 'Text',
    tspan: 'TSpan'
  };

  const usedTags = new Set(['Svg']);
  let rnInner = parsed.innerJsx;

  for (const [tag, RnTag] of Object.entries(tagMap)) {
    const regexOpen = new RegExp(`<${tag}(\\s|>)`, 'gi');
    const regexClose = new RegExp(`</${tag}>`, 'gi');

    if (regexOpen.test(rnInner) || regexClose.test(rnInner)) {
      usedTags.add(RnTag);
      rnInner = rnInner
        .replace(new RegExp(`<${tag}(\\s|>)`, 'gi'), `<${RnTag}$1`)
        .replace(new RegExp(`</${tag}>`, 'gi'), `</${RnTag}>`);
    }
  }

  const importsList = Array.from(usedTags).join(', ');

  const lines = [
    `import React from 'react';`,
    `import Svg, { ${importsList} } from 'react-native-svg';`,
    ``,
    `export function ${name}({ size = 24, color = '#000000', ...props }) {`,
    `  return (`,
    `    <Svg width={size} height={size} viewBox="${viewBox}" fill={color} {...props}>`,
    `      ${rnInner.replace(/\n/g, '\n      ')}`,
    `    </Svg>`,
    `  );`,
    `}`
  ];

  if (isDefaultExport) {
    lines.push(``);
    lines.push(`export default ${name};`);
  }

  return lines.join('\n');
}
