import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/search',
    component: ComponentCreator('/search', '044'),
    exact: true
  },
  {
    path: '/',
    component: ComponentCreator('/', 'be6'),
    routes: [
      {
        path: '/',
        component: ComponentCreator('/', '493'),
        routes: [
          {
            path: '/',
            component: ComponentCreator('/', '514'),
            routes: [
              {
                path: '/flows/image-puzzle-setup-flow',
                component: ComponentCreator('/flows/image-puzzle-setup-flow', 'a4f'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/flows/ollama-recommendation-flow',
                component: ComponentCreator('/flows/ollama-recommendation-flow', 'd3e'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/flows/provider-validation-flow',
                component: ComponentCreator('/flows/provider-validation-flow', 'eb5'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/flows/puzzle-setup-flow',
                component: ComponentCreator('/flows/puzzle-setup-flow', 'b0c'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/flows/recommendation-generation-flow',
                component: ComponentCreator('/flows/recommendation-generation-flow', '409'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/flows/response-recording-flow',
                component: ComponentCreator('/flows/response-recording-flow', 'f2a'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/nodes/backend-api-service',
                component: ComponentCreator('/nodes/backend-api-service', '784'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/nodes/frontend-webclient',
                component: ComponentCreator('/nodes/frontend-webclient', '022'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/nodes/ollama-llm-service',
                component: ComponentCreator('/nodes/ollama-llm-service', '948'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/nodes/openai-llm-service',
                component: ComponentCreator('/nodes/openai-llm-service', '4ec'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/nodes/player',
                component: ComponentCreator('/nodes/player', '158'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/relationships/backend-to-ollama-connection',
                component: ComponentCreator('/relationships/backend-to-ollama-connection', 'ef1'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/relationships/backend-to-openai-connection',
                component: ComponentCreator('/relationships/backend-to-openai-connection', '933'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/relationships/frontend-to-backend-connection',
                component: ComponentCreator('/relationships/frontend-to-backend-connection', '1f3'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/relationships/player-interaction',
                component: ComponentCreator('/relationships/player-interaction', '767'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/',
                component: ComponentCreator('/', 'bea'),
                exact: true,
                sidebar: "docs"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
