/**
 * API Contracts: Image-Based Puzzle Setup
 * 
 * Feature: 004-image-puzzle-setup
 * Endpoint: POST /api/v2/setup_puzzle_from_image
 * 
 * This file defines TypeScript interfaces for the image setup API contract,
 * ensuring type safety between frontend and backend.
 */

// ============================================================================
// Request/Response Models
// ============================================================================

/**
 * Request payload for POST /api/v2/setup_puzzle_from_image
 * 
 * Sent from ImagePuzzleSetup component to backend endpoint.
 * 
 * @example
 * ```typescript
 * const request: ImageSetupRequest = {
 *   image_base64: "iVBORw0KGgoAAAANSUhEUgAA...",
 *   image_mime: "image/png",
 *   provider_type: "openai",
 *   model_name: "gpt-4-vision-preview"
 * };
 * ```
 */
export interface ImageSetupRequest {
  /**
   * Base64-encoded image content (without data URL prefix)
   * 
   * Must not exceed 5MB original size (~6.67MB base64 encoded).
   * Generated from Clipboard API Blob via FileReader.
   */
  image_base64: string;

  /**
   * Image MIME type
   * 
   * Supported types:
   * - image/png
   * - image/jpeg
   * - image/jpg
   * - image/gif
   * - image/webp
   * 
   * Extracted from Clipboard API Blob.type
   */
  image_mime: string;

  /**
   * LLM provider type for word extraction
   * 
   * Supported providers:
   * - "openai": OpenAI GPT-4 Vision models
   * - "ollama": Ollama vision models (llava, bakllava, etc.)
   * - "simple": Not supported (will return error)
   * 
   * Matches user's selected provider from dropdown.
   */
  provider_type: string;

  /**
   * Specific model name for provider
   * 
   * Examples:
   * - OpenAI: "gpt-4-vision-preview", "gpt-4-turbo"
   * - Ollama: "llava", "bakllava", "llava-llama3"
   * 
   * Matches user's selected model from dropdown.
   */
  model_name: string;
}

/**
 * Response payload from POST /api/v2/setup_puzzle_from_image
 * 
 * Returned from backend endpoint to ImagePuzzleSetup component.
 * 
 * @example Success Response
 * ```typescript
 * const response: ImageSetupResponse = {
 *   remaining_words: ["apple", "banana", "cherry", ...],  // 16 words
 *   status: "success"
 * };
 * ```
 * 
 * @example Error Response
 * ```typescript
 * const response: ImageSetupResponse = {
 *   remaining_words: [],
 *   status: "error",
 *   message: "Could not extract 16 words from image"
 * };
 * ```
 */
export interface ImageSetupResponse {
  /**
   * Extracted words from image
   * 
   * - Success: Array of exactly 16 words (lowercase)
   * - Error: Empty array
   * 
   * Words are in left-to-right, top-to-bottom reading order:
   * [row1_col1, row1_col2, row1_col3, row1_col4,
   *  row2_col1, row2_col2, row2_col3, row2_col4,
   *  row3_col1, row3_col2, row3_col3, row3_col4,
   *  row4_col1, row4_col2, row4_col3, row4_col4]
   */
  remaining_words: string[];

  /**
   * Setup status
   * 
   * - "success": Word extraction succeeded
   * - "error": Word extraction failed
   */
  status: 'success' | 'error';

  /**
   * Error message (present only when status is "error")
   * 
   * Common error messages:
   * - "Could not extract 16 words from image"
   * - "Selected model does not support image analysis"
   * - "Image size exceeds 5MB limit"
   * - "Unsupported MIME type: {type}"
   * - "LLM provider error - please retry"
   */
  message?: string;
}

// ============================================================================
// HTTP Status Codes
// ============================================================================

/**
 * HTTP status codes for /api/v2/setup_puzzle_from_image endpoint
 * 
 * Use for type-safe error handling in frontend.
 */
export enum ImageSetupStatusCode {
  /** Successfully extracted 16 words */
  OK = 200,

  /** Bad request (invalid image, wrong word count, model lacks vision) */
  BAD_REQUEST = 400,

  /** Payload too large (image > 5MB) */
  PAYLOAD_TOO_LARGE = 413,

  /** Unprocessable entity (missing required fields) */
  UNPROCESSABLE_ENTITY = 422,

  /** Internal server error (LLM provider failure) */
  INTERNAL_SERVER_ERROR = 500
}

// ============================================================================
// API Service Method
// ============================================================================

/**
 * API service method signature for image setup
 * 
 * To be added to frontend/src/services/api.ts
 * 
 * @example Implementation
 * ```typescript
 * async setupPuzzleFromImage(
 *   imageBase64: string,
 *   imageMime: string,
 *   providerType: string,
 *   modelName: string
 * ): Promise<ImageSetupResponse> {
 *   const request: ImageSetupRequest = {
 *     image_base64: imageBase64,
 *     image_mime: imageMime,
 *     provider_type: providerType,
 *     model_name: modelName
 *   };
 * 
 *   const response = await fetch(`${this.baseUrl}/api/v2/setup_puzzle_from_image`, {
 *     method: 'POST',
 *     headers: { 'Content-Type': 'application/json' },
 *     body: JSON.stringify(request)
 *   });
 * 
 *   if (!response.ok) {
 *     const error: ImageSetupResponse = await response.json();
 *     throw new Error(error.message || 'Image setup failed');
 *   }
 * 
 *   return response.json();
 * }
 * ```
 * 
 * @param imageBase64 - Base64-encoded image content
 * @param imageMime - Image MIME type
 * @param providerType - LLM provider type
 * @param modelName - Specific model name
 * @returns Promise resolving to ImageSetupResponse
 * @throws Error with message from ImageSetupResponse.message
 */
