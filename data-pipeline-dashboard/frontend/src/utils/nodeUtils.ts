import { NodeConfig } from '../types/pipeline'

/**
 * Generate default configuration for different node types
 */
export const getDefaultNodeConfig = (nodeType: string): NodeConfig => {
  switch (nodeType) {
    case 'source':
      return { 
        url: '', 
        method: 'GET', 
        headers: {} 
      }
    case 'transform':
      return { 
        operation: 'filter', 
        condition: '' 
      }
    case 'destination':
      return { 
        url: '', 
        method: 'POST', 
        type: 'api' 
      }
    default:
      return {}
  }
}

/**
 * Get color scheme for different node types
 */
export const getNodeColorScheme = (type: string) => {
  switch (type) {
    case 'source': 
      return { 
        bg: '#dbeafe', 
        border: '#3b82f6', 
        text: '#1e40af' 
      }
    case 'transform': 
      return { 
        bg: '#dcfce7', 
        border: '#22c55e', 
        text: '#166534' 
      }
    case 'destination': 
      return { 
        bg: '#f3e8ff', 
        border: '#a855f7', 
        text: '#7c3aed' 
      }
    default: 
      return { 
        bg: '#f3f4f6', 
        border: '#6b7280', 
        text: '#374151' 
      }
  }
}

/**
 * Get icon for different node types
 */
export const getNodeIcon = (type: string): string => {
  switch (type) {
    case 'source': return '📥'
    case 'transform': return '🔄'
    case 'destination': return '📤'
    default: return '⚪'
  }
}

/**
 * Validate URL format
 */
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Generate unique node ID
 */
export const generateNodeId = (type: string): string => {
  return `${type}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}