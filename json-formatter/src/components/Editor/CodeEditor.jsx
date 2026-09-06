import React, { useRef, useEffect } from 'react';
import { AlertCircle, Wrench, CheckCircle2, Code } from 'lucide-react';
import styles from './CodeEditor.module.css';

export default function CodeEditor({ value, onChange, error, isValid, onRepair }) {
  const textareaRef = useRef(null);
  const lineNumbersRef = useRef(null);

  // Sync scrolling between textarea and line numbers pane
  const handleScroll = () => {
    if (textareaRef.current && lineNumbersRef.current) {
      lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  };

  const lines = value.split('\n');
  const lineCount = lines.length || 1;

  return (
    <div className={styles.editorContainer}>
      <div className={styles.editorHeader}>
        <div className={styles.headerTitle}>
          <Code size={15} className={styles.headerIcon} />
          <span>JSON Input / Code Editor</span>
        </div>
        <div className={styles.statusIndicator}>
          {isValid ? (
            <span className={styles.validBadge}>
              <CheckCircle2 size={13} />
              Valid JSON
            </span>
          ) : (
            <span className={styles.invalidBadge}>
              <AlertCircle size={13} />
              Invalid Syntax
            </span>
          )}
        </div>
      </div>

      {!isValid && error && (
        <div className={styles.errorBanner}>
          <div className={styles.errorTextGroup}>
            <AlertCircle size={16} className={styles.errorIcon} />
            <div>
              <span className={styles.errorTitle}>JSON Syntax Error</span>
              <p className={styles.errorMessage}>
                Line {error.line}, Column {error.column}: {error.message}
              </p>
              {error.snippet && (
                <code className={styles.errorSnippet}>"{error.snippet}"</code>
              )}
            </div>
          </div>
          <button onClick={onRepair} className={styles.quickFixBtn}>
            <Wrench size={14} />
            Auto-Fix Error
          </button>
        </div>
      )}

      <div className={styles.editorBody}>
        {/* Line Numbers Sidebar */}
        <div ref={lineNumbersRef} className={styles.lineNumbers}>
          {Array.from({ length: lineCount }).map((_, idx) => {
            const lineNum = idx + 1;
            const isErrorLine = error && error.line === lineNum;
            return (
              <div
                key={lineNum}
                className={`${styles.lineNumber} ${isErrorLine ? styles.errorLineNumber : ''}`}
              >
                {lineNum}
              </div>
            );
          })}
        </div>

        {/* Text Area Code Editor */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onScroll={handleScroll}
          placeholder="Paste or type your JSON here..."
          className={styles.textarea}
          spellCheck={false}
          wrap="off"
        />
      </div>
    </div>
  );
}
