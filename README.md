# SOA System Docker Setup

This repository contains a Service-Oriented Architecture (SOA) system with multiple microservices, all containerized using Docker.

## Architecture

The system consists of:
- SOA Bus (port 8000)
- Auth Service (port 8001)
- Notification Service (port 8010)
- Message Service (port 8002)
- Forum Service (port 8003)
- Post Service (port 8004)
- Comment Service (port 8005)
- Event Service (port 8006)
- Report Service (port 8007)
- Profile Service (port 8008)

The client application (`soa_client.py`) runs locally and connects to the SOA Bus to interact with all services.

## Prerequisites

- Docker
- Docker Compose
- Python 3.9+ (for running the client locally)

## Getting Started

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Execute the setup script to create necessary directories:

**For Linux/Mac:**
```bash
chmod +x build-setup.sh
./build-setup.sh
```

**For Windows:**
```powershell
.\build-setup.ps1
```

3. Build and start all services:
```bash
docker-compose up --build
```

This will:
- Build the base image with common dependencies
- Build all service images
- Create a Docker network for service communication
- Start all services in the correct order

4. To stop all services:
```bash
docker-compose down
```

5. Run the client locally:
```bash
python soa_client.py
```

## Service Communication

All services communicate through the SOA Bus on port 8000. The services are connected through a Docker network called `soa-network`. The client connects to the SOA Bus from the host machine.

## Development

To modify a service:
1. Make your changes to the service code
2. Rebuild the specific service:
```bash
docker-compose up --build <service-name>
```

For example, to rebuild just the notification service:
```bash
docker-compose up --build notification-service
```

## File Structure

After running the setup script, your directory structure should look like this:

```
├── Dockerfile.base                 # Base image with common dependencies
├── docker-compose.yml             # Orchestration file for all services
├── requirements.txt               # Python dependencies
├── build-setup.sh                # Setup script for Linux/Mac
├── build-setup.ps1               # Setup script for Windows
├── soa_client.py                 # Client application (runs locally)
├── soa_bus/
│   └─Dockerfile                # SOA Bus container
├── auth_service/
│   └── Dockerfile                # Authentication service container
├── notification_service/
│   └── Dockerfile                # Notification service container
├── message_service/
│   └── Dockerfile                # Message service container
├── forum_service/
│   └── Dockerfile                # Forum service container
├── post_service/
│   └── Dockerfile                # Post service container
├── comment_service/
│   └── Dockerfile                # Comment service container
├── event_service/
│   └── Dockerfile                # Event service container
├── report_service/
│   └── Dockerfile                # Report service container
├── prof_service/
│   └── Dockerfile                # Profile service container
└── service_template/
    └── Dockerfile                # Template for new services
```

## Troubleshooting

1. If a service fails to start, check its logs:
```bash
docker-compose logs <service-name>
```

2. To restart a specific service:
```bash
docker-compose restart <service-name>
```

3. To view all running containers:
```bash
docker-compose ps
```

4. If the client can't connect to the SOA Bus, ensure:
   - All services are running: `docker-compose ps`
   - Port 8000 is accessible from the host
   - No firewall is blocking the connection

## Ports

- SOA Bus: 8000
- Auth Service: 8001
- Profile Service: 8002
- Forum Service: 8003
- Post Service: 8005
- Comment Service: 8006
- Event Service: 8007
- Message Service: 8008
- Report Service: 8009
- Notification Service: 8010

## Usage

1. Start all services with Docker Compose
2. Run the client locally: `python soa_client.py`
3. The client will connect to the SOA Bus and provide an interactive interface to use all services 