import React from 'react';
import styles from './VariableEditor.module.css';
import { Variable, Braces, Eye, CheckCircle2 } from 'lucide-react';

export function VariableEditor({
  detectedVariables,
  variableValues,
  onVariableChange,
  resolvedSystemPrompt,
  resolvedUserPrompt
}) {
  if (detectedVariables.length === 0) {
    return (
      <div className={styles.emptyContainer}>
        <div className={styles.emptyCard}>
          <Braces size={18} className={styles.emptyIcon} />
          <div className={styles.emptyText}>
            <strong>No prompt template variables detected.</strong>
            <span>Use <code>{"{{variable_name}}"}</code> in your System or User prompt to enable dynamic variable templating.</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.headerTitle}>
          <Variable size={16} className={styles.titleIcon} />
          <span>Dynamic Variables Test Bench ({detectedVariables.length} detected)</span>
        </div>
      </div>

      <div className={styles.contentGrid}>
        {/* Left Column: Variable Input Fields */}
        <div className={styles.variablesList}>
          <div className={styles.sectionTitle}>Fill Variable Values:</div>
          {detectedVariables.map(varName => (
            <div key={varName} className={styles.varRow}>
              <label className={styles.varLabel}>
                <code>{`{{${varName}}}`}</code>
              </label>
              <input
                type="text"
                className={styles.varInput}
                placeholder={`Value for ${varName}...`}
                value={variableValues[varName] || ''}
                onChange={(e) => onVariableChange(varName, e.target.value)}
              />
            </div>
          ))}
        </div>

        {/* Right Column: Live Resolved Preview */}
        <div className={styles.previewBox}>
          <div className={styles.sectionTitle}>
            <Eye size={14} />
            <span>Resolved Prompt Preview:</span>
          </div>
          <div className={styles.previewContent}>
            {resolvedSystemPrompt && (
              <div className={styles.resolvedBlock}>
                <span className={styles.blockBadge}>System:</span>
                <p>{resolvedSystemPrompt}</p>
              </div>
            )}
            {resolvedUserPrompt && (
              <div className={styles.resolvedBlock}>
                <span className={styles.blockBadgeUser}>User:</span>
                <p>{resolvedUserPrompt}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
