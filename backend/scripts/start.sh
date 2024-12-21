#!/bin/bash

# Esperar a que la base de datos esté lista
echo "Esperando a que la base de datos esté lista..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Base de datos lista"

# Aplicar migraciones
echo "Aplicando migraciones..."
alembic upgrade head

# Iniciar servidor
echo "Iniciando servidor..."
uvicorn app.main:api --host 0.0.0.0 --port 8000 --reload --workers 4
