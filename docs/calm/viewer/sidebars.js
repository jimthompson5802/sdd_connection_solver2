module.exports = {
    docs: [
        {
            type: 'doc',
            id: 'index',
            label: 'Home',
        },
        {
            type: 'category',
            label: 'Nodes',
            items: [
                'nodes/player',
                'nodes/frontend-webclient',
                'nodes/backend-api-service',
                'nodes/openai-llm-service',
                'nodes/ollama-llm-service'
            ],
        },
        {
            type: 'category',
            label: 'Relationships',
            items: [
                'relationships/player-interaction',
                'relationships/frontend-to-backend-connection',
                'relationships/backend-to-openai-connection',
                'relationships/backend-to-ollama-connection'
            ],
        },
        {
            type: 'category',
            label: 'Flows',
            items: [
                'flows/puzzle-setup-flow',
                'flows/recommendation-generation-flow',
                'flows/ollama-recommendation-flow',
                'flows/response-recording-flow',
                'flows/provider-validation-flow',
                'flows/image-puzzle-setup-flow'
            ],
        }
    ]
};
