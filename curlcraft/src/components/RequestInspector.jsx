import React, { useState } from 'react';
import styles from './RequestInspector.module.css';
import { 
  Sliders, 
  KeyRound, 
  Hash, 
  FileText, 
  Plus, 
  Trash2, 
  ChevronDown, 
  ChevronRight,
  Shield,
  Layers
} from 'lucide-react';

export function RequestInspector({
  parsedReq,
  onUpdateHeaders,
  onUpdateParams,
  onUpdateMethod,
  onUpdateBaseUrl
}) {
  const [activeTab, setActiveTab] = useState('params'); // 'params' | 'headers' | 'auth' | 'body'

  const handleHeaderToggle = (id) => {
    const updated = parsedReq.headers.map(h => 
      h.id === id ? { ...h, enabled: !h.enabled } : h
    );
    onUpdateHeaders(updated);
  };

  const handleHeaderChange = (id, field, val) => {
    const updated = parsedReq.headers.map(h => 
      h.id === id ? { ...h, [field]: val } : h
    );
    onUpdateHeaders(updated);
  };

  const handleAddHeader = () => {
    const newHeader = {
      id: Math.random().toString(36).substr(2, 9),
      name: '',
      value: '',
      enabled: true
    };
    onUpdateHeaders([...parsedReq.headers, newHeader]);
  };

  const handleDeleteHeader = (id) => {
    onUpdateHeaders(parsedReq.headers.filter(h => h.id !== id));
  };

  const handleParamToggle = (id) => {
    const updated = parsedReq.queryParams.map(p => 
      p.id === id ? { ...p, enabled: !p.enabled } : p
    );
    onUpdateParams(updated);
  };

  const handleParamChange = (id, field, val) => {
    const updated = parsedReq.queryParams.map(p => 
      p.id === id ? { ...p, [field]: val } : p
    );
    onUpdateParams(updated);
  };

  const handleAddParam = () => {
    const newParam = {
      id: Math.random().toString(36).substr(2, 9),
      key: '',
      value: '',
      enabled: true
    };
    onUpdateParams([...parsedReq.queryParams, newParam]);
  };

  const handleDeleteParam = (id) => {
    onUpdateParams(parsedReq.queryParams.filter(p => p.id !== id));
  };

  return (
    <div className={styles.inspectorContainer}>
      {/* Inspector Tabs */}
      <div className={styles.tabHeader}>
        <div className={styles.tabTitle}>
          <Layers size={16} className={styles.titleIcon} />
          <span>Parsed Request Inspector</span>
        </div>

        <div className={styles.tabButtons}>
          <button
            className={`${styles.tabBtn} ${activeTab === 'params' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('params')}
          >
            <Hash size={14} />
            <span>Query Params ({parsedReq.queryParams.length})</span>
          </button>

          <button
            className={`${styles.tabBtn} ${activeTab === 'headers' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('headers')}
          >
            <Sliders size={14} />
            <span>Headers ({parsedReq.headers.length})</span>
          </button>

          <button
            className={`${styles.tabBtn} ${activeTab === 'auth' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('auth')}
          >
            <Shield size={14} />
            <span>Auth {parsedReq.auth ? `(${parsedReq.auth.type})` : ''}</span>
          </button>

          <button
            className={`${styles.tabBtn} ${activeTab === 'body' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('body')}
          >
            <FileText size={14} />
            <span>Body ({parsedReq.body.type})</span>
          </button>
        </div>
      </div>

      {/* Tab Contents */}
      <div className={styles.tabContent}>
        {/* QUERY PARAMS */}
        {activeTab === 'params' && (
          <div className={styles.tableWrapper}>
            <div className={styles.tableHeaderRow}>
              <span className={styles.colCheck}>Active</span>
              <span className={styles.colKey}>Parameter Key</span>
              <span className={styles.colVal}>Parameter Value</span>
              <span className={styles.colAction}>Action</span>
            </div>

            {parsedReq.queryParams.length === 0 ? (
              <div className={styles.emptyState}>No query parameters detected in URL.</div>
            ) : (
              parsedReq.queryParams.map(param => (
                <div key={param.id} className={styles.tableRow}>
                  <div className={styles.colCheck}>
                    <input
                      type="checkbox"
                      checked={param.enabled}
                      onChange={() => handleParamToggle(param.id)}
                    />
                  </div>
                  <div className={styles.colKey}>
                    <input
                      type="text"
                      className={styles.inputField}
                      value={param.key}
                      placeholder="key"
                      onChange={(e) => handleParamChange(param.id, 'key', e.target.value)}
                    />
                  </div>
                  <div className={styles.colVal}>
                    <input
                      type="text"
                      className={styles.inputField}
                      value={param.value}
                      placeholder="value"
                      onChange={(e) => handleParamChange(param.id, 'value', e.target.value)}
                    />
                  </div>
                  <div className={styles.colAction}>
                    <button 
                      className={styles.deleteBtn} 
                      onClick={() => handleDeleteParam(param.id)}
                      title="Delete Parameter"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>
              ))
            )}

            <button className={styles.addRowBtn} onClick={handleAddParam}>
              <Plus size={14} />
              <span>Add Query Parameter</span>
            </button>
          </div>
        )}

        {/* HEADERS */}
        {activeTab === 'headers' && (
          <div className={styles.tableWrapper}>
            <div className={styles.tableHeaderRow}>
              <span className={styles.colCheck}>Active</span>
              <span className={styles.colKey}>Header Name</span>
              <span className={styles.colVal}>Header Value</span>
              <span className={styles.colAction}>Action</span>
            </div>

            {parsedReq.headers.length === 0 ? (
              <div className={styles.emptyState}>No headers detected in command.</div>
            ) : (
              parsedReq.headers.map(header => (
                <div key={header.id} className={styles.tableRow}>
                  <div className={styles.colCheck}>
                    <input
                      type="checkbox"
                      checked={header.enabled}
                      onChange={() => handleHeaderToggle(header.id)}
                    />
                  </div>
                  <div className={styles.colKey}>
                    <input
                      type="text"
                      className={styles.inputField}
                      value={header.name}
                      placeholder="Header-Name"
                      onChange={(e) => handleHeaderChange(header.id, 'name', e.target.value)}
                    />
                  </div>
                  <div className={styles.colVal}>
                    <input
                      type="text"
                      className={styles.inputField}
                      value={header.value}
                      placeholder="Value"
                      onChange={(e) => handleHeaderChange(header.id, 'value', e.target.value)}
                    />
                  </div>
                  <div className={styles.colAction}>
                    <button 
                      className={styles.deleteBtn} 
                      onClick={() => handleDeleteHeader(header.id)}
                      title="Delete Header"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>
              ))
            )}

            <button className={styles.addRowBtn} onClick={handleAddHeader}>
              <Plus size={14} />
              <span>Add Header</span>
            </button>
          </div>
        )}

        {/* AUTH */}
        {activeTab === 'auth' && (
          <div className={styles.authContainer}>
            {!parsedReq.auth ? (
              <div className={styles.emptyState}>
                No authorization credentials detected (-u, --user, or Authorization header).
              </div>
            ) : parsedReq.auth.type === 'bearer' ? (
              <div className={styles.authCard}>
                <div className={styles.authHeader}>
                  <KeyRound size={16} className={styles.authIcon} />
                  <strong>Bearer Token Authentication</strong>
                </div>
                <div className={styles.authField}>
                  <label>Token:</label>
                  <code className={styles.authCode}>{parsedReq.auth.token}</code>
                </div>
              </div>
            ) : (
              <div className={styles.authCard}>
                <div className={styles.authHeader}>
                  <KeyRound size={16} className={styles.authIcon} />
                  <strong>HTTP Basic Authentication</strong>
                </div>
                <div className={styles.authField}>
                  <label>Username:</label>
                  <code className={styles.authCode}>{parsedReq.auth.username || '(empty)'}</code>
                </div>
                <div className={styles.authField}>
                  <label>Password:</label>
                  <code className={styles.authCode}>{parsedReq.auth.password || '(empty)'}</code>
                </div>
              </div>
            )}
          </div>
        )}

        {/* BODY */}
        {activeTab === 'body' && (
          <div className={styles.bodyContainer}>
            {parsedReq.body.type === 'none' ? (
              <div className={styles.emptyState}>No request body or payload present (typical for GET requests).</div>
            ) : parsedReq.body.type === 'json' && parsedReq.body.json ? (
              <pre className={styles.bodyPre}>
                {JSON.stringify(parsedReq.body.json, null, 2)}
              </pre>
            ) : parsedReq.body.type === 'form-data' ? (
              <div className={styles.tableWrapper}>
                <div className={styles.tableHeaderRow}>
                  <span className={styles.colKey}>Field Key</span>
                  <span className={styles.colVal}>Value / File</span>
                  <span className={styles.colCheck}>Type</span>
                </div>
                {parsedReq.body.formData.map((item, idx) => (
                  <div key={idx} className={styles.tableRow}>
                    <span className={styles.colKey}><strong>{item.key}</strong></span>
                    <span className={styles.colVal}>{item.value}</span>
                    <span className={styles.colCheck}>{item.type}</span>
                  </div>
                ))}
              </div>
            ) : (
              <pre className={styles.bodyPre}>
                {parsedReq.body.raw}
              </pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
