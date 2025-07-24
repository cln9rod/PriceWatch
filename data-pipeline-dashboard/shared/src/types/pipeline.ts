export interface PipelineNode {
  id: string;
  type: 'source' | 'transform' | 'destination';
  name: string;
  config: Record<string, any>;
  position: { x: number; y: number };
}

export interface PipelineConnection {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface Pipeline {
  id: string;
  name: string;
  description?: string;
  nodes: PipelineNode[];
  connections: PipelineConnection[];
  schedule?: {
    enabled: boolean;
    cron?: string;
  };
  status: 'draft' | 'active' | 'paused' | 'error';
  createdAt: Date;
  updatedAt: Date;
}

export interface PipelineExecution {
  id: string;
  pipelineId: string;
  status: 'running' | 'completed' | 'failed';
  startTime: Date;
  endTime?: Date;
  logs: ExecutionLog[];
  metrics: ExecutionMetrics;
}

export interface ExecutionLog {
  timestamp: Date;
  level: 'info' | 'warn' | 'error';
  message: string;
  nodeId?: string;
}

export interface ExecutionMetrics {
  recordsProcessed: number;
  duration: number;
  memoryUsage: number;
  errors: number;
}