# PY_Smart_Parking

A smart parking system with real-time spot availability tracking using MQTT, FastAPI backend, React frontend, and PostgreSQL database.

## 🚀 Quick Start

**Prerequisites:** Only Docker Desktop is required! No need to install Python, Node.js, or any other dependencies.

Run the entire stack with a single command:

```bash
docker-compose up --build
```

This will start:
- **PostgreSQL** database (port 5432)
- **Redis** cache (port 6379)
- **RedisInsight** UI (port 5540)
- **MQTT Broker** (Mosquitto, port 1883)
- **Backend** API + MQTT Publisher (port 8000)
- **Frontend** web app (port 5173)

Access the application:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **RedisInsight**: http://localhost:5540

The MQTT mock publisher runs automatically inside the backend container, generating test parking spot updates every 3 seconds.

## 📋 Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (included with Docker Desktop)

That's it! Everything else runs inside containers.

## 🏗️ Architecture

- **Backend**: FastAPI (Python) with async PostgreSQL, Redis caching, and MQTT consumer
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Database**: PostgreSQL with async SQLAlchemy
- **Cache**: Redis for high-performance data access
- **Messaging**: MQTT for real-time parking spot updates
- **Mock Data**: MQTT publisher generates realistic test data

## 📁 Project Structure

```
PY_Smart_Parking/
├── backend/              # FastAPI backend
│   ├── app/             # Main application code
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # Business logic
│   │   ├── repositories/# Data access layer
│   │   └── dtos/        # Data transfer objects
│   ├── mqtt_mock_publisher.py  # MQTT test data generator
│   ├── start.sh         # Container startup script
│   └── Dockerfile       # Backend + MQTT publisher container
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API client services
│   │   ├── hooks/       # Custom React hooks
│   │   └── types/       # TypeScript types
│   └── Dockerfile       # Frontend container
├── ops/                 # Database initialization scripts
├── mqtt-broker/         # MQTT broker configuration
└── docker-compose.yml   # Multi-container orchestration
```

## 🛠️ Development

All development happens inside Docker containers with hot-reload enabled:

**Backend**: Code changes are automatically detected via volume mount  
**Frontend**: Vite HMR (Hot Module Replacement) works out of the box

To view logs:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

To rebuild after dependency changes:
```bash
docker-compose up --build
```

To stop all services:
```bash
docker-compose down
```

## 🔧 Container Details

### Backend Container
Runs two processes:
1. **FastAPI Server** (foreground) - REST API on port 8000
2. **MQTT Publisher** (background) - Generates test data

Both processes start automatically via the `start.sh` script.

### Frontend Container
Runs Vite dev server with HMR enabled for instant updates.

## 📝 Environment Variables

Backend (configured in docker-compose.yml):
- `DATABASE_URL`: PostgreSQL connection string
- `MQTT_HOST`: MQTT broker hostname (mosquitto)
- `MQTT_PORT`: MQTT broker port (1883)
- `REDIS_HOST`: Redis server hostname (redis)
- `REDIS_PORT`: Redis server port (6379)

Frontend:
- `VITE_API_URL`: Backend API URL (http://localhost:8000)

## 🐛 Troubleshooting

**Port already in use:**
```bash
docker-compose down
```

**Check container logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

**Fresh start (removes all data):**
```bash
docker-compose down -v
docker-compose up --build
```

## 📄 License

[Add your license here]

