import React, { useState, useEffect, useMemo } from 'react';
import styles from './App.module.css';
import { Header } from './components/Header';
import { SvgInputPane } from './components/SvgInputPane';
import { PreviewStudio } from './components/PreviewStudio';
import { CodeOutputPane } from './components/CodeOutputPane';
import { OptionsPanel } from './components/OptionsPanel';
import { Toast } from './components/Toast';
import { parseSvg, toPascalCase } from './core/svgParser';
import { generateOutput, TARGET_FORMATS } from './core/generators';
import { SVG_PRESETS } from './core/presets';

export function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('svg2jsx_theme') || 'dark';
  });

  const [svgInput, setSvgInput] = useState(SVG_PRESETS[0].svg);
  const [activePresetId, setActivePresetId] = useState(SVG_PRESETS[0].id);
  const [activeFormatId, setActiveFormatId] = useState('react-jsx');
  const [copied, setCopied] = useState(false);
  const [toast, setToast] = useState(null);

  // Component Options
  const [componentName, setComponentName] = useState('ZapIcon');
  const [useCurrentColor, setUseCurrentColor] = useState(false);
  const [isMemo, setIsMemo] = useState(false);
  const [isForwardRef, setIsForwardRef] = useState(false);
  const [isDefaultExport, setIsDefaultExport] = useState(true);

  // Preview Studio State
  const [previewSize, setPreviewSize] = useState(48);
  const [previewColor, setPreviewColor] = useState('#818cf8');
  const [useCustomColor, setUseCustomColor] = useState(false);

  // Check if loaded in embed mode (?embed=true)
  const isEmbedded = useMemo(() => {
    return new URLSearchParams(window.location.search).get('embed') === 'true';
  }, []);

  // Theme synchronization
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('svg2jsx_theme', theme);
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

  // Parse SVG
  const parsedSvg = useMemo(() => {
    return parseSvg(svgInput, {
      useCurrentColor,
      componentName
    });
  }, [svgInput, useCurrentColor, componentName]);

  // Generate target code
  const generatedCode = useMemo(() => {
    return generateOutput(activeFormatId, parsedSvg, {
      componentName,
      isMemo,
      isForwardRef,
      isDefaultExport,
      useCurrentColor
    });
  }, [activeFormatId, parsedSvg, componentName, isMemo, isForwardRef, isDefaultExport, useCurrentColor]);

  // Handle postMessage API for parent iframe platforms
  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data && event.data.type === 'SVG2JSX_LOAD_SVG') {
        if (typeof event.data.svg === 'string') {
          setSvgInput(event.data.svg);
          setActivePresetId(null);
          if (event.data.name) {
            setComponentName(toPascalCase(event.data.name));
          }
          showToast('Loaded SVG from parent platform', 'success');
        }
      }
      if (event.data && event.data.type === 'SVG2JSX_SET_THEME') {
        if (event.data.theme === 'light' || event.data.theme === 'dark') {
          setTheme(event.data.theme);
        }
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // Handle Load Preset
  const handleLoadPreset = (preset) => {
    setSvgInput(preset.svg);
    setActivePresetId(preset.id);
    setComponentName(toPascalCase(preset.id) + 'Icon');
    showToast(`Loaded preset: ${preset.name}`, 'info');
  };

  // Handle File Upload / Drop
  const handleFileUpload = (content, filename) => {
    setSvgInput(content);
    setActivePresetId(null);
    const cleanName = filename.replace(/\.svg$/i, '');
    setComponentName(toPascalCase(cleanName) + 'Icon');
    showToast(`Loaded file: ${filename}`, 'success');
  };

  // Handle Paste
  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setSvgInput(text);
        setActivePresetId(null);
        showToast('Pasted SVG from clipboard', 'success');
      }
    } catch {
      showToast('Could not access clipboard. Please paste manually.', 'error');
    }
  };

  // Handle Clear
  const handleClear = () => {
    setSvgInput('');
    setActivePresetId(null);
    showToast('Input cleared', 'info');
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

  // Handle Download Snippet
  const handleDownload = () => {
    const target = TARGET_FORMATS.find(f => f.id === activeFormatId) || TARGET_FORMATS[0];
    const name = toPascalCase(componentName || 'SvgIcon');
    const blob = new Blob([generatedCode], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${name}.${target.extension}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    showToast(`Downloaded ${name}.${target.extension}`, 'success');
  };

  return (
    <div className={styles.appWrapper}>
      <Header
        theme={theme}
        toggleTheme={toggleTheme}
        onLoadPreset={handleLoadPreset}
        activePresetId={activePresetId}
        isEmbedded={isEmbedded}
      />

      <main className={styles.mainContent}>
        {/* Top Split Layout: Left Input/Preview vs Right Code Output */}
        <div className={styles.panesGrid}>
          {/* Left Column: Input + Live Preview Studio */}
          <div className={styles.leftColumn}>
            <SvgInputPane
              svgInput={svgInput}
              onSvgChange={(val) => {
                setSvgInput(val);
                setActivePresetId(null);
              }}
              parsedSvg={parsedSvg}
              onClear={handleClear}
              onPaste={handlePaste}
              onFileUpload={handleFileUpload}
            />

            <PreviewStudio
              rawSvg={svgInput}
              parsedSvg={parsedSvg}
              previewSize={previewSize}
              setPreviewSize={setPreviewSize}
              previewColor={previewColor}
              setPreviewColor={setPreviewColor}
              useCustomColor={useCustomColor}
              setUseCustomColor={setUseCustomColor}
            />
          </div>

          {/* Right Column: Code Output Pane */}
          <div className={styles.rightColumn}>
            <CodeOutputPane
              activeFormatId={activeFormatId}
              onSelectFormat={setActiveFormatId}
              generatedCode={generatedCode}
              onCopy={handleCopyCode}
              copied={copied}
              onDownload={handleDownload}
            />
          </div>
        </div>

        {/* Bottom Configuration Panel */}
        <OptionsPanel
          componentName={componentName}
          setComponentName={setComponentName}
          useCurrentColor={useCurrentColor}
          setUseCurrentColor={setUseCurrentColor}
          isMemo={isMemo}
          setIsMemo={setIsMemo}
          isForwardRef={isForwardRef}
          setIsForwardRef={setIsForwardRef}
          isDefaultExport={isDefaultExport}
          setIsDefaultExport={setIsDefaultExport}
        />
      </main>

      {/* Toast Feedback */}
      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}
