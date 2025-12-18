import { useState, useEffect } from 'react'
import Head from 'next/head'
import PromptRefinement from '../components/PromptRefinement'
import ChatInterface from '../components/ChatInterface'
import Storyboard from '../components/Storyboard'
import VideoPreview from '../components/VideoPreview'
import styles from '../styles/Home.module.css'

export default function Home() {
  console.log('[DEBUG] Component rendered - VERSION 2.0', new Date().toISOString())
  const [step, setStep] = useState(1)
  const [adBrief, setAdBrief] = useState({
    productName: '',
    description: '',
    mood: 50,
    energy: 50,
    style: 'cinematic',
    archetype: 'hero-journey',
    targetAudience: '',
    callToAction: ''
  })
  const [script, setScript] = useState(null)
  const [scenes, setScenes] = useState([])
  const [videoUrl, setVideoUrl] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState(null)
  
  // Debug: Track state changes
  useEffect(() => {
    console.log('[DEBUG] State changed:', { step, isGenerating, hasVideoUrl: !!videoUrl, error })
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/e3859fe4-0bdc-4abf-acd7-fbb84c182406',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'index.js:26',message:'State changed',data:{step,isGenerating,hasVideoUrl:!!videoUrl,hasError:!!error},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'1'})}).catch(()=>{});
    // #endregion
  }, [step, isGenerating, videoUrl, error])
  
  // Safety: Force reset if isGenerating is stuck for too long
  useEffect(() => {
    if (isGenerating) {
      const safetyTimeout = setTimeout(() => {
        console.warn('[DEBUG] SAFETY: isGenerating stuck for 15 seconds, forcing reset')
        setIsGenerating(false)
        setError('Request timed out. Please try again.')
      }, 15000)
      return () => clearTimeout(safetyTimeout)
    }
  }, [isGenerating])

  const handleBriefUpdate = (updates) => {
    setAdBrief(prev => ({ ...prev, ...updates }))
  }

  const handleGenerateScript = async () => {
    setIsGenerating(true)
    setError(null)
    
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 second timeout
      
      const response = await fetch('http://localhost:8002/api/generate-script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(adBrief),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Server error: ${response.status} ${response.statusText}. ${errorText}`)
      }
      
      const data = await response.json()
      
      if (data.success) {
        setScript(data.script)
        setScenes(data.scenes)
        setStep(3)
      } else {
        setError(data.error || 'Failed to generate script')
        setIsGenerating(false)
      }
    } catch (err) {
      console.error('Script generation error:', err)
      if (err.name === 'AbortError') {
        setError('Request timed out. Please check if the backend server is running on port 8002.')
      } else {
        setError(err.message || 'Failed to connect to server. Make sure the backend is running on port 8002.')
      }
      setIsGenerating(false)
    }
  }

  const handleGenerateVideo = async () => {
    console.log('[DEBUG] handleGenerateVideo called', { scenesCount: scenes?.length, hasAdBrief: !!adBrief })
    
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/e3859fe4-0bdc-4abf-acd7-fbb84c182406',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'index.js:70',message:'handleGenerateVideo ENTRY',data:{scenesCount:scenes?.length,hasScenes:!!scenes,hasAdBrief:!!adBrief,productName:adBrief?.productName},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'1'})}).catch(()=>{});
    // #endregion
    
    // Validate inputs before starting
    if (!scenes || scenes.length === 0) {
      console.error('[DEBUG] Validation failed: No scenes')
      setError('No scenes available. Please generate a script first.')
      return
    }
    if (!adBrief || !adBrief.productName) {
      console.error('[DEBUG] Validation failed: No adBrief')
      setError('Ad brief is missing. Please fill in the product details.')
      return
    }
    
    setIsGenerating(true)
    setError(null)
    
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/e3859fe4-0bdc-4abf-acd7-fbb84c182406',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'index.js:85',message:'Validation passed, starting request',data:{scenesCount:scenes.length,productName:adBrief.productName},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'1'})}).catch(()=>{});
    // #endregion
    
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => {
        console.log('[DEBUG] Timeout triggered after 10 seconds')
        // #region agent log
        fetch('http://127.0.0.1:7243/ingest/e3859fe4-0bdc-4abf-acd7-fbb84c182406',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'index.js:92',message:'Timeout triggered',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'2'})}).catch(()=>{});
        // #endregion
        controller.abort()
      }, 10000) // 10 second timeout
      
      // #region agent log
      fetch('http://127.0.0.1:7243/ingest/e3859fe4-0bdc-4abf-acd7-fbb84c182406',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'index.js:98',message:'About to call fetch',data:{url:'http://localhost:8002/api/generate-video',bodyLength:JSON.stringify({scenes,adBrief}).length},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'3'})}).catch(()=>{});
      // #endregion
      
      const fetchStartTime = Date.now()
      const response = await fetch('http://localhost:8002/api/generate-video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenes, adBrief }),
        signal: controller.signal
      })
      
      const fetchDuration = Date.now() - fetchStartTime
      console.log('[DEBUG] Fetch completed', { status: response.status, duration: fetchDuration })
      
      // #region agent log
      fetch('http://127.0.0.1:7243/ingest/e3859fe4-0bdc-4abf-acd7-fbb84c182406',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'index.js:110',message:'Fetch completed',data:{status:response.status,ok:response.ok,duration:fetchDuration},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'1'})}).catch(()=>{});
      // #endregion
      
      clearTimeout(timeoutId)
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Server error: ${response.status} ${response.statusText}. ${errorText}`)
      }
      
      const data = await response.json()
      console.log('[DEBUG] Response parsed', { success: data.success, hasVideoUrl: !!data.videoUrl })
      
      // #region agent log
      fetch('http://127.0.0.1:7243/ingest/e3859fe4-0bdc-4abf-acd7-fbb84c182406',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'index.js:137',message:'Response parsed',data:{success:data.success,hasVideoUrl:!!data.videoUrl},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'1'})}).catch(()=>{});
      // #endregion
      
      if (data.success) {
        console.log('[DEBUG] Setting video URL and updating state', { videoUrl: data.videoUrl })
        // #region agent log
        fetch('http://127.0.0.1:7243/ingest/e3859fe4-0bdc-4abf-acd7-fbb84c182406',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'index.js:144',message:'About to update state',data:{videoUrl:data.videoUrl},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'1'})}).catch(()=>{});
        // #endregion
        setVideoUrl(data.videoUrl)
        setIsGenerating(false)  // Reset loading state on success
        console.log('[DEBUG] State updated, setting step to 4')
        setStep(4)
        // #region agent log
        fetch('http://127.0.0.1:7243/ingest/e3859fe4-0bdc-4abf-acd7-fbb84c182406',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'index.js:150',message:'State update complete',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'1'})}).catch(()=>{});
        // #endregion
      } else {
        console.log('[DEBUG] Response not successful', { error: data.error })
        setError(data.error || 'Failed to generate video')
        setIsGenerating(false)
      }
    } catch (err) {
      console.error('[DEBUG] Video generation error:', err)
      // #region agent log
      fetch('http://127.0.0.1:7243/ingest/e3859fe4-0bdc-4abf-acd7-fbb84c182406',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'index.js:135',message:'Exception caught',data:{name:err.name,message:err.message,isAbort:err.name==='AbortError'},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'2'})}).catch(()=>{});
      // #endregion
      
      if (err.name === 'AbortError') {
        setError('Request timed out. Please check if the backend server is running on port 8002.')
      } else {
        setError(err.message || 'Failed to connect to server. Make sure the backend is running on port 8002.')
      }
      setIsGenerating(false)
    }
  }

  return (
    <>
      <Head>
        <title>AI Ad Video Generator</title>
        <meta name="description" content="Create stunning video ads with AI" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </Head>

      <main className={styles.main}>
        <header className={styles.header}>
          <div className={styles.logo}>
            <span className={styles.logoIcon}>🎬</span>
            <h1>AdVision AI</h1>
          </div>
          <nav className={styles.nav}>
            <span className={step >= 1 ? styles.active : ''}>1. Brief</span>
            <span className={step >= 2 ? styles.active : ''}>2. Refine</span>
            <span className={step >= 3 ? styles.active : ''}>3. Storyboard</span>
            <span className={step >= 4 ? styles.active : ''}>4. Video</span>
          </nav>
        </header>

        <div className={styles.content}>
          {error && (
            <div className={styles.error} data-testid="error-message">
              {error}
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}

          {step === 1 && (
            <PromptRefinement
              adBrief={adBrief}
              onUpdate={handleBriefUpdate}
              onNext={() => setStep(2)}
            />
          )}

          {step === 2 && (
            <ChatInterface
              adBrief={adBrief}
              onUpdate={handleBriefUpdate}
              onGenerateScript={handleGenerateScript}
              isGenerating={isGenerating}
              onBack={() => setStep(1)}
            />
          )}

          {step === 3 && (
            <Storyboard
              script={script}
              scenes={scenes}
              onScenesUpdate={setScenes}
              onGenerateVideo={handleGenerateVideo}
              isGenerating={isGenerating}
              onBack={() => setStep(2)}
            />
          )}

          {step === 4 && (
            <VideoPreview
              videoUrl={videoUrl}
              adBrief={adBrief}
              onBack={() => setStep(3)}
              onStartOver={() => {
                setStep(1)
                setScript(null)
                setScenes([])
                setVideoUrl(null)
              }}
            />
          )}
        </div>
      </main>
    </>
  )
}
