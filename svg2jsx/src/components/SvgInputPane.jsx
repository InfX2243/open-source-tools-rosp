import React, { useRef } from 'react';
import styles from './SvgInputPane.module.css';
import { FileCode, Upload, ClipboardPaste, Trash2 } from 'lucide-react';

export function SvgInputPane({
  svgInput,
  onSvgChange,
  parsedSvg,
  onClear,
  onPaste,
  onFileUpload
}) {
  const fileInputRef = useRef(null);

  const lineCount = Math.max(svgInput.split('\n').length, 12);
  const lineNumbers = Array.from({ length: lineCount }, (_, i) => i + 1);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result;
        if (typeof content === 'string') {
          onFileUpload(content, file.name);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.includes('svg')) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result;
        if (typeof content === 'string') {
          onFileUpload(content, file.name);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  return (
    <div 
      className={styles.paneContainer}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      {/* Pane Header */}
      <div className={styles.paneHeader}>
        <div className={styles.headerLeft}>
          <FileCode size={16} className={styles.titleIcon} />
          <span className={styles.paneTitle}>Raw SVG Input</span>

          {parsedSvg.isValid && (
            <span className={styles.viewBoxBadge}>
              viewBox: {parsedSvg.viewBox}
            </span>
          )}
        </div>

        {/* Action Toolbar */}
        <div className={styles.toolbar}>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".svg"
            style={{ display: 'none' }}
          />

          <button 
            className={styles.toolBtn} 
            onClick={() => fileInputRef.current?.click()}
            title="Upload .svg File"
          >
            <Upload size={14} />
            <span>Upload SVG</span>
          </button>

          <button 
            className={styles.toolBtn} 
            onClick={onPaste}
            title="Paste from Clipboard"
          >
            <ClipboardPaste size={14} />
            <span>Paste</span>
          </button>

          <button 
            className={`${styles.toolBtn} ${styles.dangerBtn}`} 
            onClick={onClear}
            disabled={!svgInput.trim()}
            title="Clear SVG"
          >
            <Trash2 size={14} />
            <span>Clear</span>
          </button>
        </div>
      </div>

      {/* Editor Body */}
      <div className={styles.editorWrapper}>
        <div className={styles.lineNumbers}>
          {lineNumbers.map(num => (
            <span key={num} className={styles.lineNumber}>{num}</span>
          ))}
        </div>

        <textarea
          className={styles.textarea}
          value={svgInput}
          onChange={(e) => onSvgChange(e.target.value)}
          placeholder={`Paste your raw <svg> markup here or drag & drop a .svg file...\n\nExample:\n<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">\n  <path d="M12 2L2 7l10 5 10-5-10-5z" />\n</svg>`}
          spellCheck={false}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
        />
      </div>

      {/* Footer / Status */}
      <div className={styles.paneFooter}>
        {parsedSvg.isValid ? (
          <span className={styles.statusValid}>
            ✓ Valid SVG ({svgInput.length} chars, {new Blob([svgInput]).size} bytes)
          </span>
        ) : svgInput.trim() ? (
          <span className={styles.statusError}>
            {parsedSvg.error || 'Invalid SVG markup'}
          </span>
        ) : (
          <span className={styles.statusEmpty}>
            Ready for SVG input or choose a preset above
          </span>
        )}
      </div>
    </div>
  );
}
