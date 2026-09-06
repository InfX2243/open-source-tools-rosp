import React from 'react';
import { formatBytes } from '../../utils/jsonFormatter';
import styles from './StatsBar.module.css';

export default function StatsBar({ stats, isValid, isEmbedded }) {
  if (isEmbedded) return null;

  return (
    <footer className={styles.statsBar}>
      <div className={styles.statsGroup}>
        <div className={styles.statItem}>
          <span className={styles.statLabel}>Lines:</span>
          <span className={styles.statValue}>{stats.lines.toLocaleString()}</span>
        </div>
        <div className={styles.statDivider} />

        <div className={styles.statItem}>
          <span className={styles.statLabel}>Size:</span>
          <span className={styles.statValue}>{formatBytes(stats.bytes)}</span>
        </div>
        <div className={styles.statDivider} />

        {isValid && (
          <>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Keys:</span>
              <span className={styles.statValue}>{stats.keys.toLocaleString()}</span>
            </div>
            <div className={styles.statDivider} />

            <div className={styles.statItem}>
              <span className={styles.statLabel}>Max Depth:</span>
              <span className={styles.statValue}>{stats.depth}</span>
            </div>
          </>
        )}
      </div>

      <div className={styles.footerBrand}>
        <span>ROSP Open Source Tool</span>
        <span className={styles.dot}>•</span>
        <span>100% Client-Side</span>
      </div>
    </footer>
  );
}
