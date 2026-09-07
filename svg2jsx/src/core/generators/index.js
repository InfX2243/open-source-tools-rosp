import { generateReactJsx } from './reactJsx';
import { generateReactTsx } from './reactTsx';
import { generateReactNative } from './reactNative';
import { generateCssDataUri } from './cssDataUri';
import { generateMinifiedSvg } from './minifiedSvg';
import { generateBase64Svg } from './base64Svg';

export const TARGET_FORMATS = [
  {
    id: 'react-jsx',
    name: 'React (JSX)',
    category: 'React',
    library: 'Functional Component',
    prismLang: 'javascript',
    extension: 'jsx',
    generator: generateReactJsx
  },
  {
    id: 'react-tsx',
    name: 'React (TSX)',
    category: 'TypeScript',
    library: 'Typed Component',
    prismLang: 'javascript',
    extension: 'tsx',
    generator: generateReactTsx
  },
  {
    id: 'react-native',
    name: 'React Native',
    category: 'Mobile',
    library: 'react-native-svg',
    prismLang: 'javascript',
    extension: 'jsx',
    generator: generateReactNative
  },
  {
    id: 'css-data-uri',
    name: 'CSS Data-URI',
    category: 'CSS',
    library: 'Background & Mask',
    prismLang: 'css',
    extension: 'css',
    generator: generateCssDataUri
  },
  {
    id: 'minified-svg',
    name: 'Cleaned SVG',
    category: 'SVG',
    library: 'Minified Markup',
    prismLang: 'markup',
    extension: 'svg',
    generator: generateMinifiedSvg
  },
  {
    id: 'base64-svg',
    name: 'Base64 & HTML',
    category: 'Web',
    library: 'Data URI & <img>',
    prismLang: 'markup',
    extension: 'html',
    generator: generateBase64Svg
  }
];

export function generateOutput(formatId, parsedSvg, options = {}) {
  const target = TARGET_FORMATS.find(t => t.id === formatId) || TARGET_FORMATS[0];
  try {
    return target.generator(parsedSvg, options);
  } catch (err) {
    return `// Failed to generate code for ${target.name}:\n// ${err.message}`;
  }
}
