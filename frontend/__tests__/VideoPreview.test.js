/**
 * QA Tests for VideoPreview Component
 */

import { render, screen, fireEvent } from '@testing-library/react'
import VideoPreview from '../components/VideoPreview'

describe('VideoPreview Component', () => {
  const mockOnBack = jest.fn()
  const mockOnStartOver = jest.fn()
  
  const defaultProps = {
    videoUrl: '/videos/test-ad.mp4',
    adBrief: {
      productName: 'TestProduct',
      description: 'A test product'
    },
    onBack: mockOnBack,
    onStartOver: mockOnStartOver
  }

  beforeEach(() => {
    jest.clearAllMocks()
    // Mock alert
    window.alert = jest.fn()
  })

  test('renders the video preview component', () => {
    render(<VideoPreview {...defaultProps} />)
    expect(screen.getByTestId('video-preview')).toBeInTheDocument()
  })

  test('displays success message', () => {
    render(<VideoPreview {...defaultProps} />)
    expect(screen.getByText(/Your Video Ad is Ready/i)).toBeInTheDocument()
  })

  test('renders video player', () => {
    render(<VideoPreview {...defaultProps} />)
    expect(screen.getByTestId('video-player')).toBeInTheDocument()
  })

  test('displays product name in video preview', () => {
    render(<VideoPreview {...defaultProps} />)
    expect(screen.getByText('TestProduct')).toBeInTheDocument()
  })

  test('renders engagement metrics section', () => {
    render(<VideoPreview {...defaultProps} />)
    expect(screen.getByText('📊 Engagement Metrics')).toBeInTheDocument()
    expect(screen.getByText('Hook Score')).toBeInTheDocument()
  })

  test('renders format selection options', () => {
    render(<VideoPreview {...defaultProps} />)
    expect(screen.getByTestId('format-vertical')).toBeInTheDocument()
    expect(screen.getByTestId('format-square')).toBeInTheDocument()
    expect(screen.getByTestId('format-horizontal')).toBeInTheDocument()
  })

  test('vertical format is selected by default', () => {
    render(<VideoPreview {...defaultProps} />)
    const verticalButton = screen.getByTestId('format-vertical')
    expect(verticalButton).toHaveClass('selected')
  })

  test('can select different format', () => {
    render(<VideoPreview {...defaultProps} />)
    const squareButton = screen.getByTestId('format-square')
    fireEvent.click(squareButton)
    expect(squareButton).toHaveClass('selected')
  })

  test('renders download button', () => {
    render(<VideoPreview {...defaultProps} />)
    expect(screen.getByTestId('download-button')).toBeInTheDocument()
  })

  test('download button triggers alert', () => {
    render(<VideoPreview {...defaultProps} />)
    fireEvent.click(screen.getByTestId('download-button'))
    expect(window.alert).toHaveBeenCalled()
  })

  test('renders start over button', () => {
    render(<VideoPreview {...defaultProps} />)
    expect(screen.getByTestId('start-over-button')).toBeInTheDocument()
  })

  test('start over button calls onStartOver', () => {
    render(<VideoPreview {...defaultProps} />)
    fireEvent.click(screen.getByTestId('start-over-button'))
    expect(mockOnStartOver).toHaveBeenCalled()
  })

  test('back button calls onBack', () => {
    render(<VideoPreview {...defaultProps} />)
    fireEvent.click(screen.getByText('← Back'))
    expect(mockOnBack).toHaveBeenCalled()
  })

  test('displays tips section', () => {
    render(<VideoPreview {...defaultProps} />)
    expect(screen.getByText('💡 Tips to Improve')).toBeInTheDocument()
  })

  test('displays platform information for formats', () => {
    render(<VideoPreview {...defaultProps} />)
    expect(screen.getByText('TikTok, Reels, Shorts')).toBeInTheDocument()
    expect(screen.getByText('Instagram Feed')).toBeInTheDocument()
    expect(screen.getByText('YouTube, Facebook')).toBeInTheDocument()
  })
})

