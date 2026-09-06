# ROSP JSON Formatter & Visualizer

A modern, high-performance, open-source JSON Formatter, Minifier, Repair Tool, and Interactive Tree Visualizer built with React and JavaScript (Vite). Designed for standalone web deployment or iframe integration into parent React applications.

![Theme](https://img.shields.io/badge/Theme-Blue%20%26%20White-blue)
![Client Side](https://img.shields.io/badge/Privacy-100%25%20Client--Side-green)
![React](https://img.shields.io/badge/React-JavaScript-blue)

---

## 🚀 Key Features

- **Blue & White Premium Design**: Built with modern CSS design tokens, glassmorphism, responsive grid layout, and dark mode support.
- **Dual View Panes**:
  - **Code Editor Pane**: Real-time syntax validation, line numbers, error pointers (line & column), quick auto-fix button.
  - **Interactive Tree View**: Collapsible nodes, type badge chips (`string`, `number`, `boolean`, `array`, `object`), key-path copier (`data.users[0].name`), and real-time key/value filter search.
- **Smart Actions**:
  - **Format & Minify**: Customizable indentation (2 spaces, 4 spaces, tabs).
  - **Auto-Fix / Repair**: Automatically fixes unquoted keys, single quotes, and trailing commas.
  - **Converters**: Export JSON to **YAML, CSV, XML, and JS Objects**.
- **100% Client-Side Privacy**: Zero backend required. Your JSON payload never leaves the browser.

---

## 💻 Local Development

1. Navigate to the tool folder:
   ```bash
   cd json-formatter
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

## 🔗 How to Link via iframe in Your React Platform

### 1. Simple iframe Embedding
Render the application with the `?embed=true` URL query parameter to automatically hide the standalone headers and footers for a clean embedded UI:

```jsx
<iframe
  src="https://your-rosp-tools-domain.com/json-formatter/?embed=true&theme=light"
  style={{ width: '100%', height: '600px', border: 'none', borderRadius: '12px' }}
  title="ROSP JSON Formatter"
/>
```

### 2. Passing JSON Dynamically from Parent React Platform

You can pass JSON directly to the embedded iframe using `postMessage`:

```jsx
import React, { useRef } from 'react';

export function MyPlatformPage() {
  const iframeRef = useRef(null);

  const sendJSONToTool = (data) => {
    if (iframeRef.current) {
      iframeRef.current.contentWindow.postMessage(
        {
          type: 'ROSP_LOAD_JSON',
          json: data // Object or JSON string
        },
        '*'
      );
    }
  };

  return (
    <div>
      <button onClick={() => sendJSONToTool({ status: 'ok', user: 'Admin' })}>
        Load Data into Formatter
      </button>

      <iframe
        ref={iframeRef}
        src="http://localhost:3000/?embed=true"
        style={{ width: '100%', height: '650px', border: '1px solid #e2e8f0', borderRadius: '8px' }}
        title="ROSP JSON Formatter"
      />
    </div>
  );
}
```
