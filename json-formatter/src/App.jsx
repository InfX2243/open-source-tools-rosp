import React, { useState, useEffect, useMemo, useCallback } from 'react';
import Navbar from './components/Navbar/Navbar';
import Toolbar from './components/Toolbar/Toolbar';
import CodeEditor from './components/Editor/CodeEditor';
import JSONTreeView from './components/TreeView/JSONTreeView';
import ConverterModal from './components/ConverterModal/ConverterModal';
import StatsBar from './components/StatsBar/StatsBar';
import GuideModal from './components/GuideModal/GuideModal';
import { formatJSON, repairJSON } from './utils/jsonFormatter';
import { SAMPLE_JSONS } from './utils/sampleData';
import styles from './App.module.css';

export default function App() {
  // Read URL Params for iframe embedding options (?embed=true, ?theme=dark)
  const urlParams = new URLSearchParams(window.location.search);
  const isEmbedded = urlParams.get('embed') === 'true';
  const initialThemeParam = urlParams.get('theme');

  const [theme, setTheme] = useState(() => {
    if (initialThemeParam === 'dark' || initialThemeParam === 'light') return initialThemeParam;
    return localStorage.getItem('rosp_theme') || 'light';
  });

  const [rawInput, setRawInput] = useState(() => {
    return localStorage.getItem('rosp_json_input') || SAMPLE_JSONS.apiResponse;
  });

  const [indent, setIndent] = useState('2');
  const [viewMode, setViewMode] = useState('split');
  const [isConverterOpen, setIsConverterOpen] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  // Apply theme data attribute to document element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('rosp_theme', theme);
  }, [theme]);

  // Auto-save input state
  useEffect(() => {
    localStorage.setItem('rosp_json_input', rawInput);
  }, [rawInput]);

  // iframe postMessage Event Listener for parent platform communication
  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data && event.data.type === 'ROSP_LOAD_JSON') {
        const payload = typeof event.data.json === 'string' 
          ? event.data.json 
          : JSON.stringify(event.data.json, null, 2);
        setRawInput(payload);
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // Format calculation
  const formatResult = useMemo(() => {
    return formatJSON(rawInput, indent);
  }, [rawInput, indent]);

  // Actions
  const handleFormat = useCallback(() => {
    const res = formatJSON(rawInput, indent);
    setRawInput(res.formatted);
  }, [rawInput, indent]);

  const handleMinify = useCallback(() => {
    const res = formatJSON(rawInput, 'minify');
    setRawInput(res.formatted);
  }, [rawInput]);

  const handleRepair = useCallback(() => {
    const fixed = repairJSON(rawInput);
    setRawInput(fixed);
  }, [rawInput]);

  const handleClear = useCallback(() => {
    setRawInput('');
  }, []);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(formatResult.formatted || rawInput);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 1500);
  }, [formatResult.formatted, rawInput]);

  const handleDownload = useCallback(() => {
    const blob = new Blob([formatResult.formatted || rawInput], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'formatted_data.json';
    link.click();
    URL.revokeObjectURL(url);
  }, [formatResult.formatted, rawInput]);

  const handleFileUpload = useCallback((e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setRawInput(event.target.result || '');
      };
      reader.readAsText(file);
    }
  }, []);

  const handleLoadSample = useCallback((sampleKey) => {
    if (SAMPLE_JSONS[sampleKey]) {
      setRawInput(SAMPLE_JSONS[sampleKey]);
    }
  }, []);

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'f') {
        e.preventDefault();
        handleFormat();
      } else if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'm') {
        e.preventDefault();
        handleMinify();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleFormat, handleMinify]);

  return (
    <div className={`${styles.appShell} ${isEmbedded ? 'is-embedded' : ''}`}>
      <Navbar
        theme={theme}
        onToggleTheme={() => setTheme(t => t === 'light' ? 'dark' : 'light')}
        isEmbedded={isEmbedded}
      />

      <Toolbar
        onFormat={handleFormat}
        onMinify={handleMinify}
        onRepair={handleRepair}
        onClear={handleClear}
        onCopy={handleCopy}
        onDownload={handleDownload}
        onUpload={handleFileUpload}
        onLoadSample={handleLoadSample}
        indent={indent}
        onChangeIndent={setIndent}
        viewMode={viewMode}
        onChangeViewMode={setViewMode}
        onOpenConverter={() => setIsConverterOpen(true)}
        isCopied={isCopied}
        isValid={formatResult.isValid}
      />

      <main className={styles.mainArea}>
        <div className={`${styles.panesContainer} ${styles[viewMode]}`}>
          {(viewMode === 'split' || viewMode === 'code') && (
            <div className={styles.pane}>
              <CodeEditor
                value={rawInput}
                onChange={setRawInput}
                error={formatResult.error}
                isValid={formatResult.isValid}
                onRepair={handleRepair}
              />
            </div>
          )}

          {(viewMode === 'split' || viewMode === 'tree') && (
            <div className={styles.pane}>
              <JSONTreeView
                data={formatResult.parsedObj}
                isValid={formatResult.isValid}
              />
            </div>
          )}
        </div>
      </main>

      <ConverterModal
        isOpen={isConverterOpen}
        onClose={() => setIsConverterOpen(false)}
        jsonData={formatResult.parsedObj || rawInput}
      />

      <StatsBar
        stats={formatResult.stats}
        isValid={formatResult.isValid}
        isEmbedded={isEmbedded}
      />

      <GuideModal
        onLoadSample={handleLoadSample}
        onFormat={handleFormat}
        onChangeViewMode={setViewMode}
      />
    </div>
  );
}
