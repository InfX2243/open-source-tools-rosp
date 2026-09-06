import React from 'react';
import {
  Wand2,
  Minimize2,
  Wrench,
  Trash2,
  Copy,
  Download,
  FileCode,
  LayoutGrid,
  Code,
  Network,
  FileType,
  Check,
  Upload
} from 'lucide-react';
import styles from './Toolbar.module.css';

export default function Toolbar({
  onFormat,
  onMinify,
  onRepair,
  onClear,
  onCopy,
  onDownload,
  onUpload,
  onLoadSample,
  indent,
  onChangeIndent,
  viewMode,
  onChangeViewMode,
  onOpenConverter,
  isCopied,
  isValid
}) {
  return (
    <div className={styles.toolbarContainer}>
      <div className={styles.mainActions}>
        {/* Format / Prettify */}
        <button
          onClick={onFormat}
          className={`${styles.actionBtn} ${styles.primaryBtn}`}
          title="Format JSON with indent spacing (Ctrl+Shift+F)"
        >
          <Wand2 size={16} />
          <span>Format</span>
        </button>

        {/* Minify */}
        <button
          onClick={onMinify}
          className={styles.actionBtn}
          title="Minify JSON string (Ctrl+Shift+M)"
        >
          <Minimize2 size={16} />
          <span>Minify</span>
        </button>

        {/* Auto Repair */}
        <button
          onClick={onRepair}
          className={`${styles.actionBtn} ${styles.repairBtn}`}
          title="Auto-repair common JSON errors (quotes, trailing commas)"
        >
          <Wrench size={16} />
          <span>Auto-Fix</span>
        </button>

        {/* Convert Modal Trigger */}
        <button
          onClick={onOpenConverter}
          className={`${styles.actionBtn} ${styles.convertBtn}`}
          title="Convert JSON to YAML, CSV, XML, or JS Object"
        >
          <FileType size={16} />
          <span>Convert To...</span>
        </button>

        <div className={styles.divider} />

        {/* Indent Selector */}
        <div className={styles.indentGroup}>
          <label className={styles.indentLabel}>Indent:</label>
          <select
            value={indent}
            onChange={(e) => onChangeIndent(e.target.value)}
            className={styles.indentSelect}
          >
            <option value="2">2 Spaces</option>
            <option value="4">4 Spaces</option>
            <option value="tab">Tab</option>
          </select>
        </div>

        {/* Samples Selector */}
        <div className={styles.sampleGroup}>
          <select
            onChange={(e) => {
              if (e.target.value) {
                onLoadSample(e.target.value);
                e.target.value = '';
              }
            }}
            className={styles.sampleSelect}
            defaultValue=""
          >
            <option value="" disabled>Load Sample JSON...</option>
            <option value="apiResponse">REST API Response</option>
            <option value="ecommerce">E-Commerce Order</option>
            <option value="malformed">Malformed JSON (Test Auto-Fix)</option>
          </select>
        </div>
      </div>

      <div className={styles.rightActions}>
        {/* View Mode Switcher */}
        <div className={styles.viewModeGroup}>
          <button
            onClick={() => onChangeViewMode('split')}
            className={`${styles.viewBtn} ${viewMode === 'split' ? styles.activeView : ''}`}
            title="Split Editor & Tree View"
          >
            <LayoutGrid size={15} />
            <span>Split</span>
          </button>
          <button
            onClick={() => onChangeViewMode('code')}
            className={`${styles.viewBtn} ${viewMode === 'code' ? styles.activeView : ''}`}
            title="Code Editor Only"
          >
            <Code size={15} />
            <span>Code</span>
          </button>
          <button
            onClick={() => onChangeViewMode('tree')}
            className={`${styles.viewBtn} ${viewMode === 'tree' ? styles.activeView : ''}`}
            title="Interactive Tree View Only"
          >
            <Network size={15} />
            <span>Tree</span>
          </button>
        </div>

        <div className={styles.divider} />

        {/* File Upload */}
        <label className={styles.iconBtn} title="Upload .json file">
          <Upload size={16} />
          <input
            type="file"
            accept=".json,application/json,text/plain"
            onChange={onUpload}
            style={{ display: 'none' }}
          />
        </label>

        {/* Copy */}
        <button
          onClick={onCopy}
          className={`${styles.iconBtn} ${isCopied ? styles.copied : ''}`}
          title="Copy formatted JSON to clipboard"
        >
          {isCopied ? <Check size={16} /> : <Copy size={16} />}
        </button>

        {/* Download */}
        <button
          onClick={onDownload}
          className={styles.iconBtn}
          title="Download as .json file"
        >
          <Download size={16} />
        </button>

        {/* Clear */}
        <button
          onClick={onClear}
          className={`${styles.iconBtn} ${styles.clearBtn}`}
          title="Clear Editor"
        >
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  );
}
