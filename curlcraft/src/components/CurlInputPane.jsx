import React, { useRef } from 'react';
import styles from './CurlInputPane.module.css';
import { Terminal, ClipboardPaste, Trash2, Wand2, ArrowRight } from 'lucide-react';

export function CurlInputPane({
  curlInput,
  onCurlChange,
  parsedReq,
  onBeautify,
  onClear,
  onPaste,
  activeTab,
  setActiveTab
}) {
  const textareaRef = useRef(null);

  // Compute line numbers
  const lineCount = Math.max(curlInput.split('\n').length, 12);
  const lineNumbers = Array.from({ length: lineCount }, (_, i) => i + 1);

  const getMethodBadgeClass = (method) => {
    switch (method?.toUpperCase()) {
      case 'GET': return styles.badgeGet;
      case 'POST': return styles.badgePost;
      case 'PUT': return styles.badgePut;
      case 'PATCH': return styles.badgePatch;
      case 'DELETE': return styles.badgeDelete;
      default: return styles.badgeGeneric;
    }
  };

  return (
    <div className={styles.paneContainer}>
      {/* Pane Header */}
      <div className={styles.paneHeader}>
        <div className={styles.headerLeft}>
          <div className={styles.paneTitle}>
            <Terminal size={16} className={styles.titleIcon} />
            <span>cURL Command</span>
          </div>

          {parsedReq.isValid && (
            <div className={styles.parsedSummary}>
              <span className={`${styles.methodBadge} ${getMethodBadgeClass(parsedReq.method)}`}>
                {parsedReq.method}
              </span>
              <span className={styles.urlPreview} title={parsedReq.url}>
                {parsedReq.url}
              </span>
            </div>
          )}
        </div>

        {/* Action Toolbar */}
        <div className={styles.toolbar}>
          <button 
            className={styles.toolBtn} 
            onClick={onPaste}
            title="Paste from Clipboard"
          >
            <ClipboardPaste size={14} />
            <span>Paste</span>
          </button>

          <button 
            className={styles.toolBtn} 
            onClick={onBeautify}
            disabled={!curlInput.trim()}
            title="Format cURL with line continuations"
          >
            <Wand2 size={14} />
            <span>Format</span>
          </button>

          <button 
            className={`${styles.toolBtn} ${styles.dangerBtn}`} 
            onClick={onClear}
            disabled={!curlInput.trim()}
            title="Clear Input"
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
          ref={textareaRef}
          className={styles.textarea}
          value={curlInput}
          onChange={(e) => onCurlChange(e.target.value)}
          placeholder={`Paste your cURL command here...\n\nExample:\ncurl -X POST https://api.example.com/data \\\n  -H "Authorization: Bearer token123" \\\n  -H "Content-Type: application/json" \\\n  -d '{"key": "value"}'`}
          spellCheck={false}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
        />
      </div>

      {/* Footer / Status Bar */}
      <div className={styles.paneFooter}>
        <div className={styles.footerStatus}>
          {parsedReq.isValid ? (
            <span className={styles.statusValid}>
              ✓ Parsed: {parsedReq.headers.length} header(s), {parsedReq.queryParams.length} param(s), Body: {parsedReq.body.type}
            </span>
          ) : curlInput.trim() ? (
            <span className={styles.statusHint}>
              Enter a valid cURL command (must contain a URL)
            </span>
          ) : (
            <span className={styles.statusEmpty}>
              Ready for cURL input or load a sample from the top bar
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
