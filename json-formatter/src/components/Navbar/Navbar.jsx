import React from 'react';
import { Code2, Sun, Moon, ExternalLink, Sparkles, ShieldCheck } from 'lucide-react';
import styles from './Navbar.module.css';

export default function Navbar({ theme, onToggleTheme, isEmbedded }) {
  if (isEmbedded) return null;

  return (
    <header className={styles.navbar}>
      <div className={styles.brandContainer}>
        <div className={styles.logoBadge}>
          <Code2 size={24} className={styles.logoIcon} />
        </div>
        <div className={styles.brandText}>
          <div className={styles.titleRow}>
            <h1 className={styles.title}>ROSP JSON Formatter</h1>
            <span className={styles.versionBadge}>v1.0</span>
            <span className={styles.openSourceBadge}>Open Source</span>
          </div>
          <p className={styles.subtitle}>
            Formatter, Tree Visualizer & Converter Tool for Developers
          </p>
        </div>
      </div>

      <div className={styles.navActions}>
        <div className={styles.privacyPill} title="100% Client-side processing. Your data never leaves your browser.">
          <ShieldCheck size={14} className={styles.shieldIcon} />
          <span>100% Privacy</span>
        </div>

        <button
          onClick={onToggleTheme}
          className={styles.themeToggleBtn}
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Theme`}
          aria-label="Toggle Theme"
        >
          {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          <span className={styles.themeLabel}>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>
        </button>

        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className={styles.platformLink}
        >
          <span>ROSP Platform</span>
          <ExternalLink size={14} />
        </a>
      </div>
    </header>
  );
}
