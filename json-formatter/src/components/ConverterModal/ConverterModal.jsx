import React, { useState, useMemo } from 'react';
import { X, Copy, Check, Download, FileText } from 'lucide-react';
import { jsonToYAML, jsonToCSV, jsonToXML, jsonToJSObject } from '../../utils/converters';
import styles from './ConverterModal.module.css';

export default function ConverterModal({ isOpen, onClose, jsonData }) {
  const [activeTab, setActiveTab] = useState('yaml');
  const [copied, setCopied] = useState(false);

  const convertedOutput = useMemo(() => {
    if (!jsonData) return '// No valid JSON data to convert.';

    switch (activeTab) {
      case 'yaml':
        return jsonToYAML(jsonData);
      case 'csv':
        return jsonToCSV(jsonData);
      case 'xml':
        return jsonToXML(jsonData);
      case 'js':
        return jsonToJSObject(jsonData);
      default:
        return '';
    }
  }, [jsonData, activeTab]);

  if (!isOpen) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(convertedOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleDownload = () => {
    const extensions = { yaml: 'yaml', csv: 'csv', xml: 'xml', js: 'js' };
    const ext = extensions[activeTab] || 'txt';
    const blob = new Blob([convertedOutput], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `converted_data.${ext}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <div className={styles.modalTitle}>
            <FileText size={18} className={styles.titleIcon} />
            <span>Export & Convert JSON Format</span>
          </div>
          <button onClick={onClose} className={styles.closeBtn} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        <div className={styles.tabContainer}>
          <button
            onClick={() => setActiveTab('yaml')}
            className={`${styles.tabBtn} ${activeTab === 'yaml' ? styles.activeTab : ''}`}
          >
            YAML
          </button>
          <button
            onClick={() => setActiveTab('csv')}
            className={`${styles.tabBtn} ${activeTab === 'csv' ? styles.activeTab : ''}`}
          >
            CSV
          </button>
          <button
            onClick={() => setActiveTab('xml')}
            className={`${styles.tabBtn} ${activeTab === 'xml' ? styles.activeTab : ''}`}
          >
            XML
          </button>
          <button
            onClick={() => setActiveTab('js')}
            className={`${styles.tabBtn} ${activeTab === 'js' ? styles.activeTab : ''}`}
          >
            JS Object
          </button>
        </div>

        <div className={styles.previewContainer}>
          <pre className={styles.codePreview}>{convertedOutput}</pre>
        </div>

        <div className={styles.modalFooter}>
          <button onClick={handleDownload} className={styles.downloadBtn}>
            <Download size={15} />
            Download .{activeTab}
          </button>

          <button onClick={handleCopy} className={`${styles.copyBtn} ${copied ? styles.copied : ''}`}>
            {copied ? <Check size={15} /> : <Copy size={15} />}
            {copied ? 'Copied!' : 'Copy Code'}
          </button>
        </div>
      </div>
    </div>
  );
}
