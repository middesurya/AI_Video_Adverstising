import { useState } from 'react'
import styles from '../styles/Storyboard.module.css'

export default function Storyboard({ script, scenes, onScenesUpdate, onGenerateVideo, isGenerating, onBack }) {
  const [editingScene, setEditingScene] = useState(null)

  const handleSceneEdit = (index, field, value) => {
    const updated = [...scenes]
    updated[index] = { ...updated[index], [field]: value }
    onScenesUpdate(updated)
  }

  return (
    <div className={styles.container} data-testid="storyboard">
      <div className={styles.header}>
        <button className={styles.backButton} onClick={onBack}>← Back</button>
        <h2>Your Storyboard</h2>
        <span className={styles.scenesCount}>{scenes.length} scenes • ~60 seconds</span>
      </div>

      <div className={styles.scriptSection}>
        <h3>📜 Generated Script</h3>
        <div className={styles.scriptText} data-testid="script-text">
          {script}
        </div>
      </div>

      <div className={styles.scenesSection}>
        <h3>🎬 Scene Breakdown</h3>
        <div className={styles.scenesGrid}>
          {scenes.map((scene, idx) => (
            <div 
              key={idx} 
              className={styles.sceneCard}
              data-testid={`scene-${idx}`}
            >
              <div className={styles.sceneHeader}>
                <span className={styles.sceneNumber}>Scene {idx + 1}</span>
                <span className={styles.sceneDuration}>{scene.duration}s</span>
              </div>
              
              <div className={styles.scenePreview}>
                <div className={styles.previewPlaceholder}>
                  {scene.visualEmoji || '🎬'}
                </div>
              </div>

              {editingScene === idx ? (
                <div className={styles.editForm}>
                  <textarea
                    value={scene.description}
                    onChange={(e) => handleSceneEdit(idx, 'description', e.target.value)}
                    rows={3}
                    data-testid={`scene-${idx}-edit`}
                  />
                  <input
                    type="text"
                    value={scene.narration || ''}
                    onChange={(e) => handleSceneEdit(idx, 'narration', e.target.value)}
                    placeholder="Voiceover text..."
                  />
                  <button onClick={() => setEditingScene(null)}>Done</button>
                </div>
              ) : (
                <>
                  <p className={styles.sceneDescription}>{scene.description}</p>
                  {scene.narration && (
                    <p className={styles.sceneNarration}>
                      <span>🎙️</span> "{scene.narration}"
                    </p>
                  )}
                  <div className={styles.sceneTags}>
                    {scene.tags?.map((tag, i) => (
                      <span key={i} className={styles.tag}>{tag}</span>
                    ))}
                  </div>
                  <button 
                    className={styles.editButton}
                    onClick={() => setEditingScene(idx)}
                  >
                    ✏️ Edit
                  </button>
                </>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className={styles.generateSection}>
        <button
          className={styles.generateButton}
          onClick={onGenerateVideo}
          disabled={isGenerating}
          data-testid="generate-video-button"
        >
          {isGenerating ? (
            <>
              <span className={styles.spinner}></span>
              Generating Video...
            </>
          ) : (
            '🎬 Generate Video'
          )}
        </button>
        <p className={styles.generateHint}>
          This will create video clips for each scene and assemble them into your final ad
        </p>
      </div>
    </div>
  )
}

