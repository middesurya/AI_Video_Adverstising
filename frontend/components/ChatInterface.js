import { useState, useEffect, useRef } from 'react'
import styles from '../styles/ChatInterface.module.css'

const CLARIFYING_QUESTIONS = [
  "Who is your target audience? (age, interests, demographics)",
  "What's the main problem your product solves?",
  "What emotion do you want viewers to feel?",
  "What's your call-to-action? (Buy now, Sign up, Learn more)",
  "Any specific visual elements you want to include?"
]

export default function ChatInterface({ adBrief, onUpdate, onGenerateScript, isGenerating, onBack }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    // Initial greeting
    const greeting = {
      role: 'assistant',
      content: `Great! Let me help you refine your ad for "${adBrief.productName}". I have a few questions to make your video perfect.`
    }
    setMessages([greeting])
    
    // First question after delay
    setTimeout(() => {
      askQuestion(0)
    }, 1000)
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const askQuestion = (index) => {
    if (index < CLARIFYING_QUESTIONS.length) {
      setIsTyping(true)
      setTimeout(() => {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: CLARIFYING_QUESTIONS[index]
        }])
        setIsTyping(false)
        setCurrentQuestion(index)
      }, 800)
    }
  }

  const handleSend = () => {
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    
    // Update brief based on question
    const questionIndex = currentQuestion
    if (questionIndex === 0) {
      onUpdate({ targetAudience: input })
    } else if (questionIndex === 3) {
      onUpdate({ callToAction: input })
    }

    setInput('')

    // Ask next question or finish
    if (currentQuestion < CLARIFYING_QUESTIONS.length - 1) {
      setTimeout(() => askQuestion(currentQuestion + 1), 500)
    } else {
      setIsTyping(true)
      setTimeout(() => {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: "Perfect! I have all the details I need. Ready to generate your script?"
        }])
        setIsTyping(false)
      }, 800)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const allQuestionsAnswered = currentQuestion >= CLARIFYING_QUESTIONS.length - 1 && 
    messages.filter(m => m.role === 'user').length >= CLARIFYING_QUESTIONS.length

  return (
    <div className={styles.container} data-testid="chat-interface">
      <div className={styles.header}>
        <button className={styles.backButton} onClick={onBack}>← Back</button>
        <h2>Refine Your Ad</h2>
        <div className={styles.briefPreview}>
          <span>📦 {adBrief.productName}</span>
          <span>🎨 {adBrief.style}</span>
          <span>🎭 {adBrief.archetype}</span>
        </div>
      </div>

      <div className={styles.chatArea}>
        <div className={styles.messages}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`${styles.message} ${msg.role === 'user' ? styles.user : styles.assistant}`}
              data-testid={`message-${msg.role}`}
            >
              {msg.role === 'assistant' && <span className={styles.avatar}>🤖</span>}
              <div className={styles.content}>{msg.content}</div>
              {msg.role === 'user' && <span className={styles.avatar}>👤</span>}
            </div>
          ))}
          {isTyping && (
            <div className={`${styles.message} ${styles.assistant}`}>
              <span className={styles.avatar}>🤖</span>
              <div className={styles.typing}>
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className={styles.inputArea}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your answer..."
            rows={2}
            disabled={isGenerating}
            data-testid="chat-input"
          />
          <button 
            onClick={handleSend} 
            disabled={!input.trim() || isGenerating}
            data-testid="send-button"
          >
            Send
          </button>
        </div>
      </div>

      {allQuestionsAnswered && (
        <div className={styles.generateSection}>
          <button
            className={styles.generateButton}
            onClick={onGenerateScript}
            disabled={isGenerating}
            data-testid="generate-script-button"
          >
            {isGenerating ? (
              <>
                <span className={styles.spinner}></span>
                Generating Script...
              </>
            ) : (
              '✨ Generate Script'
            )}
          </button>
        </div>
      )}
    </div>
  )
}

