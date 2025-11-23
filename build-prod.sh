#!/bin/bash

# Script para construir imágenes de producción localmente
# Útil para probar antes de desplegar

set -e

echo "🏗️  Construyendo imágenes de producción..."

# Backend
echo "📦 Backend..."
cd backend
docker build -f Dockerfile.prod -t mrc-backend:latest .
cd ..

# Frontend
echo "🎨 Frontend..."
cd frontend
docker build -f Dockerfile.prod --build-arg VITE_API_URL=http://localhost:8000/api/v1 -t mrc-frontend:latest .
cd ..

echo "✅ Imágenes construidas exitosamente!"
echo ""
echo "Para probar localmente:"
echo "  docker-compose -f docker-compose.prod.yml up"
