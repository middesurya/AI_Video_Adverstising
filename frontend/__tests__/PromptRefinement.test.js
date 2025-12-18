/**
 * QA Tests for PromptRefinement Component
 */

import { render, screen, fireEvent } from '@testing-library/react'
import PromptRefinement from '../components/PromptRefinement'

describe('PromptRefinement Component', () => {
  const mockOnUpdate = jest.fn()
  const mockOnNext = jest.fn()
  
  const defaultBrief = {
    productName: '',
    description: '',
    mood: 50,
    energy: 50,
    style: 'cinematic',
    archetype: 'hero-journey',
    targetAudience: '',
    callToAction: ''
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders the prompt refinement form', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    expect(screen.getByTestId('prompt-refinement')).toBeInTheDocument()
    expect(screen.getByText('Create Your Ad Vision')).toBeInTheDocument()
  })

  test('renders product name input', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    const input = screen.getByTestId('product-name-input')
    expect(input).toBeInTheDocument()
    expect(input).toHaveAttribute('placeholder', 'e.g., FitTrack Pro')
  })

  test('renders description textarea', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    const textarea = screen.getByTestId('description-input')
    expect(textarea).toBeInTheDocument()
  })

  test('updates product name on input change', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    const input = screen.getByTestId('product-name-input')
    fireEvent.change(input, { target: { value: 'My Product' } })

    expect(mockOnUpdate).toHaveBeenCalledWith({ productName: 'My Product' })
  })

  test('updates description on textarea change', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    const textarea = screen.getByTestId('description-input')
    fireEvent.change(textarea, { target: { value: 'A great product' } })

    expect(mockOnUpdate).toHaveBeenCalledWith({ description: 'A great product' })
  })

  test('renders all style options', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    expect(screen.getByTestId('style-cinematic')).toBeInTheDocument()
    expect(screen.getByTestId('style-minimalist')).toBeInTheDocument()
    expect(screen.getByTestId('style-energetic')).toBeInTheDocument()
    expect(screen.getByTestId('style-warm')).toBeInTheDocument()
    expect(screen.getByTestId('style-professional')).toBeInTheDocument()
    expect(screen.getByTestId('style-playful')).toBeInTheDocument()
  })

  test('updates style on selection', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    fireEvent.click(screen.getByTestId('style-minimalist'))
    expect(mockOnUpdate).toHaveBeenCalledWith({ style: 'minimalist' })
  })

  test('renders all archetype options', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    expect(screen.getByTestId('archetype-hero-journey')).toBeInTheDocument()
    expect(screen.getByTestId('archetype-testimonial')).toBeInTheDocument()
    expect(screen.getByTestId('archetype-problem-solution')).toBeInTheDocument()
    expect(screen.getByTestId('archetype-tutorial')).toBeInTheDocument()
    expect(screen.getByTestId('archetype-comedy')).toBeInTheDocument()
    expect(screen.getByTestId('archetype-lifestyle')).toBeInTheDocument()
  })

  test('updates archetype on selection', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    fireEvent.click(screen.getByTestId('archetype-comedy'))
    expect(mockOnUpdate).toHaveBeenCalledWith({ archetype: 'comedy' })
  })

  test('renders mood slider', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    const slider = screen.getByTestId('mood-slider')
    expect(slider).toBeInTheDocument()
    expect(slider).toHaveAttribute('type', 'range')
  })

  test('renders energy slider', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    const slider = screen.getByTestId('energy-slider')
    expect(slider).toBeInTheDocument()
    expect(slider).toHaveAttribute('type', 'range')
  })

  test('updates mood on slider change', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    const slider = screen.getByTestId('mood-slider')
    fireEvent.change(slider, { target: { value: '75' } })

    expect(mockOnUpdate).toHaveBeenCalledWith({ mood: 75 })
  })

  test('next button is disabled when form is invalid', () => {
    render(
      <PromptRefinement
        adBrief={defaultBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    const button = screen.getByTestId('next-button')
    expect(button).toBeDisabled()
  })

  test('next button is enabled when form is valid', () => {
    const validBrief = {
      ...defaultBrief,
      productName: 'Test Product',
      description: 'Test description'
    }

    render(
      <PromptRefinement
        adBrief={validBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    const button = screen.getByTestId('next-button')
    expect(button).not.toBeDisabled()
  })

  test('calls onNext when next button is clicked', () => {
    const validBrief = {
      ...defaultBrief,
      productName: 'Test Product',
      description: 'Test description'
    }

    render(
      <PromptRefinement
        adBrief={validBrief}
        onUpdate={mockOnUpdate}
        onNext={mockOnNext}
      />
    )

    fireEvent.click(screen.getByTestId('next-button'))
    expect(mockOnNext).toHaveBeenCalled()
  })
})

