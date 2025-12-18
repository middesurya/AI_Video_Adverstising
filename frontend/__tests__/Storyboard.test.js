/**
 * QA Tests for Storyboard Component
 */

import { render, screen, fireEvent } from '@testing-library/react'
import Storyboard from '../components/Storyboard'

describe('Storyboard Component', () => {
  const mockOnScenesUpdate = jest.fn()
  const mockOnGenerateVideo = jest.fn()
  const mockOnBack = jest.fn()
  
  const defaultProps = {
    script: 'This is a test script for the ad.',
    scenes: [
      {
        description: 'Opening hook scene',
        duration: 10,
        narration: 'Welcome to our product',
        visualEmoji: '✨',
        tags: ['hook', 'intro']
      },
      {
        description: 'Product showcase',
        duration: 15,
        narration: 'Here is what we offer',
        visualEmoji: '💡',
        tags: ['product', 'features']
      },
      {
        description: 'Call to action',
        duration: 10,
        narration: 'Get it now!',
        visualEmoji: '🎯',
        tags: ['cta']
      }
    ],
    onScenesUpdate: mockOnScenesUpdate,
    onGenerateVideo: mockOnGenerateVideo,
    isGenerating: false,
    onBack: mockOnBack
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders the storyboard component', () => {
    render(<Storyboard {...defaultProps} />)
    expect(screen.getByTestId('storyboard')).toBeInTheDocument()
  })

  test('displays the header', () => {
    render(<Storyboard {...defaultProps} />)
    expect(screen.getByText('Your Storyboard')).toBeInTheDocument()
  })

  test('displays the script text', () => {
    render(<Storyboard {...defaultProps} />)
    expect(screen.getByTestId('script-text')).toBeInTheDocument()
    expect(screen.getByText('This is a test script for the ad.')).toBeInTheDocument()
  })

  test('renders all scenes', () => {
    render(<Storyboard {...defaultProps} />)
    expect(screen.getByTestId('scene-0')).toBeInTheDocument()
    expect(screen.getByTestId('scene-1')).toBeInTheDocument()
    expect(screen.getByTestId('scene-2')).toBeInTheDocument()
  })

  test('displays scene numbers correctly', () => {
    render(<Storyboard {...defaultProps} />)
    expect(screen.getByText('Scene 1')).toBeInTheDocument()
    expect(screen.getByText('Scene 2')).toBeInTheDocument()
    expect(screen.getByText('Scene 3')).toBeInTheDocument()
  })

  test('displays scene durations', () => {
    render(<Storyboard {...defaultProps} />)
    // Multiple scenes can have the same duration, use getAllByText
    const tenSecondScenes = screen.getAllByText('10s')
    expect(tenSecondScenes.length).toBeGreaterThan(0)
    expect(screen.getByText('15s')).toBeInTheDocument()
  })

  test('displays scene descriptions', () => {
    render(<Storyboard {...defaultProps} />)
    expect(screen.getByText('Opening hook scene')).toBeInTheDocument()
    expect(screen.getByText('Product showcase')).toBeInTheDocument()
    expect(screen.getByText('Call to action')).toBeInTheDocument()
  })

  test('displays scene count', () => {
    render(<Storyboard {...defaultProps} />)
    expect(screen.getByText(/3 scenes/)).toBeInTheDocument()
  })

  test('renders generate video button', () => {
    render(<Storyboard {...defaultProps} />)
    expect(screen.getByTestId('generate-video-button')).toBeInTheDocument()
  })

  test('generate video button calls onGenerateVideo', () => {
    render(<Storyboard {...defaultProps} />)
    fireEvent.click(screen.getByTestId('generate-video-button'))
    expect(mockOnGenerateVideo).toHaveBeenCalled()
  })

  test('generate video button is disabled when generating', () => {
    render(<Storyboard {...defaultProps} isGenerating={true} />)
    expect(screen.getByTestId('generate-video-button')).toBeDisabled()
  })

  test('shows generating text when isGenerating is true', () => {
    render(<Storyboard {...defaultProps} isGenerating={true} />)
    expect(screen.getByText(/Generating Video/)).toBeInTheDocument()
  })

  test('back button calls onBack', () => {
    render(<Storyboard {...defaultProps} />)
    fireEvent.click(screen.getByText('← Back'))
    expect(mockOnBack).toHaveBeenCalled()
  })

  test('displays visual emojis for scenes', () => {
    render(<Storyboard {...defaultProps} />)
    expect(screen.getByText('✨')).toBeInTheDocument()
    expect(screen.getByText('💡')).toBeInTheDocument()
    expect(screen.getByText('🎯')).toBeInTheDocument()
  })
})

