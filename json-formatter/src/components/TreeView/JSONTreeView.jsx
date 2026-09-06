import React, { useState } from 'react';
import {
  ChevronRight,
  ChevronDown,
  Search,
  ChevronsDownUp,
  ChevronsUpDown,
  Copy,
  Check,
  Network
} from 'lucide-react';
import styles from './JSONTreeView.module.css';

export default function JSONTreeView({ data, isValid }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedPaths, setExpandedPaths] = useState({ '$': true });
  const [copiedPath, setCopiedPath] = useState(null);

  const toggleExpand = (path) => {
    setExpandedPaths((prev) => ({
      ...prev,
      [path]: !prev[path]
    }));
  };

  const expandAll = () => {
    const allPaths = {};
    function collectPaths(obj, currentPath = '$') {
      allPaths[currentPath] = true;
      if (obj !== null && typeof obj === 'object') {
        Object.entries(obj).forEach(([key, val]) => {
          const nextPath = Array.isArray(obj) ? `${currentPath}[${key}]` : `${currentPath}.${key}`;
          collectPaths(val, nextPath);
        });
      }
    }
    if (data) collectPaths(data);
    setExpandedPaths(allPaths);
  };

  const collapseAll = () => {
    setExpandedPaths({ '$': true });
  };

  const handleCopyPath = (path, e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(path);
    setCopiedPath(path);
    setTimeout(() => setCopiedPath(null), 1500);
  };

  if (!isValid || data === null || data === undefined) {
    return (
      <div className={styles.treeContainer}>
        <div className={styles.treeHeader}>
          <div className={styles.headerTitle}>
            <Network size={15} className={styles.headerIcon} />
            <span>Interactive Tree View</span>
          </div>
        </div>
        <div className={styles.emptyState}>
          <p>Tree View unavailable. Please enter valid JSON syntax in the editor pane.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.treeContainer}>
      <div className={styles.treeHeader}>
        <div className={styles.headerTitle}>
          <Network size={15} className={styles.headerIcon} />
          <span>Interactive Tree View</span>
        </div>

        <div className={styles.treeControls}>
          {/* Search Box */}
          <div className={styles.searchWrapper}>
            <Search size={14} className={styles.searchIcon} />
            <input
              type="text"
              placeholder="Filter keys or values..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={styles.searchInput}
            />
          </div>

          <button onClick={expandAll} className={styles.controlBtn} title="Expand All Nodes">
            <ChevronsUpDown size={15} />
          </button>
          <button onClick={collapseAll} className={styles.controlBtn} title="Collapse All Nodes">
            <ChevronsDownUp size={15} />
          </button>
        </div>
      </div>

      <div className={styles.treeBody}>
        <TreeNode
          name="root"
          value={data}
          path="$"
          expandedPaths={expandedPaths}
          onToggle={toggleExpand}
          onCopyPath={handleCopyPath}
          copiedPath={copiedPath}
          searchQuery={searchQuery.toLowerCase()}
        />
      </div>
    </div>
  );
}

function TreeNode({
  name,
  value,
  path,
  expandedPaths,
  onToggle,
  onCopyPath,
  copiedPath,
  searchQuery
}) {
  const isExpanded = !!expandedPaths[path];
  const isObject = value !== null && typeof value === 'object';
  const isArray = Array.isArray(value);

  // Type badge colors
  let typeLabel = typeof value;
  if (value === null) typeLabel = 'null';
  else if (isArray) typeLabel = 'array';
  else if (isObject) typeLabel = 'object';

  // Search filter matching logic
  const matchesSearch = searchQuery
    ? String(name).toLowerCase().includes(searchQuery) ||
      (!isObject && String(value).toLowerCase().includes(searchQuery))
    : true;

  if (!isObject) {
    if (searchQuery && !matchesSearch) return null;

    return (
      <div className={styles.treeNodeRow}>
        <span className={styles.nodeKey}>{name}:</span>
        <RenderPrimitiveValue value={value} />
        <span className={`${styles.typeBadge} ${styles[typeLabel]}`}>{typeLabel}</span>

        <button
          onClick={(e) => onCopyPath(path, e)}
          className={styles.copyPathBtn}
          title={`Copy path: ${path}`}
        >
          {copiedPath === path ? <Check size={12} /> : <Copy size={12} />}
        </button>
      </div>
    );
  }

  const entries = Object.entries(value);
  const itemCount = entries.length;

  return (
    <div className={styles.treeNodeGroup}>
      <div className={styles.treeNodeHeader} onClick={() => onToggle(path)}>
        <span className={styles.toggleIcon}>
          {isExpanded ? <ChevronDown size={15} /> : <ChevronRight size={15} />}
        </span>
        <span className={styles.nodeKey}>{name}</span>
        <span className={styles.countBadge}>
          {isArray ? `[${itemCount}]` : `{${itemCount}}`}
        </span>
        <span className={`${styles.typeBadge} ${styles[typeLabel]}`}>{typeLabel}</span>

        <button
          onClick={(e) => onCopyPath(path, e)}
          className={styles.copyPathBtn}
          title={`Copy path: ${path}`}
        >
          {copiedPath === path ? <Check size={12} /> : <Copy size={12} />}
        </button>
      </div>

      {isExpanded && (
        <div className={styles.treeChildren}>
          {entries.map(([key, val]) => {
            const childPath = isArray ? `${path}[${key}]` : `${path}.${key}`;
            return (
              <TreeNode
                key={key}
                name={key}
                value={val}
                path={childPath}
                expandedPaths={expandedPaths}
                onToggle={onToggle}
                onCopyPath={onCopyPath}
                copiedPath={copiedPath}
                searchQuery={searchQuery}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}

function RenderPrimitiveValue({ value }) {
  if (value === null) return <span className={styles.valNull}>null</span>;
  if (typeof value === 'boolean') return <span className={styles.valBoolean}>{String(value)}</span>;
  if (typeof value === 'number') return <span className={styles.valNumber}>{value}</span>;
  return <span className={styles.valString}>"{String(value)}"</span>;
}
