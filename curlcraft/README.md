# CurlCraft ⚡

A modern, high-performance, open-source **cURL to Multi-Language Code Converter** built with React, Vite, and JavaScript. Convert any cURL request into clean, copy-pasteable, idiomatic code for JavaScript (Fetch, Axios, Node.js), Python (Requests, HTTPX), Go, Rust, PHP, Java, C#, Ruby, and HTTPie.

![Theme](https://img.shields.io/badge/Theme-Dark%20%26%20Light-blue)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Client--Side-green)
![React](https://img.shields.io/badge/React-18-blue)

---

## 🚀 Features

- **Multi-Language & Multi-Library Generation**:
  - **JavaScript**: Native `fetch` (with async/await & error handling)
  - **JavaScript / TypeScript**: `Axios`
  - **Node.js**: Native global `fetch` / `Headers`
  - **Python**: `requests` (idiomatic `json=`, `headers=`, `params=`, `auth=`)
  - **Python (Async)**: `httpx` with `asyncio`
  - **Go**: `net/http` with `http.Client` & request building
  - **Rust**: `reqwest` with Tokio async runtime
  - **PHP**: `cURL` options array
  - **Java**: Modern `java.net.http.HttpClient`
  - **C# / .NET**: `HttpClient` and `HttpRequestMessage`
  - **Ruby**: `net/http`
  - **CLI**: `HTTPie`
- **Robust cURL Parser**:
  - Handles multi-line commands with line continuations (`\`, `` ` ``, `^`).
  - Automatically parses headers (`-H`), basic auth (`-u`), bearer tokens (`Authorization`), query params, JSON payloads (`-d`), form-urlencoded data (`--data-urlencode`), multipart file uploads (`-F`), cookies (`-b`), and options.
- **Visual Request Inspector**:
  - Breakdown tabs for **Query Params**, **Headers**, **Auth**, and **Body**.
  - Interactive table allowing you to toggle, edit, add, or delete parameters/headers in real-time.
- **Developer Experience**:
  - Syntax highlighting with Prism.js.
  - One-click copy with toast notifications.
  - Code snippet file downloader (`.js`, `.py`, `.go`, `.rs`, `.php`, `.java`, `.cs`, `.rb`).
  - Pre-loaded sample requests (Bearer Auth, Query Params, Form URL Encoded, Multipart Upload, GraphQL, Basic Auth).
- **100% Client-Side Privacy**:
  - No server-side tracking, analytics, or payload transmission. All parsing and conversion happens directly in your browser.

---

## 💻 Local Development

1. Navigate to the `curlcraft` folder:
   ```bash
   cd curlcraft
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
Add the `?embed=true` URL parameter to hide standalone navigation headers:

```jsx
<iframe
  src="http://localhost:5174/?embed=true"
  style={{ width: '100%', height: '700px', border: 'none', borderRadius: '12px' }}
  title="CurlCraft Converter"
/>
```

### 2. Passing cURL Dynamically from Parent Platform

You can pass cURL commands dynamically to the embedded iframe using `postMessage`:

```jsx
import React, { useRef } from 'react';

export function MyApiDocumentation() {
  const iframeRef = useRef(null);

  const sendCurlToTool = (curlCommand) => {
    if (iframeRef.current) {
      iframeRef.current.contentWindow.postMessage(
        {
          type: 'CURLCRAFT_LOAD_CURL',
          curl: curlCommand
        },
        '*'
      );
    }
  };

  return (
    <div>
      <button onClick={() => sendCurlToTool('curl -X GET https://api.stripe.com/v1/charges -u "sk_test_key:"')}>
        Convert Stripe Charge cURL
      </button>

      <iframe
        ref={iframeRef}
        src="http://localhost:5174/?embed=true"
        style={{ width: '100%', height: '700px', border: '1px solid #e2e8f0', borderRadius: '8px' }}
        title="CurlCraft"
      />
    </div>
  );
}
```
