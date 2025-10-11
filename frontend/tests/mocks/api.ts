/**
 * Mock API responses for testing frontend-backend integration
 */

export const mockRecommendationResponses = {
  simple: {
    recommended_words: ["BASS", "PIKE", "SOLE", "CARP"],
    connection_explanation: "These are all types of fish.",
    provider_used: "simple",
    generation_time_ms: null,
    puzzle_state: {
      remaining_words: [
        "BASS", "PIKE", "SOLE", "CARP", "APPLE", "BANANA", "CHERRY", "GRAPE",
        "RED", "BLUE", "GREEN", "YELLOW", "CHAIR", "TABLE", "LAMP", "DESK"
      ],
      completed_groups: [],
      total_mistakes: 0,
      max_mistakes: 4,
      game_status: "active"
    },
    alternative_suggestions: [
      ["APPLE", "BANANA", "CHERRY", "GRAPE"],
      ["RED", "BLUE", "GREEN", "YELLOW"]
    ]
  },
  
  ollama: {
    recommended_words: ["BASS", "PIKE", "SOLE", "CARP"],
    connection_explanation: "These words are all types of fish. Bass and pike are freshwater fish commonly found in lakes and rivers, while sole and carp are also fish species.",
    provider_used: "ollama",
    generation_time_ms: 2340,
    puzzle_state: {
      remaining_words: [
        "BASS", "PIKE", "SOLE", "CARP", "APPLE", "BANANA", "CHERRY", "GRAPE",
        "RED", "BLUE", "GREEN", "YELLOW", "CHAIR", "TABLE", "LAMP", "DESK"
      ],
      completed_groups: [],
      total_mistakes: 0,
      max_mistakes: 4,
      game_status: "active"
    },
    alternative_suggestions: [
      ["APPLE", "BANANA", "CHERRY", "GRAPE"],
      ["RED", "BLUE", "GREEN", "YELLOW"]
    ]
  },
  
  openai: {
    recommended_words: ["APPLE", "BANANA", "CHERRY", "GRAPE"],
    connection_explanation: "These are all fruits. They are common fruits that people eat and are found in grocery stores and orchards.",
    provider_used: "openai",
    generation_time_ms: 1850,
    puzzle_state: {
      remaining_words: [
        "BASS", "PIKE", "SOLE", "CARP", "APPLE", "BANANA", "CHERRY", "GRAPE",
        "RED", "BLUE", "GREEN", "YELLOW", "CHAIR", "TABLE", "LAMP", "DESK"
      ],
      completed_groups: [],
      total_mistakes: 0,
      max_mistakes: 4,
      game_status: "active"
    },
    alternative_suggestions: [
      ["RED", "BLUE", "GREEN", "YELLOW"],
      ["CHAIR", "TABLE", "LAMP", "DESK"]
    ]
  }
};

export const mockProviderValidation = {
  simple: {
    provider_type: "simple",
    is_valid: true,
    status: "available",
    message: "Simple provider is always available"
  },
  
  ollama: {
    provider_type: "ollama",
    is_valid: true,
    status: "available",
    message: "Ollama is running and model is available"
  },
  
  openai: {
    provider_type: "openai",
    is_valid: true,
    status: "configured",
    message: "OpenAI API key is valid and service is available"
  },
  
  invalid: {
    provider_type: "invalid",
    is_valid: false,
    status: "not_configured",
    message: "Invalid provider type specified"
  }
};

export const mockErrorResponses = {
  network_error: {
    error: "Connection failed",
    detail: "Failed to connect to LLM provider. Please check your network connection and provider configuration."
  },
  
  api_key_error: {
    error: "Authentication failed",
    detail: "Invalid API key. Please check your OpenAI API key in the environment configuration."
  },
  
  provider_unavailable: {
    error: "Provider unavailable",
    detail: "The LLM provider is currently unavailable. Please try again later."
  }
};