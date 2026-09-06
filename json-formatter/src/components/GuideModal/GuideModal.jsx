import React, { useState } from 'react';
import {
  HelpCircle,
  X,
  Wand2,
  FileCode,
  Network,
  Sparkles,
  ChevronRight,
  ChevronLeft,
  Copy,
  Check,
  Code
} from 'lucide-react';
import styles from './GuideModal.module.css';

export default function GuideModal({ onLoadSample, onFormat, onChangeViewMode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState(1); // 1, 2, 3
  const [showEmbedCode, setShowEmbedCode] = useState(false);
  const [copied, setCopied] = useState(false);

  const iframeSnippet = `<iframe src="http://localhost:3000/?embed=true" width="100%" height="600px" style="border:none;" />`;

  const handleCopy = () => {
    navigator.clipboard.writeText(iframeSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleStep1Try = () => {
    if (onLoadSample) onLoadSample('apiResponse');
    setStep(2);
  };

  const handleStep2Try = () => {
    if (onFormat) onFormat();
    setStep(3);
  };

  const handleStep3Try = () => {
    if (onChangeViewMode) onChangeViewMode('tree');
    setIsOpen(false);
  };

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => {
          setStep(1);
          setShowEmbedCode(false);
          setIsOpen(true);
        }}
        className={styles.floatingGuideBtn}
        title="Quick Guide & Try Me"
      >
        <Sparkles size={16} className={styles.sparkleIcon} />
        <span>Quick Guide</span>
      </button>

      {/* Clean 1-Card Guide Modal */}
      {isOpen && (
        <div className={styles.backdrop} onClick={() => setIsOpen(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className={styles.header}>
              <div className={styles.titleGroup}>
                <span className={styles.badge}>Step {step} of 3</span>
                <h3 className={styles.title}>How to Use</h3>
              </div>
              <button onClick={() => setIsOpen(false)} className={styles.closeBtn}>
                <X size={18} />
              </button>
            </div>

            {/* Step Progress Bar */}
            <div className={styles.progressBar}>
              <div className={`${styles.progressDot} ${step >= 1 ? styles.activeDot : ''}`} onClick={() => setStep(1)}>1</div>
              <div className={`${styles.progressLine} ${step >= 2 ? styles.activeLine : ''}`} />
              <div className={`${styles.progressDot} ${step >= 2 ? styles.activeDot : ''}`} onClick={() => setStep(2)}>2</div>
              <div className={`${styles.progressLine} ${step >= 3 ? styles.activeLine : ''}`} />
              <div className={`${styles.progressDot} ${step >= 3 ? styles.activeDot : ''}`} onClick={() => setStep(3)}>3</div>
            </div>

            {/* Modal Body - Single Step Card */}
            <div className={styles.body}>
              {!showEmbedCode ? (
                <>
                  {step === 1 && (
                    <div className={styles.stepContent}>
                      <div className={styles.iconCircle}>
                        <FileCode size={28} />
                      </div>
                      <h3 className={styles.stepHeader}>1. Paste or Load JSON</h3>
                      <p className={styles.stepText}>
                        Paste raw JSON into the editor. Or click below to load a sample JSON payload right now!
                      </p>
                      <button onClick={handleStep1Try} className={styles.tryBtn}>
                        <Sparkles size={16} />
                        <span>Try Me: Load Sample JSON</span>
                        <ChevronRight size={16} />
                      </button>
                    </div>
                  )}

                  {step === 2 && (
                    <div className={styles.stepContent}>
                      <div className={`${styles.iconCircle} ${styles.formatCircle}`}>
                        <Wand2 size={28} />
                      </div>
                      <h3 className={styles.stepHeader}>2. Format & Auto-Fix</h3>
                      <p className={styles.stepText}>
                        Click "Format" to clean up indents, or "Auto-Fix" to repair unquoted keys, single quotes, and trailing commas.
                      </p>
                      <button onClick={handleStep2Try} className={styles.tryBtn}>
                        <Wand2 size={16} />
                        <span>Try Me: Format JSON Now</span>
                        <ChevronRight size={16} />
                      </button>
                    </div>
                  )}

                  {step === 3 && (
                    <div className={styles.stepContent}>
                      <div className={`${styles.iconCircle} ${styles.treeCircle}`}>
                        <Network size={28} />
                      </div>
                      <h3 className={styles.stepHeader}>3. Explore Tree & Export</h3>
                      <p className={styles.stepText}>
                        Explore nested objects in the visual Tree View, filter keys, or click "Convert To..." to export to YAML/CSV.
                      </p>
                      <button onClick={handleStep3Try} className={styles.tryBtn}>
                        <Network size={16} />
                        <span>Try Me: Switch to Tree View & Finish</span>
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <div className={styles.embedContent}>
                  <div className={styles.embedTitle}>
                    <Code size={18} />
                    <span>Link in React Platform (iframe)</span>
                  </div>
                  <p className={styles.embedText}>
                    Use this clean iframe tag to embed this tool into your platform:
                  </p>
                  <pre className={styles.codeBlock}>{iframeSnippet}</pre>
                  <button onClick={handleCopy} className={styles.copyBtn}>
                    {copied ? <Check size={14} /> : <Copy size={14} />}
                    <span>{copied ? 'Copied to Clipboard!' : 'Copy iframe Tag'}</span>
                  </button>
                </div>
              )}
            </div>

            {/* Footer Navigation */}
            <div className={styles.footer}>
              <button
                onClick={() => setShowEmbedCode(!showEmbedCode)}
                className={styles.embedToggleBtn}
              >
                {showEmbedCode ? '← Back to Guide' : 'Need iframe Embed Code?'}
              </button>

              {!showEmbedCode && (
                <div className={styles.navBtns}>
                  {step > 1 && (
                    <button onClick={() => setStep(s => s - 1)} className={styles.backBtn}>
                      <ChevronLeft size={16} /> Back
                    </button>
                  )}
                  {step < 3 && (
                    <button onClick={() => setStep(s => s + 1)} className={styles.nextBtn}>
                      Next <ChevronRight size={16} />
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
