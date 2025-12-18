import { useState } from 'react'
import styles from '../styles/PromptRefinement.module.css'

const STYLES = [
  { id: 'cinematic', label: '🎬 Cinematic', desc: 'Epic, movie-like visuals' },
  { id: 'minimalist', label: '✨ Minimalist', desc: 'Clean, simple aesthetics' },
  { id: 'energetic', label: '⚡ Energetic', desc: 'Fast-paced, dynamic' },
  { id: 'warm', label: '🌅 Warm', desc: 'Cozy, inviting feel' },
  { id: 'professional', label: '💼 Professional', desc: 'Corporate, polished' },
  { id: 'playful', label: '🎮 Playful', desc: 'Fun, whimsical style' }
]

const ARCHETYPES = [
  { id: 'hero-journey', label: 'Hero\'s Journey', desc: 'Overcome challenges, achieve greatness' },
  { id: 'testimonial', label: 'Testimonial', desc: 'Real stories, authentic voices' },
  { id: 'problem-solution', label: 'Problem-Solution', desc: 'Show the pain, reveal the cure' },
  { id: 'tutorial', label: 'Tutorial', desc: 'Step-by-step demonstration' },
  { id: 'comedy', label: 'Comedy Skit', desc: 'Humor that sticks' },
  { id: 'lifestyle', label: 'Lifestyle', desc: 'Aspirational, emotional connection' }
]

export default function PromptRefinement({ adBrief, onUpdate, onNext }) {
  const isValid = adBrief.productName && adBrief.description

  return (
    <div className={styles.container} data-testid="prompt-refinement">
      <div className={styles.hero}>
        <h2>Create Your Ad Vision</h2>
        <p>Tell us about your product and we'll craft a compelling video ad</p>
      </div>

      <div className={styles.form}>
        <div className={styles.section}>
          <h3>📦 Product Details</h3>
          <div className={styles.inputGroup}>
            <label htmlFor="productName">Product Name</label>
            <input
              id="productName"
              type="text"
              value={adBrief.productName}
              onChange={(e) => onUpdate({ productName: e.target.value })}
              placeholder="e.g., FitTrack Pro"
              data-testid="product-name-input"
            />
          </div>
          <div className={styles.inputGroup}>
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              value={adBrief.description}
              onChange={(e) => onUpdate({ description: e.target.value })}
              placeholder="Describe your product and what makes it special..."
              rows={4}
              data-testid="description-input"
            />
          </div>
        </div>

        <div className={styles.section}>
          <h3>🎨 Visual Style</h3>
          <div className={styles.styleGrid}>
            {STYLES.map(style => (
              <button
                key={style.id}
                className={`${styles.styleCard} ${adBrief.style === style.id ? styles.selected : ''}`}
                onClick={() => onUpdate({ style: style.id })}
                data-testid={`style-${style.id}`}
              >
                <span className={styles.styleLabel}>{style.label}</span>
                <span className={styles.styleDesc}>{style.desc}</span>
              </button>
            ))}
          </div>
        </div>

        <div className={styles.section}>
          <h3>🎭 Story Archetype</h3>
          <div className={styles.archetypeGrid}>
            {ARCHETYPES.map(arch => (
              <button
                key={arch.id}
                className={`${styles.archetypeCard} ${adBrief.archetype === arch.id ? styles.selected : ''}`}
                onClick={() => onUpdate({ archetype: arch.id })}
                data-testid={`archetype-${arch.id}`}
              >
                <span className={styles.archetypeLabel}>{arch.label}</span>
                <span className={styles.archetypeDesc}>{arch.desc}</span>
              </button>
            ))}
          </div>
        </div>

        <div className={styles.section}>
          <h3>🎚️ Mood & Energy</h3>
          <div className={styles.sliderGroup}>
            <div className={styles.slider}>
              <label>
                <span>Mood</span>
                <span className={styles.sliderValue}>
                  {adBrief.mood < 30 ? '😌 Calm' : adBrief.mood > 70 ? '🎉 Exciting' : '😊 Balanced'}
                </span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={adBrief.mood}
                onChange={(e) => onUpdate({ mood: parseInt(e.target.value) })}
                data-testid="mood-slider"
              />
              <div className={styles.sliderLabels}>
                <span>Calm</span>
                <span>Exciting</span>
              </div>
            </div>
            <div className={styles.slider}>
              <label>
                <span>Energy</span>
                <span className={styles.sliderValue}>
                  {adBrief.energy < 30 ? '🐢 Slow' : adBrief.energy > 70 ? '🚀 Fast' : '⚖️ Medium'}
                </span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={adBrief.energy}
                onChange={(e) => onUpdate({ energy: parseInt(e.target.value) })}
                data-testid="energy-slider"
              />
              <div className={styles.sliderLabels}>
                <span>Slow-paced</span>
                <span>Fast-paced</span>
              </div>
            </div>
          </div>
        </div>

        <button
          className={styles.nextButton}
          onClick={onNext}
          disabled={!isValid}
          data-testid="next-button"
        >
          Continue to Refinement →
        </button>
      </div>
    </div>
  )
}

