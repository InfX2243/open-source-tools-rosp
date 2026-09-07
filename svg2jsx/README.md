# SVG2JSX 🎨

A modern, high-performance, open-source **SVG to React (JSX/TSX) & CSS Data-URI Converter** built with React 18, Vite, and JavaScript. Effortlessly transform raw `<svg>` code and `.svg` icon files into clean, customizable React components, CSS background data-URIs, and minified vector assets.

![Theme](https://img.shields.io/badge/Theme-Dark%20%26%20Light-indigo)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Client--Side-green)
![React](https://img.shields.io/badge/React-18-blue)

---

## 🚀 Features

- **Multi-Format Code Generation (via Dropdown)**:
  - **React (JSX)**: Clean functional components with configurable props (`size`, `color`, `className`, `...props`).
  - **React (TSX)**: Fully typed component with `React.SVGProps<SVGSVGElement>` interface.
  - **React Native SVG**: `import Svg, { Path, Rect, Circle, ... } from 'react-native-svg'`.
  - **CSS Data-URI**: Ready-to-use `background-image: url('data:image/svg+xml,...')` with optimized UTF-8 encoding.
  - **CSS Mask**: `-webkit-mask-image` and `mask-image` rules enabling dynamic icon colorization with `background-color`.
  - **Cleaned & Minified SVG**: Strips doctype, XML headers, Figma/Illustrator/Inkscape metadata, comments, and extra whitespace.
  - **Base64 String & HTML `<img>` tag**: One-click data-URI for HTML or CSS.
- **Interactive Live Preview Studio**:
  - Real-time rendering of the SVG.
  - Live color adjustment (`currentColor` / custom color picker).
  - Size controls with quick presets (16, 24, 32, 48, 64, 96, 128px) and slider.
  - Canvas background switcher (Checkerboard transparent, Dark, Light).
  - Rotation (90° increments) and Horizontal/Vertical flip controls.
- **Component Customization Controls**:
  - Custom Component Name with auto-PascalCase formatting.
  - `currentColor` toggle for easy CSS color cascading.
  - `React.memo` wrapping option.
  - `React.forwardRef` wrapping option.
  - Default export vs Named export selector.
- **Developer UX**:
  - Drag-and-drop & file upload for `.svg` files.
  - Pre-loaded SVG presets (Stroke icons, Multi-path logos, Solid security shields, Gradient badges).
  - 1-click Copy with toast notifications.
  - Component file download (`.jsx`, `.tsx`, `.css`, `.svg`).
  - 100% Client-side privacy (no data leaves the browser).

---

## 💻 Local Development

1. Navigate to the `svg2jsx` directory:
   ```bash
   cd svg2jsx
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

4. Build for production:
   ```bash
   npm run build
   ```

---

## 🔗 How to Embed via iframe in Parent React Platforms

### 1. Simple iframe Embedding
Add the `?embed=true` URL query parameter to hide standalone navigation headers:

```jsx
<iframe
  src="http://localhost:5175/?embed=true"
  style={{ width: '100%', height: '750px', border: 'none', borderRadius: '12px' }}
  title="SVG2JSX Converter"
/>
```

### 2. Passing SVGs Dynamically from Parent Platform

You can pass SVG strings directly to the embedded iframe using `postMessage`:

```jsx
import React, { useRef } from 'react';

export function IconLibrary() {
  const iframeRef = useRef(null);

  const sendSvgToTool = (svgString, name) => {
    if (iframeRef.current) {
      iframeRef.current.contentWindow.postMessage(
        {
          type: 'SVG2JSX_LOAD_SVG',
          svg: svgString,
          name: name
        },
        '*'
      );
    }
  };

  return (
    <div>
      <button onClick={() => sendSvgToTool('<svg ...>...</svg>', 'UserCheck')}>
        Open in SVG2JSX
      </button>

      <iframe
        ref={iframeRef}
        src="http://localhost:5175/?embed=true"
        style={{ width: '100%', height: '750px', border: '1px solid #e2e8f0', borderRadius: '8px' }}
        title="SVG2JSX"
      />
    </div>
  );
}
```
