'use client'

import { useState } from 'react'
import { Plug, Database, Webhook, Save } from 'lucide-react'

export default function IntegrationSettings() {
  const [neo4jUri, setNeo4jUri] = useState('bolt://localhost:7687')
  const [neo4jUser, setNeo4jUser] = useState('neo4j')
  const [webhookUrl, setWebhookUrl] = useState('')

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Integrations</h2>
      <p className="text-sm text-gray-600">Configure data sources and webhooks</p>

      <div className="space-y-4 pt-2">
        <div>
          <div className="flex items-center space-x-2 mb-2">
            <Database className="w-4 h-4 text-purple-600" />
            <h3 className="font-medium text-gray-900">Neo4j</h3>
          </div>
          <div className="space-y-3">
            <input
              type="text"
              value={neo4jUri}
              onChange={(e) => setNeo4jUri(e.target.value)}
              placeholder="bolt://host:7687"
              className="w-full px-3 py-2 border rounded-lg"
            />
            <input
              type="text"
              value={neo4jUser}
              onChange={(e) => setNeo4jUser(e.target.value)}
              placeholder="username"
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
        </div>

        <div>
          <div className="flex items-center space-x-2 mb-2">
            <Webhook className="w-4 h-4 text-purple-600" />
            <h3 className="font-medium text-gray-900">Webhook</h3>
          </div>
          <input
            type="text"
            value={webhookUrl}
            onChange={(e) => setWebhookUrl(e.target.value)}
            placeholder="https://example.com/webhook"
            className="w-full px-3 py-2 border rounded-lg"
          />
        </div>

        <div className="flex justify-end">
          <button className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition">
            <Save className="w-4 h-4 mr-2" />
            Save
          </button>
        </div>
      </div>
    </div>
  )
}


