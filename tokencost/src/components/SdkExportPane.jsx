import React, { useState, useMemo, useRef, useEffect } from 'react';
import styles from './SdkExportPane.module.css';
import { 
  Copy, 
  Check, 
  Download, 
  ChevronDown, 
  Search, 
  Code2, 
  FileCode
} from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/components/prism-clike';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-json';
import { SDK_TARGETS } from '../core/generators';

function highlightCode(code, langName) {
  if (!code) return '';
  try {
    const grammar = Prism.languages[langName] || Prism.languages.javascript || Prism.languages.python;
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

export function SdkExportPane({
  activeTargetId,
  onSelectTarget,
  generatedCode,
  onCopy,
  copied,
  onDownload,
  selectedModel
}) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const dropdownRef = useRef(null);

  const activeTarget = SDK_TARGETS.find(t => t.id === activeTargetId) || SDK_TARGETS[0];

  const highlightedHtml = useMemo(() => {
    return highlightCode(generatedCode, activeTarget.prismLang);
  }, [generatedCode, activeTarget.prismLang]);

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
  const filteredTargets = useMemo(() => {
    if (!searchQuery.trim()) return SDK_TARGETS;
    const q = searchQuery.toLowerCase();
    return SDK_TARGETS.filter(
      t => t.name.toLowerCase().includes(q) || t.library.toLowerCase().includes(q) || t.category.toLowerCase().includes(q)
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
              <span className={styles.triggerName}>{activeTarget.name}</span>
              <span className={styles.triggerLib}>({activeTarget.library})</span>
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
                  placeholder="Search SDK or runtime..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  autoFocus
                />
              </div>

              <div className={styles.dropdownList}>
                {filteredTargets.length === 0 ? (
                  <div className={styles.noResults}>No target matches "{searchQuery}"</div>
                ) : (
                  filteredTargets.map(tgt => (
                    <button
                      key={tgt.id}
                      className={`${styles.dropdownOption} ${activeTargetId === tgt.id ? styles.selectedOption : ''}`}
                      onClick={() => {
                        onSelectTarget(tgt.id);
                        setDropdownOpen(false);
                        setSearchQuery('');
                      }}
                    >
                      <div className={styles.optionContent}>
                        <div className={styles.optionTitleGroup}>
                          <span className={styles.optionName}>{tgt.name}</span>
                          <span className={styles.optionCategory}>{tgt.category}</span>
                        </div>
                        <span className={styles.optionLib}>{tgt.library}</span>
                      </div>
                      {activeTargetId === tgt.id && (
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
            title={`Download as .${activeTarget.extension}`}
          >
            <Download size={14} />
            <span>Download .{activeTarget.extension}</span>
          </button>

          <button 
            className={`${styles.actionBtn} ${copied ? styles.copiedBtn : styles.primaryBtn}`} 
            onClick={onCopy}
            title="Copy SDK snippet to clipboard"
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
            className={`language-${activeTarget.prismLang} ${styles.code}`}
            dangerouslySetInnerHTML={{ __html: highlightedHtml }}
          />
        </pre>
      </div>

      {/* Footer */}
      <div className={styles.paneFooter}>
        <span>{lineCount} lines</span>
        <span>Selected Model: <strong>{selectedModel?.name || 'Default'}</strong></span>
      </div>
    </div>
  );
}
