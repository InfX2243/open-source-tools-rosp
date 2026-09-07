import React, { useState } from 'react';
import styles from './CostMatrix.module.css';
import { DollarSign, Check, Zap } from 'lucide-react';
import { LLM_MODELS, calculateCost } from '../core/models';

export function CostMatrix({
  inputTokens,
  outputTokens,
  selectedModelId,
  onSelectModel
}) {
  const [requestVolume, setRequestVolume] = useState(1000);

  const volumes = [
    { label: '1 Call', value: 1 },
    { label: '1,000 (1K)', value: 1000 },
    { label: '10,000 (10K)', value: 10000 },
    { label: '1 Million', value: 1000000 }
  ];

  const modelCosts = LLM_MODELS.map(model => {
    const cost = calculateCost(model, inputTokens, outputTokens, requestVolume);
    return {
      ...model,
      ...cost
    };
  }).sort((a, b) => a.totalCost - b.totalCost);

  const formatCurrency = (amount) => {
    if (amount < 0.0001) return `$${amount.toFixed(6)}`;
    if (amount < 0.01) return `$${amount.toFixed(4)}`;
    return `$${amount.toFixed(2)}`;
  };

  return (
    <div className={styles.matrixContainer}>
      {/* Header with Volume Toggle */}
      <div className={styles.matrixHeader}>
        <div className={styles.headerTitle}>
          <DollarSign size={16} className={styles.titleIcon} />
          <span>Estimated API Cost Comparison</span>
        </div>

        <div className={styles.volumePills}>
          {volumes.map(vol => (
            <button
              key={vol.value}
              className={`${styles.volBtn} ${requestVolume === vol.value ? styles.activeVolBtn : ''}`}
              onClick={() => setRequestVolume(vol.value)}
            >
              {vol.label}
            </button>
          ))}
        </div>
      </div>

      {/* Clean Model List */}
      <div className={styles.modelList}>
        {modelCosts.map(model => {
          const isSelected = selectedModelId === model.id;

          return (
            <div
              key={model.id}
              className={`${styles.modelItem} ${isSelected ? styles.selectedItem : ''}`}
              onClick={() => onSelectModel(model.id)}
            >
              <div className={styles.modelLeft}>
                <div className={styles.modelNameRow}>
                  <strong className={styles.modelName}>{model.name}</strong>
                  <span className={`${styles.providerBadge} ${styles[model.badgeClass]}`}>
                    {model.provider}
                  </span>
                </div>
                <div className={styles.rateSubtext}>
                  <span>In: ${model.inputPricePer1M}/1M</span>
                  <span>•</span>
                  <span>Out: ${model.outputPricePer1M}/1M</span>
                </div>
              </div>

              <div className={styles.modelRight}>
                <div className={styles.costBadge}>
                  {formatCurrency(model.totalCost)}
                </div>
                {isSelected && <Check size={16} className={styles.checkIcon} />}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
