import { DragEvent } from 'react'
import { NodeCategory, NodeColors } from '../types/pipeline'

const NodePalette: React.FC = () => {
  const handleDragStart = (event: DragEvent, nodeType: string, label: string) => {
    try {
      event.dataTransfer.setData('application/reactflow', nodeType)
      event.dataTransfer.setData('application/reactflow-label', label)
      event.dataTransfer.effectAllowed = 'move'
    } catch (error) {
      console.error('Drag start failed:', error)
    }
  }

  const nodeCategories: NodeCategory[] = [
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

  const getCategoryColor = (category: string): keyof typeof colorSchemes => {
    switch (category) {
      case 'Sources': return 'blue'
      case 'Transforms': return 'green' 
      case 'Destinations': return 'purple'
      default: return 'blue'
    }
  }

  const colorSchemes: Record<string, NodeColors> = {
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      hover: 'hover:bg-blue-100',
      text: 'text-blue-800',
      description: 'text-blue-600'
    },
    green: {
      bg: 'bg-green-50',
      border: 'border-green-200', 
      hover: 'hover:bg-green-100',
      text: 'text-green-800',
      description: 'text-green-600'
    },
    purple: {
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      hover: 'hover:bg-purple-100', 
      text: 'text-purple-800',
      description: 'text-purple-600'
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
        {nodeCategories.map((category) => (
          <div key={category.category}>
            <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
              {category.category}
            </h4>
            <div className="space-y-2">
              {category.items.map((item) => {
                const color = getCategoryColor(category.category)
                const classes = colorSchemes[color]
                
                return (
                  <div
                    key={`${item.type}-${item.label}`}
                    className={`${classes.bg} border ${classes.border} rounded-md p-3 cursor-grab ${classes.hover} transition-colors`}
                    draggable
                    onDragStart={(event) => handleDragStart(event, item.type, item.label)}
                  >
                    <div className="flex items-start">
                      <div className="text-lg mr-2">{item.icon}</div>
                      <div className="flex-1 min-w-0">
                        <div className={`text-sm font-medium ${classes.text}`}>
                          {item.label}
                        </div>
                        <div className={`text-xs ${classes.description} mt-1`}>
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