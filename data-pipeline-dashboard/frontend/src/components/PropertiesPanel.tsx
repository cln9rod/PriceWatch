import { useState } from 'react'
import { PipelineNode } from '../types/pipeline'

interface PropertiesPanelProps {
  selectedNode: PipelineNode | null
  onNodeUpdate: (nodeId: string, newData: any) => void
}

const PropertiesPanel: React.FC<PropertiesPanelProps> = ({ selectedNode, onNodeUpdate }) => {
  const [jsonError, setJsonError] = useState<string | null>(null)

  const handleConfigChange = (key: string, value: string | Record<string, string>) => {
    if (!selectedNode) return
    
    try {
      const newConfig = {
        ...selectedNode.data.config,
        [key]: value
      }
      
      onNodeUpdate(selectedNode.id, {
        ...selectedNode.data,
        config: newConfig
      })
      setJsonError(null)
    } catch (error) {
      console.error('Config update failed:', error)
    }
  }

  const renderSourceConfig = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          URL
        </label>
        <input
          type="url"
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="https://api.example.com/data"
          value={selectedNode?.data.config.url || ''}
          onChange={(e) => handleConfigChange('url', e.target.value)}
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Method
        </label>
        <select
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={selectedNode?.data.config.method || 'GET'}
          onChange={(e) => handleConfigChange('method', e.target.value)}
        >
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="DELETE">DELETE</option>
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Headers (JSON)
        </label>
        <textarea
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={3}
          placeholder='{"Authorization": "Bearer token"}'
          value={JSON.stringify(selectedNode?.data.config.headers || {}, null, 2)}
          onChange={(e) => {
            try {
              const headers = JSON.parse(e.target.value || '{}')
              handleConfigChange('headers', headers)
              setJsonError(null)
            } catch (error) {
              setJsonError('Invalid JSON format')
            }
          }}
        />
        {jsonError && (
          <div className="mt-1 text-xs text-red-600">
            {jsonError}
          </div>
        )}
      </div>
    </div>
  )

  const renderTransformConfig = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Operation
        </label>
        <select
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          value={selectedNode?.data.config.operation || 'filter'}
          onChange={(e) => handleConfigChange('operation', e.target.value)}
        >
          <option value="filter">Filter</option>
          <option value="map">Map</option>
          <option value="aggregate">Aggregate</option>
          <option value="join">Join</option>
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Condition/Expression
        </label>
        <textarea
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          rows={3}
          placeholder="age > 18 && status === 'active'"
          value={selectedNode?.data.config.condition || ''}
          onChange={(e) => handleConfigChange('condition', e.target.value)}
        />
      </div>
    </div>
  )

  const renderDestinationConfig = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Type
        </label>
        <select
          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          value={selectedNode?.data.config.type || 'api'}
          onChange={(e) => handleConfigChange('type', e.target.value)}
        >
          <option value="api">API Endpoint</option>
          <option value="database">Database</option>
          <option value="file">File Export</option>
          <option value="email">Email</option>
        </select>
      </div>
      {selectedNode?.data.config.type !== 'database' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            URL
          </label>
          <input
            type="url"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="https://api.example.com/webhook"
            value={selectedNode?.data.config.url || ''}
            onChange={(e) => handleConfigChange('url', e.target.value)}
          />
        </div>
      )}
      {selectedNode?.data.config.type === 'database' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Database Connection
          </label>
          <input
            type="text"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="postgresql://localhost:5432/mydb"
            value={selectedNode?.data.config.database || ''}
            onChange={(e) => handleConfigChange('database', e.target.value)}
          />
        </div>
      )}
    </div>
  )

  if (!selectedNode) {
    return (
      <div className="w-80 bg-white border-l border-gray-200 p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-4">
          Properties
        </h3>
        <div className="text-sm text-gray-500 text-center py-8">
          <div className="text-4xl mb-2">⚙️</div>
          Select a node to configure its properties
        </div>
      </div>
    )
  }

  return (
    <div className="w-80 bg-white border-l border-gray-200 p-4 overflow-y-auto">
      <h3 className="text-sm font-medium text-gray-900 mb-4">
        Properties
      </h3>
      
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="text-sm font-medium text-gray-900">
          {selectedNode.data.label}
        </div>
        <div className="text-xs text-gray-500 mt-1">
          ID: {selectedNode.id}
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Node Label
          </label>
          <input
            type="text"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={selectedNode.data.label}
            onChange={(e) => onNodeUpdate(selectedNode.id, {
              ...selectedNode.data,
              label: e.target.value
            })}
          />
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">
            Configuration
          </h4>
          {selectedNode.type === 'source' && renderSourceConfig()}
          {selectedNode.type === 'transform' && renderTransformConfig()}
          {selectedNode.type === 'destination' && renderDestinationConfig()}
        </div>
      </div>
    </div>
  )
}

export default PropertiesPanel