import { toPascalCase } from '../svgParser';

export function generateReactJsx(parsed, options = {}) {
  const {
    componentName = 'SvgIcon',
    isMemo = false,
    isForwardRef = false,
    isDefaultExport = true,
    includePropTypes = false
  } = options;

  const name = toPascalCase(componentName);
  const viewBox = parsed.viewBox || '0 0 24 24';

  const lines = [`import React from 'react';`, ``];

  let componentDef = '';

  if (isForwardRef) {
    componentDef = `export const ${name} = React.forwardRef(({ size = 24, color = 'currentColor', className = '', style, ...props }, ref) => (
  <svg
    ref={ref}
    width={size}
    height={size}
    viewBox="${viewBox}"
    fill={color}
    className={className}
    style={style}
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    ${parsed.innerJsx.replace(/\n/g, '\n    ')}
  </svg>
));

${name}.displayName = '${name}';`;
  } else if (isMemo) {
    componentDef = `export const ${name} = React.memo(({ size = 24, color = 'currentColor', className = '', style, ...props }) => (
  <svg
    width={size}
    height={size}
    viewBox="${viewBox}"
    fill={color}
    className={className}
    style={style}
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    ${parsed.innerJsx.replace(/\n/g, '\n    ')}
  </svg>
));

${name}.displayName = '${name}';`;
  } else {
    componentDef = `export function ${name}({ size = 24, color = 'currentColor', className = '', style, ...props }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="${viewBox}"
      fill={color}
      className={className}
      style={style}
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      ${parsed.innerJsx.replace(/\n/g, '\n      ')}
    </svg>
  );
}`;
  }

  lines.push(componentDef);

  if (isDefaultExport) {
    lines.push(``);
    lines.push(`export default ${name};`);
  }

  return lines.join('\n');
}
