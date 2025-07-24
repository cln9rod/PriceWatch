import React from 'react'

const NodePalette: React.FC = () => {
  const onDragStart = (event: React.DragEvent, nodeType: string, label: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType)
    event.dataTransfer.setData('application/reactflow-label', label)
    event.dataTransfer.effectAllowed = 'move'
  }

  const nodes = [
    {
      category: 'Sources',
      items: [
        { type: 'source', label: 'API Source', icon: '📥', description: 'Connect to REST APIs' },
        { type: 'source', label: 'File Source', icon: '📄', description: 'Read CSV, JSON files' },
        { type: 'source', label: 'Database Source', icon: '🗄️', description: 'Query databases' },
        { type: 'source', label: 'Webhook', icon: '🔗', description: 'Receive webhooks' },
      ]
    },
    {
      category: 'Transforms',
      items: [
        { type: 'transform', label: 'Filter', icon: '🔍', description: 'Filter data records' },
        { type: 'transform', label: 'Map', icon: '🗂', description: 'Transform fields' },
        { type: 'transform', label: 'Aggregate', icon: '📊', description: 'Group and sum data' },
        { type: 'transform', label: 'Join', icon: '🔗', description: 'Combine data streams' },
      ]
    },
    {
      category: 'Destinations',
      items: [
        { type: 'destination', label: 'API Output', icon: '📤', description: 'Send to external API' },
        { type: 'destination', label: 'Database', icon: '💾', description: 'Store in database' },
        { type: 'destination', label: 'File Export', icon: '📋', description: 'Export to file' },
        { type: 'destination', label: 'Email', icon: '📧', description: 'Send email notifications' },
      ]
    }
  ]

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Sources': return 'blue'
      case 'Transforms': return 'green'
      case 'Destinations': return 'purple'
      default: return 'gray'
    }
  }

  return (
    <div className="w-64 bg-white border-r border-gray-200 p-4 overflow-y-auto">
      <h3 className="text-sm font-medium text-gray-900 mb-4">
        Node Palette
      </h3>
      <div className="text-xs text-gray-500 mb-4">
        Drag nodes to the canvas to build your pipeline
      </div>
      
      <div className="space-y-6">
        {nodes.map((category) => (
          <div key={category.category}>
            <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
              {category.category}
            </h4>
            <div className="space-y-2">
              {category.items.map((item) => {
                const color = getCategoryColor(category.category)
                return (
                  <div
                    key={`${item.type}-${item.label}`}
                    className={`bg-${color}-50 border border-${color}-200 rounded-md p-3 cursor-grab hover:bg-${color}-100 transition-colors`}
                    draggable
                    onDragStart={(event) => onDragStart(event, item.type, item.label)}
                  >
                    <div className="flex items-start">
                      <div className="text-lg mr-2">{item.icon}</div>
                      <div className="flex-1 min-w-0">
                        <div className={`text-sm font-medium text-${color}-800`}>
                          {item.label}
                        </div>
                        <div className={`text-xs text-${color}-600 mt-1`}>
                          {item.description}
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default NodePalette