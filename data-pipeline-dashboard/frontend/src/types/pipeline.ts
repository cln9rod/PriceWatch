// Core pipeline types for the data pipeline dashboard

export interface NodeConfig {
  // Source node configuration
  url?: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  headers?: Record<string, string>
  
  // Transform node configuration  
  operation?: 'filter' | 'map' | 'aggregate' | 'join'
  condition?: string
  
  // Destination node configuration
  type?: 'api' | 'database' | 'file' | 'email'
  database?: string
}

export interface PipelineNode {
  id: string
  type: 'source' | 'transform' | 'destination'
  position: {
    x: number
    y: number
  }
  data: {
    label: string
    config: NodeConfig
  }
}

export interface NodePaletteItem {
  type: 'source' | 'transform' | 'destination'
  label: string
  icon: string
  description: string
}

export interface NodeCategory {
  category: string
  items: NodePaletteItem[]
}

// Color scheme for different node types
export interface NodeColors {
  bg: string
  border: string
  hover: string
  text: string
  description: string
}

// Component props interfaces
export interface CustomCanvasProps {
  onNodeSelect?: (node: PipelineNode | null) => void
}

export interface PropertiesPanelProps {
  selectedNode: PipelineNode | null
  onNodeUpdate: (nodeId: string, newData: any) => void
}

export type DragEventData = {
  type: string
  label: string
}