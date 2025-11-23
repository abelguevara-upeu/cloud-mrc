#!/bin/bash

# Script de despliegue para VPS
# Uso: bash deploy.sh

set -e

echo "🚀 Iniciando despliegue del Sistema de Matrícula MRC"

# 1. Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Instalar Docker y Docker Compose (si no están instalados)
if ! command -v docker &> /dev/null; then
    echo "🐳 Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Instalando Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 3. Clonar repositorio (ajustar URL)
# git clone https://github.com/tu-usuario/cloud-mrc.git
# cd cloud-mrc

# 4. Configurar variables de entorno
echo "⚙️ Configurando variables de entorno..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Por favor edita el archivo .env con tus credenciales"
    exit 1
fi

# 5. Crear directorio para uploads
mkdir -p uploads/documents

# 6. Levantar servicios
echo "🚀 Levantando contenedores..."
docker-compose up -d --build

# 7. Esperar a que la BD esté lista
echo "⏳ Esperando a que PostgreSQL esté listo..."
sleep 10

# 8. Verificar estado
echo "✅ Verificando servicios..."
docker-compose ps

echo "
✅ Despliegue completado!

📋 Próximos pasos:
1. Configurar dominio y SSL (certbot)
2. Configurar Nginx como reverse proxy
3. Configurar backups de PostgreSQL

🌐 Acceder a:
- Frontend: http://tu-ip:3000
- Backend: http://tu-ip:8000
- Docs API: http://tu-ip:8000/docs
"
