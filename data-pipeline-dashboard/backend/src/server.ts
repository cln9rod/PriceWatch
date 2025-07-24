import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import morgan from 'morgan'
import { createServer } from 'http'
import { Server } from 'socket.io'
import mongoose from 'mongoose'
import dotenv from 'dotenv'

dotenv.config()

const app = express()
const server = createServer(app)
const io = new Server(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    methods: ["GET", "POST"]
  }
})

// Middleware
app.use(helmet())
app.use(cors())
app.use(morgan('combined'))
app.use(express.json())

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// MongoDB connection
const connectDB = async () => {
  await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/datapipeline')
  console.log('MongoDB connected successfully')
}

// Socket.io connection handling
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id)
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id)
  })
})

const PORT = process.env.PORT || 3001

const startServer = async () => {
  // Try to connect to MongoDB but don't fail if it's not available
  try {
    await connectDB()
  } catch (error) {
    console.warn('MongoDB not available, running without database:', (error as Error).message)
  }
  
  server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`)
  })
}

startServer().catch(console.error)