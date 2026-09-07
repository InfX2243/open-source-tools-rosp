import React, { useState } from 'react';
import styles from './Header.module.css';
import { Sparkles, Sun, Moon, ShieldCheck, ChevronDown, Check, Code2 } from 'lucide-react';
import { SVG_PRESETS } from '../core/presets';

export function Header({ theme, toggleTheme, onLoadPreset, activePresetId, isEmbedded }) {
  const [presetsOpen, setPresetsOpen] = useState(false);

  if (isEmbedded) return null;

  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <div className={styles.logoIcon}>
          <Code2 size={22} className={styles.codeIcon} />
        </div>
        <div className={styles.brandInfo}>
          <div className={styles.brandTitleGroup}>
            <h1 className={styles.brandName}>SVG2JSX</h1>
            <span className={styles.versionBadge}>v1.0</span>
          </div>
          <p className={styles.brandTagline}>SVG to React (JSX / TSX) & CSS Data-URI Studio</p>
        </div>
      </div>

      <div className={styles.actions}>
        {/* Presets Dropdown */}
        <div className={styles.dropdownContainer}>
          <button 
            className={styles.presetButton}
            onClick={() => setPresetsOpen(!presetsOpen)}
            aria-expanded={presetsOpen}
          >
            <Sparkles size={16} className={styles.sparkleIcon} />
            <span>Load Preset SVG</span>
            <ChevronDown size={14} className={presetsOpen ? styles.chevronUp : ''} />
          </button>

          {presetsOpen && (
            <>
              <div className={styles.backdrop} onClick={() => setPresetsOpen(false)} />
              <div className={styles.dropdownMenu}>
                <div className={styles.dropdownHeader}>Sample Vector Assets</div>
                {SVG_PRESETS.map(preset => (
                  <button
                    key={preset.id}
                    className={`${styles.dropdownItem} ${activePresetId === preset.id ? styles.activeItem : ''}`}
                    onClick={() => {
                      onLoadPreset(preset);
                      setPresetsOpen(false);
                    }}
                  >
                    <span className={styles.presetBadge}>{preset.badge}</span>
                    <span className={styles.presetLabel}>{preset.name}</span>
                    {activePresetId === preset.id && <Check size={14} className={styles.checkIcon} />}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        {/* 100% Client-Side Badge */}
        <div className={styles.privacyPill} title="100% Client-Side Processing. No SVGs leave your device.">
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
