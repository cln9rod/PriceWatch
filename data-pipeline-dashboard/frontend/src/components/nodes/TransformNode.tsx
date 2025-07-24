import React from 'react'
import { Handle, Position, NodeProps } from 'reactflow'

interface TransformNodeData {
  label: string
  config: {
    operation?: string
    condition?: string
  }
}

const TransformNode: React.FC<NodeProps<TransformNodeData>> = ({ data, selected }) => {
  return (
    <div className={`px-4 py-2 shadow-lg rounded-lg bg-green-50 border-2 min-w-[150px] ${
      selected ? 'border-green-500' : 'border-green-200'
    }`}>
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-green-500 border-2 border-white"
        style={{ left: -6 }}
      />

      <div className="flex items-center">
        <div className="text-green-600 mr-2">🔄</div>
        <div>
          <div className="text-sm font-bold text-green-800">{data.label}</div>
          <div className="text-xs text-green-600">
            {data.config?.operation || 'Configure transform'}
          </div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-green-500 border-2 border-white"
        style={{ right: -6 }}
      />
    </div>
  )
}

export default TransformNode