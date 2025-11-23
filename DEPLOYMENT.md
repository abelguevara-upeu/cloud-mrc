# Guía de Despliegue - Sistema de Matrícula MRC

## 🎯 Requisitos Previos

- Servidor Linux (Ubuntu 20.04+ recomendado)
- 2GB RAM mínimo, 4GB recomendado
- 20GB espacio en disco
- Dominio apuntando al servidor (opcional pero recomendado)

## 🚀 Opción 1: Despliegue en VPS (DigitalOcean, AWS, Azure)

### 1. Conectar al servidor
```bash
ssh root@tu-servidor-ip
```

### 2. Clonar el repositorio
```bash
cd /opt
git clone https://github.com/tu-usuario/cloud-mrc.git
cd cloud-mrc
```

### 3. Configurar variables de entorno
```bash
cp .env.example .env
nano .env  # Editar credenciales
```

**Importante:** Cambiar:
- `POSTGRES_PASSWORD` - Contraseña segura para PostgreSQL
- `SECRET_KEY` - Generar con: `openssl rand -hex 32`
- `VITE_API_URL` - URL de tu dominio/IP

### 4. Ejecutar script de despliegue
```bash
chmod +x deploy.sh
bash deploy.sh
```

### 5. Configurar firewall
```bash
# Permitir puertos HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 6. Configurar SSL con Let's Encrypt (Recomendado)
```bash
# Instalar certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtener certificado (cambiar tudominio.com)
sudo certbot --nginx -d tudominio.com -d www.tudominio.com

# Renovación automática
sudo systemctl enable certbot.timer
```

### 7. Verificar servicios
```bash
docker-compose -f docker-compose.prod.yml ps
```

## 🌐 Opción 2: Despliegue con Railway/Render (Más fácil)

### Railway (Recomendado para prototipo rápido)

1. Crear cuenta en [Railway.app](https://railway.app)
2. Instalar CLI:
```bash
npm i -g @railway/cli
railway login
```

3. Inicializar proyecto:
```bash
cd cloud-mrc
railway init
```

4. Crear servicios:
```bash
# Base de datos
railway add --service postgres

# Backend
railway up --service backend --dockerfile backend/Dockerfile

# Frontend
railway up --service frontend --dockerfile frontend/Dockerfile
```

5. Configurar variables de entorno en el dashboard de Railway

### Render

1. Conectar repositorio en [render.com](https://render.com)
2. Crear PostgreSQL database
3. Crear Web Service para backend (Docker)
4. Crear Static Site para frontend
5. Configurar variables de entorno

## 📦 Opción 3: Docker Compose Simple (Para pruebas)

```bash
# Levantar servicios
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## 🔧 Configuración Post-Despliegue

### 1. Crear usuario administrador
El usuario por defecto se crea automáticamente:
- Usuario: `admin`
- Contraseña: `admin123`

**⚠️ Cambiar contraseña inmediatamente en producción**

### 2. Backup de Base de Datos

```bash
# Crear backup
docker-compose exec db pg_dump -U mrc_user mrc_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose exec -T db psql -U mrc_user mrc_db < backup_20231120.sql
```

### 3. Configurar backups automáticos (cron)
```bash
# Editar crontab
crontab -e

# Añadir línea (backup diario a las 2 AM)
0 2 * * * cd /opt/cloud-mrc && docker-compose exec -T db pg_dump -U mrc_user mrc_db > /backups/mrc_$(date +\%Y\%m\%d).sql
```

### 4. Monitoreo

```bash
# Ver uso de recursos
docker stats

# Ver logs en tiempo real
docker-compose logs -f backend

# Ver logs del frontend
docker-compose logs -f frontend
```

## 🔐 Seguridad

1. **Cambiar contraseñas por defecto**
2. **Configurar SSL/HTTPS**
3. **Configurar firewall (UFW)**
4. **Actualizar dependencias regularmente**
5. **Configurar backups automáticos**
6. **Limitar intentos de login (fail2ban)**

```bash
# Instalar fail2ban
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
```

## 📊 URLs de Acceso

- **Frontend**: `http://tu-ip:3000` o `https://tudominio.com`
- **Backend API**: `http://tu-ip:8000`
- **Documentación API**: `http://tu-ip:8000/docs`
- **Base de datos**: Puerto 5432 (solo interno)

## 🐛 Troubleshooting

### Backend no inicia
```bash
docker-compose logs backend
# Verificar que PostgreSQL esté listo
docker-compose exec db psql -U mrc_user -c '\l'
```

### Frontend no conecta con backend
- Verificar `VITE_API_URL` en `.env`
- Verificar CORS en `backend/app/main.py`

### Base de datos no persiste
- Verificar volúmenes: `docker volume ls`
- Verificar permisos: `sudo chown -R 999:999 postgres_data/`

## 📈 Escalabilidad Futura

Para mayor tráfico:
1. Usar Kubernetes (K8s) para orquestación
2. Implementar Redis para caché
3. Usar CDN para archivos estáticos
4. Implementar load balancer (Nginx/HAProxy)
5. Replicar base de datos (PostgreSQL streaming replication)

## 🔄 Actualización del Sistema

```bash
cd /opt/cloud-mrc
git pull origin main
docker-compose down
docker-compose up -d --build
```

## 📞 Soporte

Para problemas de despliegue, revisar:
- Logs: `docker-compose logs`
- Estado: `docker-compose ps`
- Recursos: `docker stats`
