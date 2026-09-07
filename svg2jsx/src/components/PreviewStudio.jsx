import React, { useState } from 'react';
import styles from './PreviewStudio.module.css';
import { Eye, RotateCw, FlipHorizontal, FlipVertical, Palette, Maximize2 } from 'lucide-react';

export function PreviewStudio({
  rawSvg,
  parsedSvg,
  previewSize,
  setPreviewSize,
  previewColor,
  setPreviewColor,
  useCustomColor,
  setUseCustomColor
}) {
  const [bgType, setBgType] = useState('checkerboard'); // 'checkerboard' | 'dark' | 'light' | 'white' | 'black'
  const [rotation, setRotation] = useState(0);
  const [flipH, setFlipH] = useState(false);
  const [flipV, setFlipV] = useState(false);

  const sizePresets = [16, 24, 32, 48, 64, 96, 128];

  const handleRotate = () => {
    setRotation(prev => (prev + 90) % 360);
  };

  const transformStyle = {
    transform: `rotate(${rotation}deg) scaleX(${flipH ? -1 : 1}) scaleY(${flipV ? -1 : 1})`,
    transition: 'transform 200ms ease'
  };

  // Modify SVG to respect preview size and color if valid
  let renderableSvg = parsedSvg.cleanedSvg;
  if (useCustomColor && previewColor) {
    renderableSvg = renderableSvg
      .replace(/fill=["'](?!none)[^"']*["']/gi, `fill="${previewColor}"`)
      .replace(/stroke=["'](?!none)[^"']*["']/gi, `stroke="${previewColor}"`);
  }

  return (
    <div className={styles.studioContainer}>
      {/* Studio Header */}
      <div className={styles.studioHeader}>
        <div className={styles.headerLeft}>
          <Eye size={16} className={styles.titleIcon} />
          <span className={styles.studioTitle}>Live Preview Studio</span>
        </div>

        {/* Studio Controls */}
        <div className={styles.headerControls}>
          <button
            className={`${styles.iconBtn} ${flipH ? styles.activeIconBtn : ''}`}
            onClick={() => setFlipH(!flipH)}
            title="Flip Horizontally"
          >
            <FlipHorizontal size={14} />
          </button>

          <button
            className={`${styles.iconBtn} ${flipV ? styles.activeIconBtn : ''}`}
            onClick={() => setFlipV(!flipV)}
            title="Flip Vertically"
          >
            <FlipVertical size={14} />
          </button>

          <button
            className={styles.iconBtn}
            onClick={handleRotate}
            title="Rotate 90°"
          >
            <RotateCw size={14} />
          </button>
        </div>
      </div>

      {/* Interactive Preview Canvas */}
      <div className={`${styles.canvasArea} ${styles[bgType]}`}>
        {parsedSvg.isValid ? (
          <div 
            className={styles.svgWrapper} 
            style={{ 
              width: `${previewSize}px`, 
              height: `${previewSize}px`,
              color: useCustomColor ? previewColor : 'currentColor',
              ...transformStyle
            }}
            dangerouslySetInnerHTML={{ __html: renderableSvg }}
          />
        ) : (
          <div className={styles.emptyPreview}>
            <span>No valid SVG to preview</span>
          </div>
        )}
      </div>

      {/* Studio Footer Controls */}
      <div className={styles.studioFooter}>
        {/* Size Presets & Slider */}
        <div className={styles.controlRow}>
          <div className={styles.controlLabel}>
            <Maximize2 size={13} />
            <span>Size: <strong>{previewSize}px</strong></span>
          </div>

          <div className={styles.sizePresets}>
            {sizePresets.map(sz => (
              <button
                key={sz}
                className={`${styles.sizePill} ${previewSize === sz ? styles.activeSizePill : ''}`}
                onClick={() => setPreviewSize(sz)}
              >
                {sz}
              </button>
            ))}
          </div>

          <input
            type="range"
            min="12"
            max="256"
            value={previewSize}
            onChange={(e) => setPreviewSize(Number(e.target.value))}
            className={styles.sizeSlider}
          />
        </div>

        {/* Color & Background Row */}
        <div className={styles.controlRow}>
          <div className={styles.colorControls}>
            <div className={styles.controlLabel}>
              <Palette size={13} />
              <span>Color:</span>
            </div>

            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={useCustomColor}
                onChange={(e) => setUseCustomColor(e.target.checked)}
              />
              <span>Override Color</span>
            </label>

            {useCustomColor && (
              <div className={styles.colorPickerWrapper}>
                <input
                  type="color"
                  value={previewColor}
                  onChange={(e) => setPreviewColor(e.target.value)}
                  className={styles.colorInput}
                />
                <span className={styles.colorHex}>{previewColor}</span>
              </div>
            )}
          </div>

          {/* Background Selector */}
          <div className={styles.bgSelector}>
            <span className={styles.bgLabel}>Canvas:</span>
            <button
              className={`${styles.bgBtn} ${styles.bgChecker} ${bgType === 'checkerboard' ? styles.activeBg : ''}`}
              onClick={() => setBgType('checkerboard')}
              title="Checkerboard (Transparent)"
            />
            <button
              className={`${styles.bgBtn} ${styles.bgDark} ${bgType === 'dark' ? styles.activeBg : ''}`}
              onClick={() => setBgType('dark')}
              title="Dark Canvas"
            />
            <button
              className={`${styles.bgBtn} ${styles.bgLight} ${bgType === 'light' ? styles.activeBg : ''}`}
              onClick={() => setBgType('light')}
              title="Light Canvas"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
