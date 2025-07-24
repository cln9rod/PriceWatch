import React, { useCallback, useState, useRef } from 'react'
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  BackgroundVariant,
  MiniMap,
  ReactFlowProvider,
  useReactFlow,
} from 'reactflow'
import 'reactflow/dist/style.css'

import SourceNode from './nodes/SourceNode'
import TransformNode from './nodes/TransformNode'
import DestinationNode from './nodes/DestinationNode'

const nodeTypes = {
  source: SourceNode,
  transform: TransformNode,
  destination: DestinationNode,
}

const initialNodes: Node[] = [
  {
    id: 'example-1',
    type: 'source',
    position: { x: 100, y: 100 },
    data: { 
      label: 'API Source',
      config: {
        url: 'https://api.example.com/data',
        method: 'GET'
      }
    },
  },
  {
    id: 'example-2',
    type: 'transform',
    position: { x: 400, y: 200 },
    data: { 
      label: 'Filter Data',
      config: {
        condition: 'age > 18'
      }
    },
  },
]

const initialEdges: Edge[] = []

interface FlowEditorProps {
  onNodeSelect?: (node: Node | null) => void
}

const FlowEditorInner: React.FC<FlowEditorProps> = ({ onNodeSelect }) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const { project } = useReactFlow()

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const onNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      setSelectedNode(node)
      onNodeSelect?.(node)
    },
    [onNodeSelect]
  )

  const onPaneClick = useCallback(() => {
    setSelectedNode(null)
    onNodeSelect?.(null)
  }, [onNodeSelect])

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect()
      if (!reactFlowBounds) return

      const type = event.dataTransfer.getData('application/reactflow')
      const label = event.dataTransfer.getData('application/reactflow-label')

      if (!type) return

      const position = project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      })

      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: { 
          label,
          config: getDefaultConfig(type)
        },
      }

      setNodes((nds) => nds.concat(newNode))
    },
    [project, setNodes]
  )

  const getDefaultConfig = (type: string) => {
    switch (type) {
      case 'source':
        return { url: '', method: 'GET', headers: {} }
      case 'transform':
        return { operation: 'filter', condition: '' }
      case 'destination':
        return { url: '', method: 'POST' }
      default:
        return {}
    }
  }

  return (
    <div className="h-full w-full relative" ref={reactFlowWrapper}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        onDrop={onDrop}
        onDragOver={onDragOver}
        nodeTypes={nodeTypes}
        fitView
        className="bg-gray-50"
      >
        <Controls className="bg-white border border-gray-200 rounded-lg shadow-sm" />
        <MiniMap 
          className="bg-white border border-gray-200 rounded-lg shadow-sm"
          nodeColor={(node) => {
            switch (node.type) {
              case 'source': return '#3b82f6'
              case 'transform': return '#10b981'  
              case 'destination': return '#8b5cf6'
              default: return '#6b7280'
            }
          }}
        />
        <Background 
          variant={BackgroundVariant.Dots} 
          gap={20} 
          size={1}
          color="#e5e7eb"
        />
      </ReactFlow>
      
      {/* Empty State Overlay */}
      {nodes.length <= 2 && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center bg-white/90 backdrop-blur-sm rounded-lg p-8 border-2 border-dashed border-gray-300">
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Drop Nodes Here!
            </h3>
            <p className="text-gray-600 text-sm max-w-xs">
              Drag nodes from the left panel and drop them on this canvas to start building your pipeline.
            </p>
            <div className="mt-4 text-xs text-gray-500">
              • Drag any node to the canvas<br/>
              • Connect nodes by dragging between handles<br/>
              • Click nodes to configure them
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

const FlowEditor: React.FC<FlowEditorProps> = (props) => {
  return (
    <ReactFlowProvider>
      <FlowEditorInner {...props} />
    </ReactFlowProvider>
  )
}

export default FlowEditor