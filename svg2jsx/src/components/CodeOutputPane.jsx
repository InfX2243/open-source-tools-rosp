import React, { useState, useMemo, useRef, useEffect } from 'react';
import styles from './CodeOutputPane.module.css';
import { 
  Copy, 
  Check, 
  Download, 
  ChevronDown, 
  Search, 
  Code2
} from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/components/prism-clike';
import 'prismjs/components/prism-markup';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-css';
import { TARGET_FORMATS } from '../core/generators';

function highlightCode(code, langName) {
  if (!code) return '';
  try {
    const grammar = Prism.languages[langName] || Prism.languages.javascript || Prism.languages.markup;
    if (grammar) {
      return Prism.highlight(code, grammar, langName);
    }
  } catch (err) {
    console.warn('Prism highlight error:', err);
  }
  return code
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

export function CodeOutputPane({
  activeFormatId,
  onSelectFormat,
  generatedCode,
  onCopy,
  copied,
  onDownload
}) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const dropdownRef = useRef(null);

  const activeFormat = TARGET_FORMATS.find(f => f.id === activeFormatId) || TARGET_FORMATS[0];

  const highlightedHtml = useMemo(() => {
    return highlightCode(generatedCode, activeFormat.prismLang);
  }, [generatedCode, activeFormat.prismLang]);

  const lineCount = Math.max(generatedCode.split('\n').length, 1);
  const lineNumbers = Array.from({ length: lineCount }, (_, i) => i + 1);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter formats
  const filteredFormats = useMemo(() => {
    if (!searchQuery.trim()) return TARGET_FORMATS;
    const q = searchQuery.toLowerCase();
    return TARGET_FORMATS.filter(
      f => f.name.toLowerCase().includes(q) || f.library.toLowerCase().includes(q) || f.category.toLowerCase().includes(q)
    );
  }, [searchQuery]);

  return (
    <div className={styles.paneContainer}>
      {/* Pane Top Bar */}
      <div className={styles.tabBar}>
        <div className={styles.selectorGroup} ref={dropdownRef}>
          {/* Main Dropdown Button */}
          <button
            className={`${styles.dropdownTrigger} ${dropdownOpen ? styles.triggerActive : ''}`}
            onClick={() => setDropdownOpen(!dropdownOpen)}
            aria-expanded={dropdownOpen}
          >
            <Code2 size={16} className={styles.dropdownIcon} />
            <div className={styles.triggerText}>
              <span className={styles.triggerName}>{activeFormat.name}</span>
              <span className={styles.triggerLib}>({activeFormat.library})</span>
            </div>
            <ChevronDown size={14} className={`${styles.chevron} ${dropdownOpen ? styles.chevronOpen : ''}`} />
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <div className={styles.dropdownMenu}>
              <div className={styles.searchBox}>
                <Search size={14} className={styles.searchIcon} />
                <input
                  type="text"
                  className={styles.searchInput}
                  placeholder="Search output format..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  autoFocus
                />
              </div>

              <div className={styles.dropdownList}>
                {filteredFormats.length === 0 ? (
                  <div className={styles.noResults}>No format matches "{searchQuery}"</div>
                ) : (
                  filteredFormats.map(fmt => (
                    <button
                      key={fmt.id}
                      className={`${styles.dropdownOption} ${activeFormatId === fmt.id ? styles.selectedOption : ''}`}
                      onClick={() => {
                        onSelectFormat(fmt.id);
                        setDropdownOpen(false);
                        setSearchQuery('');
                      }}
                    >
                      <div className={styles.optionContent}>
                        <div className={styles.optionTitleGroup}>
                          <span className={styles.optionName}>{fmt.name}</span>
                          <span className={styles.optionCategory}>{fmt.category}</span>
                        </div>
                        <span className={styles.optionLib}>{fmt.library}</span>
                      </div>
                      {activeFormatId === fmt.id && (
                        <Check size={14} className={styles.optionCheck} />
                      )}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className={styles.buttonGroup}>
          <button 
            className={styles.actionBtn} 
            onClick={onDownload}
            title={`Download as .${activeFormat.extension}`}
          >
            <Download size={14} />
            <span>Download .{activeFormat.extension}</span>
          </button>

          <button 
            className={`${styles.actionBtn} ${copied ? styles.copiedBtn : styles.primaryBtn}`} 
            onClick={onCopy}
            title="Copy code to clipboard"
          >
            {copied ? <Check size={14} /> : <Copy size={14} />}
            <span>{copied ? 'Copied!' : 'Copy Code'}</span>
          </button>
        </div>
      </div>

      {/* Code Display Area */}
      <div className={styles.codeContainer}>
        <div className={styles.lineNumbers}>
          {lineNumbers.map(num => (
            <span key={num} className={styles.lineNumber}>{num}</span>
          ))}
        </div>

        <pre className={styles.pre}>
          <code 
            className={`language-${activeFormat.prismLang} ${styles.code}`}
            dangerouslySetInnerHTML={{ __html: highlightedHtml }}
          />
        </pre>
      </div>

      {/* Footer */}
      <div className={styles.paneFooter}>
        <span>{lineCount} lines</span>
        <span>Output Format: <strong>{activeFormat.name} ({activeFormat.library})</strong></span>
      </div>
    </div>
  );
}
