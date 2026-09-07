/**
 * SVG Parser & Transformer Engine for svg2jsx
 */

// SVG attribute name mappings for React JSX/TSX
export const SVG_ATTR_MAP = {
  'class': 'className',
  'for': 'htmlFor',
  'clip-path': 'clipPath',
  'clip-rule': 'clipRule',
  'fill-rule': 'fillRule',
  'fill-opacity': 'fillOpacity',
  'stroke-width': 'strokeWidth',
  'stroke-linecap': 'strokeLinecap',
  'stroke-linejoin': 'strokeLinejoin',
  'stroke-miterlimit': 'strokeMiterlimit',
  'stroke-opacity': 'strokeOpacity',
  'stroke-dasharray': 'strokeDasharray',
  'stroke-dashoffset': 'strokeDashoffset',
  'stop-color': 'stopColor',
  'stop-opacity': 'stopOpacity',
  'font-size': 'fontSize',
  'font-family': 'fontFamily',
  'font-weight': 'fontWeight',
  'letter-spacing': 'letterSpacing',
  'text-anchor': 'textAnchor',
  'xlink:href': 'href',
  'xmlns:xlink': null, // Remove
  'xml:space': null,   // Remove
  'enable-background': null,
  'version': null,
  'baseprofile': null,
  'tabindex': 'tabIndex'
};

// Converts style string "fill: red; stroke-width: 2px" to JSX object string "{{ fill: 'red', strokeWidth: '2px' }}"
export function convertStyleStringToJsx(styleStr) {
  if (!styleStr) return null;
  const declarations = styleStr.split(';').filter(Boolean);
  const obj = {};

  declarations.forEach(dec => {
    const colonIdx = dec.indexOf(':');
    if (colonIdx > 0) {
      let key = dec.slice(0, colonIdx).trim();
      const val = dec.slice(colonIdx + 1).trim();

      // Convert kebab-case css property to camelCase
      key = key.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      obj[key] = val;
    }
  });

  return JSON.stringify(obj).replace(/"([^"]+)":/g, '$1:');
}

// Convert kebab-case or snake_case string to PascalCase component name
export function toPascalCase(str) {
  if (!str) return 'SvgIcon';
  return str
    .replace(/[-_.\s]+(.)?/g, (_, c) => (c ? c.toUpperCase() : ''))
    .replace(/^[a-z]/, c => c.toUpperCase())
    .replace(/[^a-zA-Z0-9]/g, '') || 'SvgIcon';
}

// Clean and minify raw SVG
export function cleanRawSvg(raw) {
  if (!raw || typeof raw !== 'string') return '';

  return raw
    .replace(/<\?xml[\s\S]*?\?>/gi, '')         // XML declaration
    .replace(/<!DOCTYPE[\s\S]*?>/gi, '')         // DOCTYPE
    .replace(/<!--[\s\S]*?-->/g, '')             // Comments
    .replace(/<metadata[\s\S]*?<\/metadata>/gi, '') // Metadata tags
    .replace(/sodipodi:[a-z]+="[^"]*"/gi, '')   // Inkscape sodipodi
    .replace(/inkscape:[a-z]+="[^"]*"/gi, '')   // Inkscape attrs
    .replace(/sketch:type="[^"]*"/gi, '')       // Sketch attrs
    .replace(/xmlns:sketch="[^"]*"/gi, '')      // Sketch namespace
    .replace(/xmlns:xlink="[^"]*"/gi, '')       // XLink namespace
    .replace(/xml:space="[^"]*"/gi, '')         // XML space
    .replace(/\s+/g, ' ')                       // Collapse multiple spaces
    .trim();
}

/**
 * Parses raw SVG and extracts viewBox, dimensions, and sanitized JSX body
 */
export function parseSvg(rawSvg, options = {}) {
  const {
    useCurrentColor = false,
    componentName = 'SvgIcon'
  } = options;

  const result = {
    isValid: false,
    raw: rawSvg,
    cleanedSvg: '',
    viewBox: '0 0 24 24',
    width: '24',
    height: '24',
    jsxBody: '',
    innerJsx: '',
    reactNativeBody: '',
    error: null
  };

  if (!rawSvg || !rawSvg.trim()) {
    return result;
  }

  const cleaned = cleanRawSvg(rawSvg);
  if (!cleaned.includes('<svg')) {
    result.error = 'No <svg> root element found in input.';
    return result;
  }

  result.cleanedSvg = cleaned;

  // Extract <svg ...> attributes
  const svgMatch = cleaned.match(/<svg([^>]*)>([\s\S]*?)<\/svg>/i);
  if (!svgMatch) {
    result.error = 'Invalid SVG markup structure.';
    return result;
  }

  const rootAttrs = svgMatch[1];
  let innerContent = svgMatch[2].trim();

  // Extract viewBox
  const vbMatch = rootAttrs.match(/viewBox=["']([^"']+)["']/i);
  if (vbMatch) {
    result.viewBox = vbMatch[1];
  } else {
    // Attempt to synthesize viewBox from width and height
    const wMatch = rootAttrs.match(/width=["'](\d+)["']/i);
    const hMatch = rootAttrs.match(/height=["'](\d+)["']/i);
    if (wMatch && hMatch) {
      result.viewBox = `0 0 ${wMatch[1]} ${hMatch[1]}`;
    }
  }

  // Extract width & height
  const wMatch = rootAttrs.match(/width=["']([^"']+)["']/i);
  if (wMatch) result.width = wMatch[1];
  const hMatch = rootAttrs.match(/height=["']([^"']+)["']/i);
  if (hMatch) result.height = hMatch[1];

  // If useCurrentColor is requested, replace fills/strokes
  if (useCurrentColor) {
    innerContent = innerContent
      .replace(/fill=["'](?!none)[^"']+["']/gi, 'fill="currentColor"')
      .replace(/stroke=["'](?!none)[^"']+["']/gi, 'stroke="currentColor"');
  }

  // Transform inner SVG tags and attributes to React JSX format
  let transformedInner = innerContent
    // Convert style attributes to JSX objects
    .replace(/style=["']([^"']+)["']/gi, (_, styleStr) => {
      const jsxStyle = convertStyleStringToJsx(styleStr);
      return jsxStyle ? `style={${jsxStyle}}` : '';
    })
    // Convert attributes according to SVG_ATTR_MAP
    .replace(/([a-zA-Z0-9:-]+)=["']([^"']*)["']/g, (match, attrName, attrVal) => {
      const lower = attrName.toLowerCase();
      if (lower in SVG_ATTR_MAP) {
        const mapped = SVG_ATTR_MAP[lower];
        if (mapped === null) return ''; // Remove unwanted attribute
        return `${mapped}="${attrVal}"`;
      }
      return match;
    })
    // Ensure self-closing tags for path, circle, rect, line, polygon, polyline, ellipse, stop, use
    .replace(/<(path|circle|rect|line|polygon|polyline|ellipse|stop|use)([^>]*)>(?:\s*<\/\1>)?/gi, (match, tag, attrs) => {
      const trimmedAttrs = attrs.trim();
      if (trimmedAttrs.endsWith('/')) {
        return `<${tag} ${trimmedAttrs}>`;
      }
      return `<${tag} ${trimmedAttrs} />`;
    });

  result.innerJsx = transformedInner;
  result.isValid = true;

  return result;
}
