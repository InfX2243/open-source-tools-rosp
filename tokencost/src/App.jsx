import React, { useState, useEffect, useMemo } from 'react';
import styles from './App.module.css';
import { 
  Coins, 
  Sun, 
  Moon, 
  Copy, 
  Check, 
  Trash2, 
  Code2, 
  DollarSign, 
  Braces, 
  Download,
  ChevronDown
} from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/components/prism-clike';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-json';

import { countTokens, getTextStats } from './core/tokenizer';
import { extractVariables, interpolatePrompt } from './core/templateEngine';
import { LLM_MODELS, calculateCost } from './core/models';
import { generateSdkCode, SDK_TARGETS } from './core/generators';

function highlightCode(code, langName) {
  if (!code) return '';
  try {
    const grammar = Prism.languages[langName] || Prism.languages.javascript || Prism.languages.python;
    if (grammar) {
      return Prism.highlight(code, grammar, langName);
    }
  } catch {}
  return code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

const DEFAULT_PROMPT = `Summarize the architecture of a high-throughput RAG pipeline.
Include details on:
1. Vector database indexing & embedding model
2. Re-ranking strategies
3. Handling context window limits with token compression`;

export function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('tokencost_theme') || 'dark');
  
  // Prompt states
  const [systemPrompt, setSystemPrompt] = useState('You are a helpful and concise AI assistant.');
  const [userPrompt, setUserPrompt] = useState(DEFAULT_PROMPT);
  const [outputTokens, setOutputTokens] = useState(300);
  const [variableValues, setVariableValues] = useState({});
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);

  // Right pane tab: 'cost' or 'code'
  const [activeTab, setActiveTab] = useState('cost'); // 'cost' | 'code'
  const [requestVolume, setRequestVolume] = useState(1000); // 1, 1000, 10000, 1000000
  const [selectedModelId, setSelectedModelId] = useState('gpt-4o');
  const [activeSdkId, setActiveSdkId] = useState('openai-python');
  const [sdkDropdownOpen, setSdkDropdownOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  // Sync theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('tokencost_theme', theme);
  }, [theme]);

  // Extract variables
  const detectedVariables = useMemo(() => {
    const combined = `${showSystemPrompt ? systemPrompt : ''} ${userPrompt}`;
    return extractVariables(combined);
  }, [systemPrompt, userPrompt, showSystemPrompt]);

  // Interpolate prompt
  const resolvedSystemPrompt = useMemo(() => {
    return showSystemPrompt ? interpolatePrompt(systemPrompt, variableValues) : '';
  }, [systemPrompt, variableValues, showSystemPrompt]);

  const resolvedUserPrompt = useMemo(() => {
    return interpolatePrompt(userPrompt, variableValues);
  }, [userPrompt, variableValues]);

  // Token Stats
  const systemStats = useMemo(() => getTextStats(resolvedSystemPrompt), [resolvedSystemPrompt]);
  const userStats = useMemo(() => getTextStats(resolvedUserPrompt), [resolvedUserPrompt]);
  const totalInputTokens = systemStats.tokens + userStats.tokens;
  const totalTokens = totalInputTokens + outputTokens;

  // Selected model
  const selectedModel = useMemo(() => {
    return LLM_MODELS.find(m => m.id === selectedModelId) || LLM_MODELS[0];
  }, [selectedModelId]);

  // Cost comparison list
  const modelCosts = useMemo(() => {
    return LLM_MODELS.map(model => {
      const costData = calculateCost(model, totalInputTokens, outputTokens, requestVolume);
      return {
        ...model,
        ...costData
      };
    }).sort((a, b) => a.totalCost - b.totalCost);
  }, [totalInputTokens, outputTokens, requestVolume]);

  // Generate SDK Code
  const activeSdk = useMemo(() => {
    return SDK_TARGETS.find(s => s.id === activeSdkId) || SDK_TARGETS[0];
  }, [activeSdkId]);

  const generatedCode = useMemo(() => {
    return generateSdkCode(activeSdkId, {
      systemPrompt: resolvedSystemPrompt,
      userPrompt: resolvedUserPrompt,
      outputTokens,
      selectedModel
    });
  }, [activeSdkId, resolvedSystemPrompt, resolvedUserPrompt, outputTokens, selectedModel]);

  const highlightedHtml = useMemo(() => {
    return highlightCode(generatedCode, activeSdk.prismLang);
  }, [generatedCode, activeSdk.prismLang]);

  const formatPrice = (price) => {
    if (price < 0.0001) return `$${price.toFixed(6)}`;
    if (price < 0.01) return `$${price.toFixed(4)}`;
    return `$${price.toFixed(2)}`;
  };

  const handleVariableChange = (name, val) => {
    setVariableValues(prev => ({
      ...prev,
      [name]: val
    }));
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(generatedCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([generatedCode], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `llm_request.${activeSdk.extension}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={styles.appContainer}>
      {/* Top Navbar */}
      <header className={styles.navbar}>
        <div className={styles.brand}>
          <div className={styles.brandIcon}>
            <Coins size={20} />
          </div>
          <div>
            <h1 className={styles.brandTitle}>TokenCost</h1>
            <span className={styles.brandSubtitle}>AI Prompt, Token & Cost Calculator</span>
          </div>
        </div>

        <div className={styles.navRight}>
          <button 
            className={styles.themeToggle} 
            onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
            title="Toggle theme"
          >
            {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>
      </header>

      {/* Main 2-Column Studio */}
      <main className={styles.mainStudio}>
        <div className={styles.studioGrid}>
          {/* ================= LEFT: UNIFIED PROMPT BENCH ================= */}
          <div className={styles.leftPane}>
            <div className={styles.promptCard}>
              {/* Card Header with Controls */}
              <div className={styles.cardHeader}>
                <div className={styles.headerLeft}>
                  <strong className={styles.headerTitle}>Prompt</strong>
                </div>

                <div className={styles.headerRight}>
                  <button
                    className={`${styles.headerActionBtn} ${showSystemPrompt ? styles.activeHeaderBtn : ''}`}
                    onClick={() => setShowSystemPrompt(!showSystemPrompt)}
                  >
                    {showSystemPrompt ? '– System Instructions' : '+ System Instructions'}
                  </button>
                  <button 
                    className={styles.headerActionBtn}
                    onClick={() => {
                      setSystemPrompt('');
                      setUserPrompt('');
                      setVariableValues({});
                    }}
                    title="Clear prompt"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>

              {/* Optional System Prompt */}
              {showSystemPrompt && (
                <div className={styles.systemBox}>
                  <span className={styles.fieldLabel}>System Instructions</span>
                  <textarea
                    className={styles.systemTextarea}
                    value={systemPrompt}
                    onChange={(e) => setSystemPrompt(e.target.value)}
                    placeholder="System instructions or persona... (supports {{variables}})"
                    spellCheck={false}
                  />
                </div>
              )}

              {/* Main Prompt Input */}
              <div className={styles.promptBox}>
                <textarea
                  className={styles.mainTextarea}
                  value={userPrompt}
                  onChange={(e) => setUserPrompt(e.target.value)}
                  placeholder="Enter your prompt here... Use {{variable_name}} to test dynamic variables."
                  spellCheck={false}
                />
              </div>

              {/* Dynamic Variables Test Bench */}
              {detectedVariables.length > 0 && (
                <div className={styles.variablesBox}>
                  <div className={styles.variablesHeader}>
                    <Braces size={13} className={styles.varIcon} />
                    <span>Variables ({detectedVariables.length})</span>
                  </div>
                  <div className={styles.varsList}>
                    {detectedVariables.map(varName => (
                      <div key={varName} className={styles.varItem}>
                        <span className={styles.varLabel}>{`{{${varName}}}`}</span>
                        <input
                          type="text"
                          className={styles.varInput}
                          placeholder={`Value for ${varName}...`}
                          value={variableValues[varName] || ''}
                          onChange={(e) => handleVariableChange(varName, e.target.value)}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Bottom Token Stats & Output Tokens Estimator */}
              <div className={styles.tokenBar}>
                <div className={styles.tokenChip}>
                  <span>Prompt:</span>
                  <strong>{totalInputTokens} tokens</strong>
                </div>

                <div className={styles.outputSliderWrap}>
                  <span className={styles.sliderLabel} title="Estimated tokens generated by the AI in response">
                    Est. Output Tokens:
                  </span>
                  <input
                    type="number"
                    min="10"
                    max="8000"
                    step="50"
                    value={outputTokens}
                    onChange={(e) => setOutputTokens(Math.max(1, Number(e.target.value) || 0))}
                    className={styles.outputNumberInput}
                  />
                  <div className={styles.quickOutputPills}>
                    {[
                      { label: 'Short', val: 150 },
                      { label: 'Medium', val: 500 },
                      { label: 'Long', val: 1500 }
                    ].map(p => (
                      <button
                        key={p.val}
                        type="button"
                        className={`${styles.quickPill} ${outputTokens === p.val ? styles.activeQuickPill : ''}`}
                        onClick={() => setOutputTokens(p.val)}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className={styles.totalBadge}>
                  Total: <strong>{totalTokens} tokens</strong>
                </div>
              </div>
            </div>
          </div>

          {/* ================= RIGHT: COST MATRIX & CODE EXPORT ================= */}
          <div className={styles.rightPane}>
            {/* View Tab Switcher */}
            <div className={styles.tabNav}>
              <button
                className={`${styles.tabBtn} ${activeTab === 'cost' ? styles.activeTabBtn : ''}`}
                onClick={() => setActiveTab('cost')}
              >
                <DollarSign size={15} />
                <span>Cost Comparison</span>
              </button>

              <button
                className={`${styles.tabBtn} ${activeTab === 'code' ? styles.activeTabBtn : ''}`}
                onClick={() => setActiveTab('code')}
              >
                <Code2 size={15} />
                <span>Export SDK Code</span>
              </button>
            </div>

            {/* TAB 1: COST CALCULATOR */}
            {activeTab === 'cost' && (
              <div className={styles.costContainer}>
                {/* Volume Selector Header */}
                <div className={styles.volumeHeader}>
                  <span className={styles.volumeLabel}>Simulate Requests:</span>
                  <div className={styles.volumeGroup}>
                    {[
                      { label: '1 Call', val: 1 },
                      { label: '1,000 (1K)', val: 1000 },
                      { label: '10,000 (10K)', val: 10000 },
                      { label: '1 Million', val: 1000000 }
                    ].map(v => (
                      <button
                        key={v.val}
                        className={`${styles.volPill} ${requestVolume === v.val ? styles.activeVolPill : ''}`}
                        onClick={() => setRequestVolume(v.val)}
                      >
                        {v.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Model Pricing Table */}
                <div className={styles.modelTable}>
                  {modelCosts.map((model, idx) => {
                    const isSelected = selectedModelId === model.id;

                    return (
                      <div
                        key={model.id}
                        className={`${styles.modelRow} ${isSelected ? styles.selectedModelRow : ''}`}
                        onClick={() => {
                          setSelectedModelId(model.id);
                          if (model.provider === 'Anthropic') setActiveSdkId('anthropic-python');
                          else if (model.provider === 'Google') setActiveSdkId('gemini-python');
                          else setActiveSdkId('openai-python');
                        }}
                      >
                        <div className={styles.modelMeta}>
                          <div className={styles.modelNameRow}>
                            <strong className={styles.modelNameText}>{model.name}</strong>
                            <span className={styles.providerPill}>{model.provider}</span>
                            {idx === 0 && <span className={styles.lowestBadge}>Lowest Cost</span>}
                          </div>
                          <span className={styles.modelRates}>
                            ${model.inputPricePer1M}/1M in • ${model.outputPricePer1M}/1M out • {model.latency}
                          </span>
                        </div>

                        <div className={styles.modelPriceGroup}>
                          <strong className={styles.priceNumber}>
                            {formatPrice(model.totalCost)}
                          </strong>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* TAB 2: EXPORT SDK CODE */}
            {activeTab === 'code' && (
              <div className={styles.codeContainer}>
                {/* SDK Selector Dropdown Bar */}
                <div className={styles.sdkBar}>
                  <div className={styles.sdkDropdownWrapper}>
                    <button
                      className={styles.sdkDropdownTrigger}
                      onClick={() => setSdkDropdownOpen(!sdkDropdownOpen)}
                    >
                      <Code2 size={15} />
                      <span>{activeSdk.name} ({activeSdk.library})</span>
                      <ChevronDown size={14} />
                    </button>

                    {sdkDropdownOpen && (
                      <div className={styles.sdkMenu}>
                        {SDK_TARGETS.map(t => (
                          <button
                            key={t.id}
                            className={`${styles.sdkOption} ${activeSdkId === t.id ? styles.activeSdkOption : ''}`}
                            onClick={() => {
                              setActiveSdkId(t.id);
                              setSdkDropdownOpen(false);
                            }}
                          >
                            <span>{t.name}</span>
                            <span className={styles.sdkLibText}>{t.library}</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className={styles.codeActions}>
                    <button className={styles.codeActionBtn} onClick={handleDownload}>
                      <Download size={13} />
                      <span>Download</span>
                    </button>
                    <button 
                      className={`${styles.codeActionBtn} ${copied ? styles.copiedBtn : styles.primaryCopyBtn}`} 
                      onClick={handleCopy}
                    >
                      {copied ? <Check size={13} /> : <Copy size={13} />}
                      <span>{copied ? 'Copied!' : 'Copy Code'}</span>
                    </button>
                  </div>
                </div>

                {/* Code Viewer */}
                <pre className={styles.codePre}>
                  <code 
                    className={`language-${activeSdk.prismLang}`}
                    dangerouslySetInnerHTML={{ __html: highlightedHtml }}
                  />
                </pre>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
