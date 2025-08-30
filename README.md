# Contract Intelligence Parser

A professional tool for extracting and analyzing contract data from PDF documents using Docker containers.

## Project Structure

```
.
├── backend/           # FastAPI service for PDF processing and data extraction
├── frontend/          # Next.js web interface
├── docker-compose.yml # Docker Compose configuration
└── README.md          # This file
```

## Prerequisites

- Docker (v20.10+)
- Docker Compose (v2.0+)
- Git

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/Nuu-maan/Contract-Intelligence-Parser.git
   cd contract-intelligence-parser
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```
   This will build and start all services in detached mode. Add `-d` to run in the background.

3. **Access the services**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - MongoDB Express: http://localhost:8081 (MongoDB management UI)

## Services

1. **Frontend**
   - Next.js application
   - Port: 3000
   - Hot-reload enabled in development

2. **Backend**
   - FastAPI application
   - Port: 8000
   - Automatic reload in development
   - Interactive API docs at `/docs`

3. **MongoDB**
   - Database service
   - Port: 27017 (internal)
   - Data volume: `mongo-data`

4. **Mongo Express**
   - Web-based MongoDB admin interface
   - Port: 8081

## Environment Variables

Create `.env` files in both `backend` and `frontend` directories if you need to override any configurations.

### Backend (.env)
```
MONGODB_URL=mongodb://mongo:27017/contract_intelligence
UPLOAD_FOLDER=./uploads
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

### Rebuilding Containers
After making changes to the code, rebuild and restart the containers:
```bash
docker-compose up --build
```

### Viewing Logs
To view logs from all services:
```bash
docker-compose logs -f
```

### Stopping Services
To stop all services:
```bash
docker-compose down
```

To stop and remove volumes (including database data):
```bash
docker-compose down -v
```

## Troubleshooting

1. **Port Conflicts**
   Ensure ports 3000, 8000, and 8081 are not in use by other applications.

2. **Docker Permissions**
   If you encounter permission issues, try running commands with `sudo` or add your user to the docker group.

3. **Container Health**
   Check container status:
   ```bash
   docker-compose ps
   ```

## License

MIT License