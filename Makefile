# Distill Your Bro - Development Makefile
.PHONY: install dev server clean build s

# Install dependencies
install:
	@echo "Installing frontend dependencies..."
	cd frontend && pnpm install
	@echo "Installing backend dependencies..."
	pip install -r requirements.txt

# Start development server (frontend + backend)
dev:
	@echo "Starting development servers..."
	@cd frontend && pnpm run dev &
	@python scripts/server.py

# Start Flask server only
server:
	@echo "Starting Flask server on port 1007..."
	python scripts/server.py

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	cd frontend && rm -rf dist node_modules
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Build frontend for production
build:
	@echo "Building frontend..."
	cd frontend && pnpm run build

# Quick start - install dependencies and start server
start: install build server

# Help
help:
	@echo "Available commands:"
	@echo "  make install  - Install all dependencies"
	@echo "  make dev      - Start development servers"
	@echo "  make server   - Start Flask server only"
	@echo "  make clean    - Clean build artifacts"
	@echo "  make build    - Build frontend for production"
	@echo "  make start    - Quick start (install + server)"
