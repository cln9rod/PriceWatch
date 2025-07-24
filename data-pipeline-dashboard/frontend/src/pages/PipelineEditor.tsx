import React, { useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Node } from 'reactflow'
import FlowEditor from '../components/FlowEditor'
import NodePalette from '../components/NodePalette'
import PropertiesPanel from '../components/PropertiesPanel'

const PipelineEditor: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [nodes, setNodes] = useState<Node[]>([])

  const handleNodeSelect = useCallback((node: Node | null) => {
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b fixed top-0 left-0 right-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link
                to="/"
                className="text-gray-500 hover:text-gray-700 mr-4"
              >
                ← Back to Dashboard
              </Link>
              <h1 className="text-xl font-semibold text-gray-900">
                Pipeline Editor
              </h1>
            </div>
            <div className="flex space-x-2">
              <button className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium transition-colors">
                Test Run
              </button>
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                Save Pipeline
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex h-screen pt-16">
        {/* Node Palette */}
        <NodePalette />

        {/* Canvas Area */}
        <div className="flex-1 bg-gray-100">
          <FlowEditor onNodeSelect={handleNodeSelect} />
        </div>

        {/* Properties Panel */}
        <PropertiesPanel 
          selectedNode={selectedNode} 
          onNodeUpdate={handleNodeUpdate}
        />
      </main>
    </div>
  )
}

export default PipelineEditor