import React from 'react';
import styles from './OptionsPanel.module.css';
import { Sliders, Settings2, Type } from 'lucide-react';

export function OptionsPanel({
  componentName,
  setComponentName,
  useCurrentColor,
  setUseCurrentColor,
  isMemo,
  setIsMemo,
  isForwardRef,
  setIsForwardRef,
  isDefaultExport,
  setIsDefaultExport
}) {
  return (
    <div className={styles.panelContainer}>
      <div className={styles.panelHeader}>
        <Settings2 size={16} className={styles.titleIcon} />
        <span className={styles.panelTitle}>Component & Export Configuration</span>
      </div>

      <div className={styles.optionsGrid}>
        {/* Component Name Field */}
        <div className={styles.nameGroup}>
          <label className={styles.inputLabel}>
            <Type size={13} />
            <span>Component Name:</span>
          </label>
          <input
            type="text"
            className={styles.nameInput}
            value={componentName}
            onChange={(e) => setComponentName(e.target.value)}
            placeholder="SvgIcon"
          />
        </div>

        {/* Checkbox Toggles */}
        <div className={styles.togglesGroup}>
          <label className={styles.toggleItem}>
            <input
              type="checkbox"
              checked={useCurrentColor}
              onChange={(e) => setUseCurrentColor(e.target.checked)}
            />
            <div className={styles.toggleText}>
              <strong>Use currentColor</strong>
              <span>Replace static fill/stroke with currentColor for easy CSS theming</span>
            </div>
          </label>

          <label className={styles.toggleItem}>
            <input
              type="checkbox"
              checked={isMemo}
              onChange={(e) => setIsMemo(e.target.checked)}
            />
            <div className={styles.toggleText}>
              <strong>React.memo</strong>
              <span>Wrap component in React.memo for render optimization</span>
            </div>
          </label>

          <label className={styles.toggleItem}>
            <input
              type="checkbox"
              checked={isForwardRef}
              onChange={(e) => setIsForwardRef(e.target.checked)}
            />
            <div className={styles.toggleText}>
              <strong>React.forwardRef</strong>
              <span>Forward ref directly to root &lt;svg&gt; DOM node</span>
            </div>
          </label>

          <label className={styles.toggleItem}>
            <input
              type="checkbox"
              checked={isDefaultExport}
              onChange={(e) => setIsDefaultExport(e.target.checked)}
            />
            <div className={styles.toggleText}>
              <strong>Default Export</strong>
              <span>Include export default {componentName || 'SvgIcon'}</span>
            </div>
          </label>
        </div>
      </div>
    </div>
  );
}
