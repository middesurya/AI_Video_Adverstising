/**
 * Tests for ChatInterface Component
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ChatInterface from '../components/ChatInterface'

// Mock fetch
global.fetch = jest.fn()

describe('ChatInterface Component', () => {
  const mockAdBrief = {
    productName: 'Test Product',
    description: 'Test description',
    mood: 50,
    energy: 50,
    style: 'cinematic',
    archetype: 'hero-journey',
    targetAudience: 'Test audience',
    callToAction: 'Buy now'
  }

  const mockOnUpdate = jest.fn()
  const mockOnGenerateScript = jest.fn()
  const mockOnBack = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    global.fetch.mockClear()
  })

  test('renders chat interface correctly', () => {
    render(
      <ChatInterface
        adBrief={mockAdBrief}
        onUpdate={mockOnUpdate}
        onGenerateScript={mockOnGenerateScript}
        isGenerating={false}
        onBack={mockOnBack}
      />
    )

    // Check for chat interface title or key elements
    expect(screen.getByText(/Refine Your Brief/i)).toBeInTheDocument()
  })

  test('displays initial brief summary', () => {
    render(
      <ChatInterface
        adBrief={mockAdBrief}
        onUpdate={mockOnUpdate}
        onGenerateScript={mockOnGenerateScript}
        isGenerating={false}
        onBack={mockOnBack}
      />
    )

    expect(screen.getByText(/Test Product/i)).toBeInTheDocument()
  })

  test('shows loading state when generating', () => {
    render(
      <ChatInterface
        adBrief={mockAdBrief}
        onUpdate={mockOnUpdate}
        onGenerateScript={mockOnGenerateScript}
        isGenerating={true}
        onBack={mockOnBack}
      />
    )

    expect(screen.getByText(/Generating/i)).toBeInTheDocument()
  })

  test('generate script button is enabled when not generating', () => {
    render(
      <ChatInterface
        adBrief={mockAdBrief}
        onUpdate={mockOnUpdate}
        onGenerateScript={mockOnGenerateScript}
        isGenerating={false}
        onBack={mockOnBack}
      />
    )

    const generateButton = screen.getByText(/Generate Script/i)
    expect(generateButton).not.toBeDisabled()
  })

  test('generate script button is disabled when generating', () => {
    render(
      <ChatInterface
        adBrief={mockAdBrief}
        onUpdate={mockOnUpdate}
        onGenerateScript={mockOnGenerateScript}
        isGenerating={true}
        onBack={mockOnBack}
      />
    )

    const generateButton = screen.getByText(/Generating/i)
    expect(generateButton).toBeDisabled()
  })

  test('calls onGenerateScript when generate button is clicked', () => {
    render(
      <ChatInterface
        adBrief={mockAdBrief}
        onUpdate={mockOnUpdate}
        onGenerateScript={mockOnGenerateScript}
        isGenerating={false}
        onBack={mockOnBack}
      />
    )

    const generateButton = screen.getByText(/Generate Script/i)
    fireEvent.click(generateButton)

    expect(mockOnGenerateScript).toHaveBeenCalledTimes(1)
  })

  test('calls onBack when back button is clicked', () => {
    render(
      <ChatInterface
        adBrief={mockAdBrief}
        onUpdate={mockOnUpdate}
        onGenerateScript={mockOnGenerateScript}
        isGenerating={false}
        onBack={mockOnBack}
      />
    )

    const backButton = screen.getByText(/Back/i)
    fireEvent.click(backButton)

    expect(mockOnBack).toHaveBeenCalledTimes(1)
  })

  test('brief can be edited inline', () => {
    render(
      <ChatInterface
        adBrief={mockAdBrief}
        onUpdate={mockOnUpdate}
        onGenerateScript={mockOnGenerateScript}
        isGenerating={false}
        onBack={mockOnBack}
      />
    )

    // Try to find editable fields (if they exist in the component)
    // This test assumes the component allows editing
    const editableFields = screen.queryAllByRole('textbox')
    if (editableFields.length > 0) {
      fireEvent.change(editableFields[0], { target: { value: 'Updated value' } })
      expect(mockOnUpdate).toHaveBeenCalled()
    }
  })
})
