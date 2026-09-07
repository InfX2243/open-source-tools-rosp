import React, { useState, useMemo, useRef, useEffect } from 'react';
import styles from './CodeOutputPane.module.css';
import { 
  Copy, 
  Check, 
  Download, 
  FileCode, 
  ChevronDown, 
  Search, 
  Code2
} from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/components/prism-clike';
import 'prismjs/components/prism-markup';
import 'prismjs/components/prism-markup-templating';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-go';
import 'prismjs/components/prism-rust';
import 'prismjs/components/prism-php';
import 'prismjs/components/prism-java';
import 'prismjs/components/prism-csharp';
import 'prismjs/components/prism-ruby';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-json';
import { TARGET_LANGUAGES } from '../core/generators';

function highlightCode(code, langName) {
  if (!code) return '';
  try {
    const grammar = Prism.languages[langName] || Prism.languages.javascript || Prism.languages.clike;
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
  activeLanguageId,
  onSelectLanguage,
  generatedCode,
  onCopy,
  copied,
  onDownload
}) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const dropdownRef = useRef(null);

  const activeLang = TARGET_LANGUAGES.find(l => l.id === activeLanguageId) || TARGET_LANGUAGES[0];

  const highlightedHtml = useMemo(() => {
    return highlightCode(generatedCode, activeLang.prismLang);
  }, [generatedCode, activeLang.prismLang]);

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

  // Filter languages by search query
  const filteredLanguages = useMemo(() => {
    if (!searchQuery.trim()) return TARGET_LANGUAGES;
    const q = searchQuery.toLowerCase();
    return TARGET_LANGUAGES.filter(
      l => l.name.toLowerCase().includes(q) || l.library.toLowerCase().includes(q)
    );
  }, [searchQuery]);

  return (
    <div className={styles.paneContainer}>
      {/* Pane Top Bar with Language Dropdown & Actions */}
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
              <span className={styles.triggerLang}>{activeLang.name}</span>
              <span className={styles.triggerLib}>({activeLang.library})</span>
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
                  placeholder="Search language or library..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  autoFocus
                />
              </div>

              <div className={styles.dropdownList}>
                {filteredLanguages.length === 0 ? (
                  <div className={styles.noResults}>No language matches "{searchQuery}"</div>
                ) : (
                  filteredLanguages.map(lang => (
                    <button
                      key={lang.id}
                      className={`${styles.dropdownOption} ${activeLanguageId === lang.id ? styles.selectedOption : ''}`}
                      onClick={() => {
                        onSelectLanguage(lang.id);
                        setDropdownOpen(false);
                        setSearchQuery('');
                      }}
                    >
                      <div className={styles.optionContent}>
                        <span className={styles.optionName}>{lang.name}</span>
                        <span className={styles.optionLib}>{lang.library}</span>
                      </div>
                      {activeLanguageId === lang.id && (
                        <Check size={14} className={styles.optionCheck} />
                      )}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons in Header */}
        <div className={styles.buttonGroup}>
          <button 
            className={styles.actionBtn} 
            onClick={onDownload}
            title={`Download as .${activeLang.extension}`}
          >
            <Download size={14} />
            <span>Download .{activeLang.extension}</span>
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
            className={`language-${activeLang.prismLang} ${styles.code}`}
            dangerouslySetInnerHTML={{ __html: highlightedHtml }}
          />
        </pre>
      </div>

      {/* Footer / Stats */}
      <div className={styles.paneFooter}>
        <span>{lineCount} lines</span>
        <span>Target: <strong>{activeLang.name} ({activeLang.library})</strong></span>
      </div>
    </div>
  );
}
