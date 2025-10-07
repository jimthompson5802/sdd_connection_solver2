import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PuzzleInterface from '../../../src/components/PuzzleInterface';

describe('Correct button integration (PuzzleInterface)', () => {
  test('clicking Correct button calls onRecordResponse with recommendation words', async () => {
    const words = [
      'alpha','bravo','charlie','delta','echo','foxtrot','golf','hotel',
      'india','juliet','kilo','lima','mike','november','oscar','papa'
    ];

    const recommended = ['alpha','bravo','charlie','delta'];

    const mockRecord = jest.fn();

    render(
      <PuzzleInterface
        words={words}
        recommendation={recommended}
        recommendationConnection={'test'}
        correctCount={0}
        mistakeCount={0}
        gameStatus={'active'}
        isLoading={false}
        error={null}
        onRecordResponse={mockRecord}
        previousResponses={[]}
      />
    );

    // Wait for the Correct (Yellow) button to be in the document
    await waitFor(() => expect(screen.getByRole('button', { name: /Correct \(Yellow\)/i })).toBeInTheDocument());

    // Click Correct (Yellow)
    fireEvent.click(screen.getByRole('button', { name: /Correct \(Yellow\)/i }));

    expect(mockRecord).toHaveBeenCalled();
    const callArgs = mockRecord.mock.calls[0];
    // onRecordResponse(type, color?, words?)
    expect(callArgs[0]).toBe('correct');
    expect(callArgs[1]).toBe('Yellow');
    expect(callArgs[2]).toEqual(recommended);
  });
});
