#!/bin/bash

# Exit on error
set -e

# Set working directory to the directory of this script
cd "$(dirname "$0")"

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Starting Calmindra Dev Environment (Cloud-Connected) ===${NC}"

# Check if backend/.env file exists
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}Error: backend/.env file is missing!${NC}"
    echo -e "Please create 'backend/.env' with your cloud credentials before starting."
    echo -e "You can copy 'backend/.env.example' as a template."
    exit 1
fi

# Check if docker is installed and running
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running. Please start Docker first.${NC}"
    exit 1
fi

# Determine docker compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "${RED}Error: docker compose/docker-compose is not installed.${NC}"
    exit 1
fi

# Start Backend via Docker Compose
echo -e "${YELLOW}Starting Backend service via Docker Compose...${NC}"
$DOCKER_COMPOSE -f backend/docker-compose.yml up -d --build

echo -e "${GREEN}Backend is up and running (connected to Cloud Neo4j & Vertex AI)!${NC}"
echo -e "Backend API available at: ${BLUE}http://localhost:8000${NC}"
echo -e "API Docs available at:    ${BLUE}http://localhost:8000/docs${NC}"

# Set up trap to stop docker containers on exit/Ctrl+C
cleanup() {
    echo -e "\n${YELLOW}Stopping backend service...${NC}"
    $DOCKER_COMPOSE -f backend/docker-compose.yml down
    echo -e "${GREEN}Services stopped successfully.${NC}"
}
trap cleanup EXIT

# Start Frontend
echo -e "${YELLOW}Setting up frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing npm dependencies...${NC}"
    npm install
fi

echo -e "${GREEN}Starting frontend dev server...${NC}"
echo -e "Frontend will be available at: ${BLUE}http://localhost:3000${NC}"
echo -e "Press ${YELLOW}Ctrl+C${NC} to stop all services."
echo ""

npm run dev
