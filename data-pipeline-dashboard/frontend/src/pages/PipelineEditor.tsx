import { useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { PipelineNode } from '../types/pipeline'
import NodePalette from '../components/NodePalette'
import PropertiesPanel from '../components/PropertiesPanel'
import CustomCanvas from '../components/CustomCanvas'

const PipelineEditor: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<PipelineNode | null>(null)

  const handleNodeSelect = useCallback((node: PipelineNode | null) => {
    setSelectedNode(node)
  }, [])

  const handleNodeUpdate = useCallback((nodeId: string, newData: any) => {
    // This would typically update the nodes in the FlowEditor
    // For now, we'll just update the selectedNode
    if (selectedNode?.id === nodeId) {
      setSelectedNode({
        ...selectedNode,
        data: newData
      })
    }
  }, [selectedNode])

  return (
    <div style={{ width: '100%', height: '100vh', overflow: 'hidden' }}>
      {/* Header */}
      <header style={{ 
        height: '64px', 
        backgroundColor: 'white', 
        borderBottom: '1px solid #e5e7eb',
        display: 'flex',
        alignItems: 'center',
        padding: '0 24px',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 10
      }}>
        <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
          <Link
            to="/"
            style={{ color: '#6b7280', textDecoration: 'none', marginRight: '16px' }}
          >
            ← Back to Dashboard
          </Link>
          <h1 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', margin: 0 }}>
            Pipeline Editor
          </h1>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button style={{ 
            backgroundColor: '#e5e7eb', 
            color: '#374151', 
            padding: '8px 16px', 
            borderRadius: '6px',
            border: 'none',
            fontSize: '14px',
            cursor: 'pointer'
          }}>
            Test Run
          </button>
          <button style={{ 
            backgroundColor: '#2563eb', 
            color: 'white', 
            padding: '8px 16px', 
            borderRadius: '6px',
            border: 'none',
            fontSize: '14px',
            cursor: 'pointer'
          }}>
            Save Pipeline
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div style={{ 
        marginTop: '64px', 
        height: 'calc(100vh - 64px)', 
        display: 'flex',
        minWidth: '800px',
        width: '100%'
      }}>
        {/* Node Palette */}
        <div className="w-48 min-w-48 bg-white border-r border-gray-200 p-4 overflow-y-auto flex-shrink-0">
          <NodePalette />
        </div>

        {/* Canvas Area */}
        <div className="flex-1 bg-gray-50 min-w-80">
          <CustomCanvas onNodeSelect={handleNodeSelect} />
        </div>

        {/* Properties Panel */}
        <div className="w-64 min-w-64 bg-white border-l border-gray-200 flex-shrink-0">
          <PropertiesPanel 
            selectedNode={selectedNode} 
            onNodeUpdate={handleNodeUpdate}
          />
        </div>              
      </div>
    </div>
  )
}

export default PipelineEditor