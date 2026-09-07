import React, { useState } from 'react';
import styles from './PromptEditor.module.css';
import { Bot, User, Trash2, ClipboardPaste, Sliders, Braces } from 'lucide-react';

export function PromptEditor({
  systemPrompt,
  setSystemPrompt,
  userPrompt,
  setUserPrompt,
  outputTokens,
  setOutputTokens,
  totalInputTokens,
  detectedVariables,
  variableValues,
  onVariableChange,
  onClear,
  onPaste
}) {
  const [activeTab, setActiveTab] = useState('user'); // 'user' | 'system'

  return (
    <div className={styles.editorContainer}>
      {/* Tab Switcher & Actions */}
      <div className={styles.editorHeader}>
        <div className={styles.tabGroup}>
          <button
            className={`${styles.tabBtn} ${activeTab === 'user' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('user')}
          >
            <User size={14} />
            <span>User Prompt</span>
          </button>

          <button
            className={`${styles.tabBtn} ${activeTab === 'system' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('system')}
          >
            <Bot size={14} />
            <span>System Instructions {systemPrompt.trim() ? '•' : ''}</span>
          </button>
        </div>

        <div className={styles.actions}>
          <button className={styles.iconActionBtn} onClick={onPaste} title="Paste from clipboard">
            <ClipboardPaste size={14} />
            <span>Paste</span>
          </button>
          <button 
            className={`${styles.iconActionBtn} ${styles.clearBtn}`} 
            onClick={onClear} 
            disabled={!systemPrompt.trim() && !userPrompt.trim()}
            title="Clear prompt"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {/* Main Textarea */}
      <div className={styles.textareaWrapper}>
        {activeTab === 'user' ? (
          <textarea
            className={styles.textarea}
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            placeholder="Type your user prompt or question here... You can use {{variables}} for templating."
            spellCheck={false}
          />
        ) : (
          <textarea
            className={styles.textarea}
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder="Optional system instructions (e.g. 'You are a concise financial advisor...')"
            spellCheck={false}
          />
        )}
      </div>

      {/* Dynamic Variables inline (only if variables detected) */}
      {detectedVariables.length > 0 && (
        <div className={styles.variablesSection}>
          <div className={styles.variablesHeader}>
            <Braces size={13} className={styles.varIcon} />
            <span>Variables:</span>
          </div>
          <div className={styles.variableGrid}>
            {detectedVariables.map(varName => (
              <div key={varName} className={styles.varChip}>
                <span className={styles.varLabel}>{varName}</span>
                <input
                  type="text"
                  className={styles.varInput}
                  placeholder="value..."
                  value={variableValues[varName] || ''}
                  onChange={(e) => onVariableChange(varName, e.target.value)}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bottom Token & Output Sliders */}
      <div className={styles.editorFooter}>
        <div className={styles.tokenBadge}>
          <span>Input: <strong>{totalInputTokens}</strong> tokens</span>
          <span className={styles.dot}>•</span>
          <span>Max Output: <strong>{outputTokens}</strong></span>
        </div>

        <div className={styles.outputSliderGroup}>
          <span className={styles.sliderLabel}>Output Tokens:</span>
          <input
            type="range"
            min="50"
            max="4000"
            step="50"
            value={outputTokens}
            onChange={(e) => setOutputTokens(Number(e.target.value))}
            className={styles.slider}
          />
          <span className={styles.sliderValue}>{outputTokens}</span>
        </div>
      </div>
    </div>
  );
}
