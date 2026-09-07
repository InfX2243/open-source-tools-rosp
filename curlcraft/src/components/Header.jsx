import React, { useState } from 'react';
import styles from './Header.module.css';
import { Terminal, Sun, Moon, Sparkles, ChevronDown, Check, Code2, ShieldCheck } from 'lucide-react';
import { SAMPLES } from '../core/samples';

export function Header({ theme, toggleTheme, onLoadSample, activeSampleId, isEmbedded }) {
  const [samplesOpen, setSamplesOpen] = useState(false);

  if (isEmbedded) return null;

  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <div className={styles.logoIcon}>
          <Terminal size={22} className={styles.terminalIcon} />
        </div>
        <div className={styles.brandInfo}>
          <div className={styles.brandTitleGroup}>
            <h1 className={styles.brandName}>CurlCraft</h1>
            <span className={styles.versionBadge}>v1.0</span>
          </div>
          <p className={styles.brandTagline}>Universal cURL to Idiomatic Code Converter</p>
        </div>
      </div>

      <div className={styles.actions}>
        {/* Sample Dropdown */}
        <div className={styles.dropdownContainer}>
          <button 
            className={styles.sampleButton}
            onClick={() => setSamplesOpen(!samplesOpen)}
            aria-expanded={samplesOpen}
          >
            <Sparkles size={16} className={styles.sparkleIcon} />
            <span>Load Sample</span>
            <ChevronDown size={14} className={samplesOpen ? styles.chevronUp : ''} />
          </button>

          {samplesOpen && (
            <>
              <div className={styles.backdrop} onClick={() => setSamplesOpen(false)} />
              <div className={styles.dropdownMenu}>
                <div className={styles.dropdownHeader}>Sample API Requests</div>
                {SAMPLES.map(sample => (
                  <button
                    key={sample.id}
                    className={`${styles.dropdownItem} ${activeSampleId === sample.id ? styles.activeItem : ''}`}
                    onClick={() => {
                      onLoadSample(sample);
                      setSamplesOpen(false);
                    }}
                  >
                    <span className={`${styles.methodBadge} ${styles['badge' + sample.badge]}`}>
                      {sample.badge}
                    </span>
                    <span className={styles.sampleLabel}>{sample.name}</span>
                    {activeSampleId === sample.id && <Check size={14} className={styles.checkIcon} />}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Privacy Pill */}
        <div className={styles.privacyPill} title="100% Client-Side Processing. No data is sent to any server.">
          <ShieldCheck size={15} />
          <span>100% Client-Side</span>
        </div>

        {/* Theme Toggle */}
        <button 
          className={styles.themeToggle} 
          onClick={toggleTheme}
          aria-label="Toggle Theme"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}
