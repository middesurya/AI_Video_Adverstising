import { useState } from 'react'
import styles from '../styles/VideoPreview.module.css'

export default function VideoPreview({ videoUrl, adBrief, onBack, onStartOver }) {
  const [selectedFormat, setSelectedFormat] = useState('vertical')
  const [hookScore] = useState(Math.floor(Math.random() * 30) + 70) // Mock score 70-100

  const getHookLabel = (score) => {
    if (score >= 85) return { label: 'Excellent', color: '#4ade80', emoji: '🔥' }
    if (score >= 70) return { label: 'Good', color: '#fbbf24', emoji: '👍' }
    return { label: 'Needs Work', color: '#f87171', emoji: '💡' }
  }

  const hookInfo = getHookLabel(hookScore)

  const formats = [
    { id: 'vertical', label: '9:16 Vertical', desc: 'TikTok, Reels, Shorts', icon: '📱' },
    { id: 'square', label: '1:1 Square', desc: 'Instagram Feed', icon: '⬜' },
    { id: 'horizontal', label: '16:9 Horizontal', desc: 'YouTube, Facebook', icon: '🖥️' }
  ]

  const handleDownload = () => {
    // Mock download - in real app would trigger actual download
    alert(`Downloading ${selectedFormat} format video...`)
  }

  return (
    <div className={styles.container} data-testid="video-preview">
      <div className={styles.header}>
        <button className={styles.backButton} onClick={onBack}>← Back</button>
        <h2>Your Video Ad is Ready! 🎉</h2>
      </div>

      <div className={styles.content}>
        <div className={styles.videoSection}>
          <div className={styles.videoPlayer} data-testid="video-player">
            <div className={styles.videoPlaceholder}>
              <div className={styles.playButton}>▶</div>
              <p>Video Preview</p>
              <span>{adBrief.productName}</span>
            </div>
          </div>

          <div className={styles.videoControls}>
            <button className={styles.playBtn}>▶ Play</button>
            <div className={styles.timeline}>
              <div className={styles.progress} style={{ width: '0%' }}></div>
            </div>
            <span className={styles.duration}>0:00 / 1:00</span>
          </div>
        </div>

        <div className={styles.sidebar}>
          <div className={styles.metricsCard}>
            <h3>📊 Engagement Metrics</h3>
            
            <div className={styles.metric}>
              <div className={styles.metricHeader}>
                <span>Hook Score</span>
                <span className={styles.metricValue} style={{ color: hookInfo.color }}>
                  {hookInfo.emoji} {hookScore}%
                </span>
              </div>
              <div className={styles.progressBar}>
                <div 
                  className={styles.progressFill} 
                  style={{ width: `${hookScore}%`, background: hookInfo.color }}
                ></div>
              </div>
              <p className={styles.metricDesc}>
                {hookScore >= 85 
                  ? "Great hook! Your opening will capture attention." 
                  : "Consider adding a stronger visual or text in the first 3 seconds."}
              </p>
            </div>

            <div className={styles.tips}>
              <h4>💡 Tips to Improve</h4>
              <ul>
                <li>Show your product within first 2 seconds</li>
                <li>Add captions for silent viewing</li>
                <li>Include a clear call-to-action</li>
              </ul>
            </div>
          </div>

          <div className={styles.formatCard}>
            <h3>📐 Export Format</h3>
            <div className={styles.formatOptions}>
              {formats.map(format => (
                <button
                  key={format.id}
                  className={`${styles.formatOption} ${selectedFormat === format.id ? styles.selected : ''}`}
                  onClick={() => setSelectedFormat(format.id)}
                  data-testid={`format-${format.id}`}
                >
                  <span className={styles.formatIcon}>{format.icon}</span>
                  <span className={styles.formatLabel}>{format.label}</span>
                  <span className={styles.formatDesc}>{format.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <div className={styles.actions}>
            <button 
              className={styles.downloadBtn} 
              onClick={handleDownload}
              data-testid="download-button"
            >
              ⬇️ Download Video
            </button>
            <button 
              className={styles.startOverBtn} 
              onClick={onStartOver}
              data-testid="start-over-button"
            >
              🔄 Create Another Ad
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

