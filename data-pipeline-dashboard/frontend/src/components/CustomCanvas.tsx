import { useCallback, useState } from 'react'
import { PipelineNode } from '../types/pipeline'
import { getDefaultNodeConfig, getNodeColorScheme, getNodeIcon, generateNodeId } from '../utils/nodeUtils'

// Use our custom type that extends ReactFlow's Node
type CanvasProps = {
  onNodeSelect?: (node: PipelineNode | null) => void
}

const CustomCanvas: React.FC<CanvasProps> = ({ onNodeSelect }) => {
  const [nodes, setNodes] = useState<PipelineNode[]>([])
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const type = event.dataTransfer.getData('application/reactflow')
      const label = event.dataTransfer.getData('application/reactflow-label')

      if (!type) {
        return
      }

      // Get canvas bounds and calculate relative position
      const canvasBounds = (event.currentTarget as HTMLElement).getBoundingClientRect()
      const position = {
        x: event.clientX - canvasBounds.left - 50, // Center the node
        y: event.clientY - canvasBounds.top - 25
      }


      const newNode: PipelineNode = {
        id: generateNodeId(type),
        type: type as 'source' | 'transform' | 'destination',
        position,
        data: { 
          label: label || 'New Node',
          config: getDefaultNodeConfig(type)
        },
      }

      setNodes((nds) => nds.concat(newNode))
    },
    [setNodes]
  )

  const handleNodeClick = (node: PipelineNode) => {
    setSelectedNodeId(node.id)
    onNodeSelect?.(node)
  }


  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        backgroundColor: '#f9fafb',
        position: 'relative',
        backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)',
        backgroundSize: '20px 20px',
        overflow: 'hidden'
      }}
      onDragOver={onDragOver}
      onDrop={onDrop}
      onClick={() => {
        setSelectedNodeId(null)
        onNodeSelect?.(null)
      }}
    >
      {/* Success indicator */}
      <div 
        style={{
          position: 'absolute',
          top: '10px',
          left: '10px',
          background: 'rgba(34,197,94,0.1)',
          border: '2px solid #22c55e',
          padding: '10px',
          borderRadius: '4px',
          fontSize: '12px',
          zIndex: 1001,
          pointerEvents: 'none'
        }}
      >
        ✅ Custom Canvas<br/>
        Nodes: {nodes.length}<br/>
        Working perfectly!
      </div>

      {/* Help text when empty */}
      {nodes.length === 0 && (
        <div 
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
            pointerEvents: 'none',
            background: 'rgba(255,255,255,0.9)',
            padding: '20px',
            borderRadius: '8px',
            border: '2px dashed #ccc',
            zIndex: 1000
          }}
        >
          <div style={{ fontSize: '24px', marginBottom: '10px' }}>🎯</div>
          <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>Drop Nodes Here!</div>
          <div style={{ fontSize: '14px', color: '#666' }}>
            Drag nodes from the left panel and drop them here
          </div>
        </div>
      )}

      {/* Render nodes */}
      {nodes.map((node) => {
        const colors = getNodeColorScheme(node.type)
        const icon = getNodeIcon(node.type)
        const isSelected = selectedNodeId === node.id
        
        return (
          <div
            key={node.id}
            style={{
              position: 'absolute',
              left: `${node.position.x}px`,
              top: `${node.position.y}px`,
              width: '100px',
              minHeight: '50px',
              backgroundColor: colors.bg,
              border: `2px solid ${isSelected ? '#f59e0b' : colors.border}`,
              borderRadius: '8px',
              padding: '8px',
              cursor: 'pointer',
              boxShadow: isSelected ? '0 4px 12px rgba(0,0,0,0.15)' : '0 2px 8px rgba(0,0,0,0.1)',
              zIndex: isSelected ? 1002 : 1001,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center'
            }}
            onClick={(e) => {
              e.stopPropagation()
              handleNodeClick(node)
            }}
          >
            <div style={{ fontSize: '16px', marginBottom: '4px' }}>{icon}</div>
            <div 
              style={{ 
                fontSize: '10px', 
                fontWeight: 'bold',
                color: colors.text,
                lineHeight: 1.2,
                wordBreak: 'break-word'
              }}
            >
              {node.data.label}
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default CustomCanvas