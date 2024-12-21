#!/bin/bash

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Función para imprimir mensajes
print_message() {
    echo -e "${2}${1}${NC}"
}

# Función para verificar si Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_message "Docker no está instalado. Por favor, instálalo primero." "$RED"
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null; then
        print_message "Docker Compose no está instalado. Por favor, instálalo primero." "$RED"
        exit 1
    fi
}

# Función para construir los servicios
build() {
    print_message "Construyendo servicios..." "$YELLOW"
    docker-compose build --no-cache
}

# Función para iniciar los servicios
start() {
    print_message "Iniciando servicios..." "$YELLOW"
    docker-compose up -d
    print_message "Servicios iniciados. Accede a:" "$GREEN"
    print_message "- Frontend: http://localhost:3000" "$GREEN"
    print_message "- Backend API: http://localhost:8000/docs" "$GREEN"
    print_message "- Adminer (DB): http://localhost:8080" "$GREEN"
    print_message "- Grafana: http://localhost:3001" "$GREEN"
}

# Función para detener los servicios
stop() {
    print_message "Deteniendo servicios..." "$YELLOW"
    docker-compose down
}

# Función para reiniciar los servicios
restart() {
    print_message "Reiniciando servicios..." "$YELLOW"
    docker-compose restart
}

# Función para ver los logs
logs() {
    if [ "$2" ]; then
        docker-compose logs -f "$2"
    else
        docker-compose logs -f
    fi
}

# Función para ejecutar las migraciones
migrate() {
    print_message "Ejecutando migraciones..." "$YELLOW"
    docker-compose exec backend alembic upgrade head
}

# Función para crear una nueva migración
make_migration() {
    if [ "$2" ]; then
        print_message "Creando migración: $2..." "$YELLOW"
        docker-compose exec backend alembic revision --autogenerate -m "$2"
    else
        print_message "Por favor, proporciona un nombre para la migración." "$RED"
        exit 1
    fi
}

# Función para crear un superusuario
createsuperuser() {
    print_message "Creando superusuario..." "$YELLOW"
    docker-compose exec backend python -m scripts.create_superuser
}

# Función para ejecutar los tests
test() {
    if [ "$2" ]; then
        print_message "Ejecutando tests de $2..." "$YELLOW"
        if [ "$2" = "frontend" ]; then
            docker-compose exec frontend npm test
        elif [ "$2" = "backend" ]; then
            docker-compose exec backend pytest
        fi
    else
        print_message "Ejecutando todos los tests..." "$YELLOW"
        docker-compose exec frontend npm test
        docker-compose exec backend pytest
    fi
}

# Función para limpiar el sistema
clean() {
    print_message "Limpiando el sistema..." "$YELLOW"
    docker-compose down -v
    docker system prune -f
    rm -rf frontend/node_modules
    rm -rf frontend/dist
    rm -rf backend/__pycache__
    rm -rf backend/.pytest_cache
}

# Función para mostrar el estado de los servicios
status() {
    print_message "Estado de los servicios:" "$YELLOW"
    docker-compose ps
}

# Función para mostrar la ayuda
show_help() {
    echo "Uso: $0 [comando] [opciones]"
    echo
    echo "Comandos disponibles:"
    echo "  build            - Construir todos los servicios"
    echo "  start            - Iniciar todos los servicios"
    echo "  stop             - Detener todos los servicios"
    echo "  restart          - Reiniciar todos los servicios"
    echo "  logs [servicio]  - Ver logs (opcionalmente de un servicio específico)"
    echo "  migrate          - Ejecutar migraciones pendientes"
    echo "  makemigrations   - Crear una nueva migración"
    echo "  createsuperuser  - Crear un superusuario"
    echo "  test [servicio]  - Ejecutar tests (frontend/backend/todos)"
    echo "  clean            - Limpiar el sistema (¡cuidado!)"
    echo "  status           - Mostrar estado de los servicios"
    echo "  help            - Mostrar esta ayuda"
}

# Verificar Docker
check_docker

# Procesar comando
case "$1" in
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs "$@"
        ;;
    migrate)
        migrate
        ;;
    makemigrations)
        make_migration "$@"
        ;;
    createsuperuser)
        createsuperuser
        ;;
    test)
        test "$@"
        ;;
    clean)
        clean
        ;;
    status)
        status
        ;;
    help)
        show_help
        ;;
    *)
        print_message "Comando no reconocido: $1" "$RED"
        show_help
        exit 1
        ;;
esac

exit 0
