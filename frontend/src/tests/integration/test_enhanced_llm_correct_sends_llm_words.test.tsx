import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import EnhancedPuzzleInterface from '../../../src/components/EnhancedPuzzleInterface';
import { llmApiService } from '../../../src/services/llm-api';

jest.mock('../../../src/services/llm-api');

describe('EnhancedPuzzleInterface LLM flow', () => {
  test('clicking Correct uses llmRecommendation.recommended_words when useLlm=true', async () => {
    const words = [
      'alpha','bravo','charlie','delta','echo','foxtrot','golf','hotel',
      'india','juliet','kilo','lima','mike','november','oscar','papa'
    ];

    const recommendation: string[] = [];
    const llmRecommendation = {
      recommended_words: ['alpha','bravo','charlie','delta'],
      connection_explanation: 'test',
      confidence_score: 0.9,
      provider_used: 'simple',
    } as any;

    const mockRecord = jest.fn().mockResolvedValue({
      remaining_words: words.slice(4),
      correct_count: 1,
      mistake_count: 0,
      game_status: 'active',
    });

    render(
      <EnhancedPuzzleInterface
        words={words}
        recommendation={recommendation}
        recommendationConnection={''}
        correctCount={0}
        mistakeCount={0}
        gameStatus={'active'}
        isLoading={false}
  error={null}
        onRecordResponse={mockRecord}
        previousResponses={[]}
        llmProvider={{ provider_type: 'simple', model_name: null }}
        onProviderChange={jest.fn()}
        showProviderControls={true}
        puzzleContext={''}
        previousGuesses={[]}
        llmRecommendationOverride={llmRecommendation}
      />
    );

    // Simulate setting an LLM recommendation: the component stores llmRecommendation internally in real code; here we simulate by
    // finding the LLM "Get AI Recommendation" button and clicking it. For this test we won't actually call the llm api, so
    // we need to simulate that the component shows the LLM recommendation. To keep the test focused and minimal, we'll directly
    // re-render the component with the llmRecommendation visible by rendering again with a prop-based approach isn't possible
    // because EnhancedPuzzleInterface manages its own LLM state. Instead we'll find the traditional "Correct" buttons and call them
    // with the assumption that useLlm = true will send the llmRecommendation.

  // Now the Correct button should be available (llmRecommendationOverride renders the LLM section); click it
  const correctBtn = await screen.findByRole('button', { name: /Correct \(Yellow\)/i });
  fireEvent.click(correctBtn);

    // Assert record called with attemptWords (third arg)
    await waitFor(() => expect(mockRecord).toHaveBeenCalled());
    const callArgs = mockRecord.mock.calls[0];
    expect(callArgs[0]).toBe('correct');
    expect(callArgs[1]).toBe('Yellow');
    expect(callArgs[2]).toEqual(llmRecommendation.recommended_words);
  });
});