export type SetupPuzzleFromImageMethod = (
  imageBase64: string,
  imageMime: string,
  providerType: string,
  modelName: string
) => Promise<ImageSetupResponse>;

// ============================================================================
// Error Type Guards
// ============================================================================

/**
 * Type guard to check if response is a success response
 * 
 * @example
 * ```typescript
 * const response = await api.setupPuzzleFromImage(...);
 * 
 * if (isSuccessResponse(response)) {
 *   // TypeScript knows response.remaining_words has 16 words
 *   onImageSetup(response.remaining_words);
 * } else {
 *   // TypeScript knows response.message exists
 *   onError(response.message);
 * }
 * ```
 */
export function isSuccessResponse(
  response: ImageSetupResponse
): response is ImageSetupResponse & { status: 'success'; remaining_words: [string, string, string, string, string, string, string, string, string, string, string, string, string, string, string, string] } {
  return response.status === 'success' && response.remaining_words.length === 16;
}

/**
 * Type guard to check if response is an error response
 * 
 * @example
 * ```typescript
 * const response = await api.setupPuzzleFromImage(...);
 * 
 * if (isErrorResponse(response)) {
 *   // TypeScript knows response.message exists
 *   console.error(response.message);
 * }
 * ```
 */
export function isErrorResponse(
  response: ImageSetupResponse
): response is ImageSetupResponse & { status: 'error'; message: string } {
  return response.status === 'error' && response.message !== undefined;
}

// ============================================================================
// Validation Helpers
// ============================================================================

/**
 * Client-side validation for image before API call
 * 
 * @example
 * ```typescript
 * const validation = validateImageRequest(imageData, imageMime, 5242880);
 * 
 * if (!validation.isValid) {
 *   setError(validation.error);
 *   return;
 * }
 * 
 * // Proceed with API call
 * const response = await api.setupPuzzleFromImage(...);
 * ```
 */
export interface ImageValidationResult {
  /** Whether image passes all validation checks */
  isValid: boolean;

  /** Error message if validation fails */
  error: string | null;
}

/**
 * Validate image base64 and MIME type before sending to API
 * 
 * @param imageBase64 - Base64-encoded image content
 * @param imageMime - Image MIME type
 * @param sizeBytes - Original image size in bytes
 * @returns Validation result with isValid flag and error message
 */
export function validateImageRequest(
  imageBase64: string,
  imageMime: string,
  sizeBytes: number
): ImageValidationResult {
  // Size check (5MB limit)
  const MAX_SIZE_BYTES = 5_242_880;
  if (sizeBytes > MAX_SIZE_BYTES) {
    return {
      isValid: false,
      error: 'Image too large (max 5MB)'
    };
  }

  // MIME type check
  const SUPPORTED_MIMES = [
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/gif',
    'image/webp'
  ];
  if (!SUPPORTED_MIMES.includes(imageMime)) {
    return {
      isValid: false,
      error: `Unsupported format: ${imageMime}. Use PNG, JPEG, or GIF.`
    };
  }

  // Base64 check
  if (!imageBase64 || imageBase64.trim() === '') {
    return {
      isValid: false,
      error: 'Image data is empty'
    };
  }

  return {
    isValid: true,
    error: null
  };
}

// ============================================================================
// OpenAPI Schema (for reference)
// ============================================================================

/**
 * OpenAPI 3.0 schema for /api/v2/setup_puzzle_from_image endpoint
 * 
 * This is the canonical API contract used for backend validation
 * and frontend code generation.
 * 
 * @openapi
 * /api/v2/setup_puzzle_from_image:
 *   post:
 *     summary: Setup puzzle from image using LLM vision
 *     description: Extracts 16 words from a 4x4 grid image using LLM vision capabilities
 *     tags:
 *       - Puzzle Setup
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/ImageSetupRequest'
 *     responses:
 *       200:
 *         description: Successfully extracted words
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ImageSetupResponseSuccess'
 *       400:
 *         description: Bad request (invalid image, wrong word count, model lacks vision)
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ImageSetupResponseError'
 *       413:
 *         description: Payload too large (image > 5MB)
 *       422:
 *         description: Unprocessable entity (missing required fields)
 *       500:
 *         description: Internal server error (LLM provider failure)
 * 
 * components:
 *   schemas:
 *     ImageSetupRequest:
 *       type: object
 *       required:
 *         - image_base64
 *         - image_mime
 *         - provider_type
 *         - model_name
 *       properties:
 *         image_base64:
 *           type: string
 *           description: Base64-encoded image content
 *         image_mime:
 *           type: string
 *           enum: [image/png, image/jpeg, image/jpg, image/gif, image/webp]
 *         provider_type:
 *           type: string
 *           enum: [openai, ollama, simple]
 *         model_name:
 *           type: string
 *     
 *     ImageSetupResponseSuccess:
 *       type: object
 *       required:
 *         - remaining_words
 *         - status
 *       properties:
 *         remaining_words:
 *           type: array
 *           items:
 *             type: string
 *           minItems: 16
 *           maxItems: 16
 *         status:
 *           type: string
 *           enum: [success]
 *     
 *     ImageSetupResponseError:
 *       type: object
 *       required:
 *         - remaining_words
 *         - status
 *         - message
 *       properties:
 *         remaining_words:
 *           type: array
 *           items:
 *             type: string
 *           maxItems: 0
 *         status:
 *           type: string
 *           enum: [error]
 *         message:
 *           type: string
 */
