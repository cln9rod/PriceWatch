# Data Pipeline Automation Dashboard

A visual data pipeline automation platform with real-time monitoring, inspired by tools like n8n but optimized for data processing workflows.

## ✨ Features

- **🔗 Visual Workflow Builder** - Drag-and-drop interface for creating data pipelines
- **📊 Multiple Data Sources** - Connect to APIs, databases, files, and more
- **⚡ Real-time Execution** - Live pipeline execution with monitoring
- **📈 Analytics Dashboard** - Performance metrics and execution logs
- **⏰ Scheduled Workflows** - Automated execution with cron expressions
- **🔧 Data Transformations** - Built-in filters, mappers, and aggregations

## 🚀 Tech Stack

**Frontend:**
- React 18 + TypeScript
- React Flow (visual node editor)
- Tailwind CSS
- Vite (build tool)

**Backend:**
- Node.js + Express
- MongoDB (data storage)
- Redis (caching/queues)
- Socket.io (real-time updates)

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+
- MongoDB
- Redis
- Docker (optional)

### Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development servers:**
   ```bash
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3001

### Docker Setup

```bash
# Build and start all services
npm run docker:up

# Stop services
npm run docker:down
```

## 📝 Available Scripts

- `npm run dev` - Start development servers
- `npm run build` - Build for production  
- `npm run test` - Run all tests
- `npm run lint` - Lint code
- `npm run docker:up` - Start with Docker

## 🏗️ Project Structure

```
data-pipeline-dashboard/
├── frontend/          # React frontend application
├── backend/           # Node.js API server
├── shared/            # Shared types and utilities
├── docs/              # Documentation
└── docker-compose.yml # Docker configuration
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details