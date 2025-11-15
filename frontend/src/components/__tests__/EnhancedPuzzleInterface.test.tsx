import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import EnhancedPuzzleInterface from '../EnhancedPuzzleInterface';
import { llmApiService } from '../../services/llm-api';

jest.mock('../../services/llm-api');

describe('EnhancedPuzzleInterface - Get Recommendation button behavior', () => {
  const mockGenerate = jest.fn();

  beforeAll(() => {
    // @ts-ignore
    llmApiService.generateRecommendation = mockGenerate;
  });

  beforeEach(() => {
    mockGenerate.mockClear();
  });

  test('disables Get AI Recommendation on click and re-enables after response button click', async () => {
    mockGenerate.mockResolvedValueOnce({
      recommended_words: ['BASS','PIKE','SOLE','CARP'],
      connection_explanation: 'Fish',
      provider_used: 'simple'
    });

    const onRecordResponse = jest.fn(() => Promise.resolve());

    render(
      <EnhancedPuzzleInterface
        words={['BASS','PIKE','SOLE','CARP']}
        recommendation={[]}
        recommendationConnection={''}
        correctCount={0}
        mistakeCount={0}
        gameStatus={'active'}
        isLoading={false}
        error={null}
        onRecordResponse={onRecordResponse}
        previousResponses={[]}
      />
    );

    const getBtn = screen.getByText(/Get AI Recommendation/i) as HTMLButtonElement;
    expect(getBtn).toBeInTheDocument();

    // Click the button - it should become disabled immediately
    fireEvent.click(getBtn);
    expect(getBtn).toBeDisabled();

    // Wait for the recommendation display and response buttons to render
    await waitFor(() => expect(screen.getByText(/How was this recommendation\?/i)).toBeInTheDocument());

    // Recommendation display should be visible (header)
    expect(screen.getByRole('heading', { name: /AI Recommendation/i })).toBeInTheDocument();

    const incorrectBtn = screen.getByText(/Incorrect/i) as HTMLButtonElement;
    expect(incorrectBtn).toBeInTheDocument();

    // Click a response button - the recommendation should be hidden and Get button re-enabled
    fireEvent.click(incorrectBtn);

    await waitFor(() => expect(getBtn).not.toBeDisabled());

    // Recommendation display should no longer be present (header)
    await waitFor(() => expect(screen.queryByRole('heading', { name: /AI Recommendation/i })).not.toBeInTheDocument(), { timeout: 500 });
  });
});
