/**
 * Validation tests for API Service implementation.
 * These tests validate that our actual API service works correctly.
 */

import { ApiService } from '../services/api';
import { PuzzleError } from '../types/puzzle';

describe('ApiService - Implementation Validation', () => {
  describe('parseAndValidateCSV', () => {
    test('validates correct CSV with 16 words', () => {
      const validCSV = 'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16';
      
      expect(() => {
        ApiService.parseAndValidateCSV(validCSV);
      }).not.toThrow();
    });

    test('returns array of 16 words for valid CSV', () => {
      const validCSV = 'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16';
      
      const result = ApiService.parseAndValidateCSV(validCSV);
      expect(result).toHaveLength(16);
      expect(result[0]).toBe('word1');
      expect(result[15]).toBe('word16');
    });

    test('throws error for empty content', () => {
      expect(() => {
        ApiService.parseAndValidateCSV('');
      }).toThrow(PuzzleError);
      
      expect(() => {
        ApiService.parseAndValidateCSV('   ');
      }).toThrow('File cannot be empty');
    });

    test('throws error for wrong number of words', () => {
      const tooFewWords = 'word1,word2,word3';
      const tooManyWords = 'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16,word17';
      
      expect(() => {
        ApiService.parseAndValidateCSV(tooFewWords);
      }).toThrow('File must contain exactly 16 words');
      
      expect(() => {
        ApiService.parseAndValidateCSV(tooManyWords);
      }).toThrow('File must contain exactly 16 words');
    });

    test('throws error for duplicate words', () => {
      const duplicateWords = 'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word1';
      
      expect(() => {
        ApiService.parseAndValidateCSV(duplicateWords);
      }).toThrow('All words must be unique');
    });

    test('handles whitespace in CSV correctly', () => {
      const csvWithSpaces = ' word1 , word2 , word3 , word4 , word5 , word6 , word7 , word8 , word9 , word10 , word11 , word12 , word13 , word14 , word15 , word16 ';
      
      const result = ApiService.parseAndValidateCSV(csvWithSpaces);
      expect(result).toHaveLength(16);
      expect(result[0]).toBe('word1');
      expect(result[15]).toBe('word16');
    });
  });

  describe('validateFileContent', () => {
    test('validates file content without throwing for valid CSV', () => {
      const validCSV = 'word1,word2,word3,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16';
      
      expect(() => {
        ApiService.validateFileContent(validCSV);
      }).not.toThrow();
    });
  });

  describe('constructor and configuration', () => {
    test('creates instance with default base URL', () => {
      const service = new ApiService();
      expect(service).toBeInstanceOf(ApiService);
    });
  });
});