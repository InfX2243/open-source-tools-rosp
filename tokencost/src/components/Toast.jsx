import React from 'react';
import styles from './Toast.module.css';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

export function Toast({ toast, onClose }) {
  if (!toast) return null;

  const icons = {
    success: <CheckCircle size={18} className={styles.iconSuccess} />,
    error: <AlertCircle size={18} className={styles.iconError} />,
    info: <Info size={18} className={styles.iconInfo} />
  };

  return (
    <div className={`${styles.toast} ${styles[toast.type || 'info']}`}>
      <div className={styles.iconWrapper}>
        {icons[toast.type || 'info']}
      </div>
      <div className={styles.message}>{toast.message}</div>
      <button className={styles.closeBtn} onClick={onClose} aria-label="Close">
        <X size={14} />
      </button>
    </div>
  );
}
