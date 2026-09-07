import React, { useState, useEffect, useMemo, useCallback } from 'react';
import styles from './App.module.css';
import { Header } from './components/Header';
import { CurlInputPane } from './components/CurlInputPane';
import { CodeOutputPane } from './components/CodeOutputPane';
import { RequestInspector } from './components/RequestInspector';
import { Toast } from './components/Toast';
import { parseCurl } from './core/parser';
import { generateCode, TARGET_LANGUAGES } from './core/generators';
import { SAMPLES } from './core/samples';

export function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('curlcraft_theme') || 'dark';
  });

  const [curlInput, setCurlInput] = useState(SAMPLES[0].curl);
  const [activeSampleId, setActiveSampleId] = useState(SAMPLES[0].id);
  const [activeLanguageId, setActiveLanguageId] = useState('js-fetch');
  const [copied, setCopied] = useState(false);
  const [toast, setToast] = useState(null);

  // Check if loaded in embed mode (?embed=true)
  const isEmbedded = useMemo(() => {
    return new URLSearchParams(window.location.search).get('embed') === 'true';
  }, []);

  // Sync theme attribute to document root
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('curlcraft_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 3000);
  };

  // Parse cURL
  const parsedReq = useMemo(() => {
    return parseCurl(curlInput);
  }, [curlInput]);

  // Generate target code
  const generatedCode = useMemo(() => {
    return generateCode(activeLanguageId, parsedReq);
  }, [activeLanguageId, parsedReq]);

  // Handle postMessage API for iframe integration
  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data && event.data.type === 'CURLCRAFT_LOAD_CURL') {
        if (typeof event.data.curl === 'string') {
          setCurlInput(event.data.curl);
          setActiveSampleId(null);
          showToast('Loaded cURL from external host', 'success');
        }
      }
      if (event.data && event.data.type === 'CURLCRAFT_SET_THEME') {
        if (event.data.theme === 'light' || event.data.theme === 'dark') {
          setTheme(event.data.theme);
        }
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // Handle Load Sample
  const handleLoadSample = (sample) => {
    setCurlInput(sample.curl);
    setActiveSampleId(sample.id);
    showToast(`Loaded sample: ${sample.name}`, 'info');
  };

  // Handle Paste
  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setCurlInput(text);
        setActiveSampleId(null);
        showToast('Pasted cURL from clipboard', 'success');
      }
    } catch {
      showToast('Could not access clipboard. Please paste manually.', 'error');
    }
  };

  // Handle Clear
  const handleClear = () => {
    setCurlInput('');
    setActiveSampleId(null);
    showToast('Input cleared', 'info');
  };

  // Handle Format / Beautify cURL
  const handleBeautify = () => {
    if (!parsedReq.isValid) return;

    const parts = [`curl -X ${parsedReq.method} "${parsedReq.url}"`];

    parsedReq.headers.forEach(h => {
      parts.push(`  -H "${h.name}: ${h.value}"`);
    });

    if (parsedReq.auth && parsedReq.auth.type === 'basic' && parsedReq.auth.username) {
      parts.push(`  -u "${parsedReq.auth.username}:${parsedReq.auth.password}"`);
    }

    if (parsedReq.body.type === 'json' && parsedReq.body.json) {
      parts.push(`  -d '${JSON.stringify(parsedReq.body.json, null, 2)}'`);
    } else if (parsedReq.body.type === 'url-encoded') {
      parsedReq.body.urlEncoded.forEach(u => {
        parts.push(`  --data-urlencode "${u.key}=${u.value}"`);
      });
    } else if (parsedReq.body.type === 'form-data') {
      parsedReq.body.formData.forEach(f => {
        parts.push(`  -F "${f.key}=${f.type === 'file' ? '@' : ''}${f.value}"`);
      });
    } else if (parsedReq.body.raw) {
      parts.push(`  -d '${parsedReq.body.raw}'`);
    }

    setCurlInput(parts.join(' \\\n'));
    showToast('Formatted cURL command', 'success');
  };

  // Handle Copy Code
  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(generatedCode);
      setCopied(true);
      showToast('Code copied to clipboard!', 'success');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      showToast('Failed to copy to clipboard', 'error');
    }
  };

  // Handle Download File
  const handleDownload = () => {
    const lang = TARGET_LANGUAGES.find(l => l.id === activeLanguageId) || TARGET_LANGUAGES[0];
    const blob = new Blob([generatedCode], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `request_snippet.${lang.extension}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    showToast(`Downloaded snippet.${lang.extension}`, 'success');
  };

  // Synchronize edits from RequestInspector back to cURL input
  const handleUpdateHeaders = (newHeaders) => {
    // Reconstruct cURL with new headers
    const parts = [`curl -X ${parsedReq.method} "${parsedReq.url}"`];
    newHeaders.filter(h => h.enabled && h.name).forEach(h => {
      parts.push(`  -H "${h.name}: ${h.value}"`);
    });
    if (parsedReq.body.type === 'json' && parsedReq.body.json) {
      parts.push(`  -d '${JSON.stringify(parsedReq.body.json)}'`);
    } else if (parsedReq.body.raw) {
      parts.push(`  -d '${parsedReq.body.raw}'`);
    }
    setCurlInput(parts.join(' \\\n'));
  };

  const handleUpdateParams = (newParams) => {
    const baseUrl = parsedReq.baseUrl || 'https://api.example.com';
    const activeParams = newParams.filter(p => p.enabled && p.key);
    const queryString = activeParams.map(p => `${encodeURIComponent(p.key)}=${encodeURIComponent(p.value)}`).join('&');
    const fullUrl = queryString ? `${baseUrl}?${queryString}` : baseUrl;

    const parts = [`curl -X ${parsedReq.method} "${fullUrl}"`];
    parsedReq.headers.filter(h => h.enabled).forEach(h => {
      parts.push(`  -H "${h.name}: ${h.value}"`);
    });
    if (parsedReq.body.raw) {
      parts.push(`  -d '${parsedReq.body.raw}'`);
    }
    setCurlInput(parts.join(' \\\n'));
  };

  return (
    <div className={styles.appWrapper}>
      <Header
        theme={theme}
        toggleTheme={toggleTheme}
        onLoadSample={handleLoadSample}
        activeSampleId={activeSampleId}
        isEmbedded={isEmbedded}
      />

      <main className={styles.mainContent}>
        {/* Dual Pane Layout */}
        <div className={styles.panesGrid}>
          {/* Left Pane: cURL Input */}
          <div className={styles.paneColumn}>
            <CurlInputPane
              curlInput={curlInput}
              onCurlChange={(val) => {
                setCurlInput(val);
                setActiveSampleId(null);
              }}
              parsedReq={parsedReq}
              onBeautify={handleBeautify}
              onClear={handleClear}
              onPaste={handlePaste}
            />
          </div>

          {/* Right Pane: Generated Code */}
          <div className={styles.paneColumn}>
            <CodeOutputPane
              activeLanguageId={activeLanguageId}
              onSelectLanguage={setActiveLanguageId}
              generatedCode={generatedCode}
              onCopy={handleCopyCode}
              copied={copied}
              onDownload={handleDownload}
            />
          </div>
        </div>

        {/* Visual Request Inspector */}
        {parsedReq.isValid && (
          <RequestInspector
            parsedReq={parsedReq}
            onUpdateHeaders={handleUpdateHeaders}
            onUpdateParams={handleUpdateParams}
          />
        )}
      </main>

      {/* Toast Feedback */}
      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}
