#!/bin/bash
# Docker setup script for AmiAgent

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    log_success "Docker and Docker Compose are installed"
}

# Setup environment file
setup_env() {
    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Created .env file from .env.example"
            log_warning "Please update .env file with your actual configuration"
        else
            log_error ".env.example not found. Please create .env file manually"
            exit 1
        fi
    else
        log_success ".env file found"
    fi
}

# Create required directories
setup_directories() {
    log_info "Creating required directories..."
    mkdir -p storage/messages
    mkdir -p logs
    log_success "Directories created"
}

# Build and start services
start_services() {
    log_info "Building and starting services..."
    docker-compose up --build -d
    log_success "Services started"
}

# Start services with tools (pgAdmin, Redis Commander)
start_with_tools() {
    log_info "Building and starting services with development tools..."
    docker-compose --profile tools up --build -d
    log_success "Services with tools started"
}

# Stop services
stop_services() {
    log_info "Stopping services..."
    docker-compose down
    log_success "Services stopped"
}

# View logs
show_logs() {
    docker-compose logs -f amiagent
}

# Show status
show_status() {
    log_info "Service status:"
    docker-compose ps

    log_info "\nHealthcheck status:"
    docker-compose exec amiagent curl -f http://localhost:1912/health || log_warning "Health check failed"

    log_info "\nDatabase status:"
    docker-compose exec postgres pg_isready -U rag -d ragdb || log_warning "Database not ready"
}

# Main menu
show_menu() {
    echo "AmiAgent Docker Management Script"
    echo "================================="
    echo "1. Setup and start services"
    echo "2. Start with development tools"
    echo "3. Stop services"
    echo "4. Show logs"
    echo "5. Show status"
    echo "6. Restart services"
    echo "7. Clean up (remove containers and volumes)"
    echo "0. Exit"
    echo ""
}

# Clean up
cleanup() {
    log_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Main script
main() {
    case "${1:-menu}" in
        "setup"|"start")
            check_docker
            setup_env
            setup_directories
            start_services
            show_status
            ;;
        "start-tools")
            check_docker
            setup_env
            setup_directories
            start_with_tools
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "restart")
            stop_services
            sleep 2
            start_services
            show_status
            ;;
        "cleanup")
            cleanup
            ;;
        "menu")
            while true; do
                show_menu
                read -p "Enter your choice [0-7]: " choice
                case $choice in
                    1) main "setup" ;;
                    2) main "start-tools" ;;
                    3) main "stop" ;;
                    4) main "logs" ;;
                    5) main "status" ;;
                    6) main "restart" ;;
                    7) main "cleanup" ;;
                    0) log_info "Goodbye!"; exit 0 ;;
                    *) log_error "Invalid option. Please try again." ;;
                esac
                echo ""
                read -p "Press Enter to continue..."
            done
            ;;
        *)
            echo "Usage: $0 {setup|start|start-tools|stop|logs|status|restart|cleanup|menu}"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
