import React from 'react'
import { Handle, Position, NodeProps } from 'reactflow'

interface DestinationNodeData {
  label: string
  config: {
    url?: string
    method?: string
    database?: string
  }
}

const DestinationNode: React.FC<NodeProps<DestinationNodeData>> = ({ data, selected }) => {
  return (
    <div className={`px-4 py-2 shadow-lg rounded-lg bg-purple-50 border-2 min-w-[150px] ${
      selected ? 'border-purple-500' : 'border-purple-200'
    }`}>
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-purple-500 border-2 border-white"
        style={{ left: -6 }}
      />

      <div className="flex items-center">
        <div className="text-purple-600 mr-2">📤</div>
        <div>
          <div className="text-sm font-bold text-purple-800">{data.label}</div>
          <div className="text-xs text-purple-600">
            {data.config?.database || data.config?.url ? 
              (data.config.database || new URL(data.config.url || '').hostname) : 
              'Configure destination'
            }
          </div>
        </div>
      </div>
    </div>
  )
}

export default DestinationNode