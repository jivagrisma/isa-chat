# ISA Chat

ISA Chat es una aplicación de chat inteligente que utiliza AWS Bedrock para proporcionar respuestas contextuales y precisas. La aplicación está construida con una arquitectura moderna y escalable, utilizando React para el frontend y FastAPI para el backend.

## Características

- 🤖 Integración con AWS Bedrock para procesamiento de lenguaje natural
- 💬 Chat en tiempo real con WebSocket
- 📎 Soporte para archivos adjuntos
- 🔍 Búsqueda web integrada
- 🔐 Autenticación y autorización robusta
- 📱 Diseño responsive
- 📊 Monitoreo y métricas
- 🔄 Caché con Redis
- 🗄️ Base de datos PostgreSQL

## Requisitos

- Docker y Docker Compose
- Node.js 18+ (para desarrollo local)
- Python 3.11+ (para desarrollo local)
- Cuenta de AWS con acceso a Bedrock

## Estructura del Proyecto

```
isa-fullstack/
├── frontend/           # Aplicación React (Vite + TypeScript)
├── backend/           # API FastAPI
├── docker-compose.yml # Configuración de Docker
├── prometheus.yml    # Configuración de monitoreo
└── manage.sh        # Script de gestión
```

## Configuración

1. Clonar el repositorio:
```bash
git clone https://github.com/jivagrisma/isa-chat.git
cd isa-chat
```

2. Configurar variables de entorno:
```bash
# Frontend
cp frontend/.env.example frontend/.env

# Backend
cp backend/.env.example backend/.env
```

3. Configurar credenciales de AWS:
   - Añadir AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY en backend/.env
   - Configurar la región y el modelo de Bedrock deseado

## Instalación

El proyecto utiliza Docker Compose para gestionar todos los servicios. Para comenzar:

```bash
# Dar permisos de ejecución al script de gestión
chmod +x manage.sh

# Construir los servicios
./manage.sh build

# Iniciar los servicios
./manage.sh start

# Ejecutar migraciones
./manage.sh migrate

# Crear superusuario
./manage.sh createsuperuser
```

## Desarrollo

Para desarrollo local:

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # o `venv\Scripts\activate` en Windows
pip install -r requirements.txt
uvicorn app.main:api --reload
```

## Comandos Útiles

```bash
# Ver logs
./manage.sh logs [servicio]

# Reiniciar servicios
./manage.sh restart

# Ejecutar tests
./manage.sh test [frontend|backend]

# Ver estado de los servicios
./manage.sh status

# Limpiar el sistema
./manage.sh clean
```

## Acceso a Servicios

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Adminer (DB): http://localhost:8080
- Grafana: http://localhost:3001

## Monitoreo

La aplicación incluye monitoreo completo con Prometheus y Grafana:

1. Métricas de aplicación en `/metrics`
2. Dashboard de Grafana preconfigurado
3. Alertas configurables

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Soporte

Para soporte, por favor abrir un issue en el repositorio o contactar al equipo de desarrollo.

## Agradecimientos

- AWS Bedrock por el modelo de lenguaje
- FastAPI por el framework backend
- React y Vite por el framework frontend
- Y todas las demás tecnologías open source utilizadas
