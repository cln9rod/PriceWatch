import React from 'react'
import { Handle, Position, NodeProps } from 'reactflow'

interface SourceNodeData {
  label: string
  config: {
    url?: string
    method?: string
    headers?: Record<string, string>
  }
}

const SourceNode: React.FC<NodeProps<SourceNodeData>> = ({ data, selected }) => {
  return (
    <div className={`px-4 py-2 shadow-lg rounded-lg bg-blue-50 border-2 min-w-[150px] ${
      selected ? 'border-blue-500' : 'border-blue-200'
    }`}>
      <div className="flex items-center">
        <div className="text-blue-600 mr-2">📥</div>
        <div>
          <div className="text-sm font-bold text-blue-800">{data.label}</div>
          <div className="text-xs text-blue-600">
            {data.config?.url ? new URL(data.config.url).hostname : 'Configure source'}
          </div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-blue-500 border-2 border-white"
        style={{ right: -6 }}
      />
    </div>
  )
}

export default SourceNode