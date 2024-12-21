#!/usr/bin/env python3
"""
Script para crear un superusuario.
Uso: python -m scripts.create_superuser
"""

import asyncio
import getpass
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.models.models import User
from app.services.auth_service import auth_service
from app.core.utils import validate_email, validate_password

async def create_superuser():
    """Crea un nuevo superusuario interactivamente."""
    print("\n=== Crear Superusuario ===\n")

    # Solicitar datos
    while True:
        email = input("Email: ").strip()
        if validate_email(email):
            break
        print("Email inválido. Por favor, intenta de nuevo.")

    while True:
        username = input("Username: ").strip()
        if len(username) >= 3:
            break
        print("Username debe tener al menos 3 caracteres.")

    full_name = input("Nombre completo (opcional): ").strip()

    while True:
        password = getpass.getpass("Contraseña: ")
        if validate_password(password):
            password2 = getpass.getpass("Confirmar contraseña: ")
            if password == password2:
                break
            print("Las contraseñas no coinciden.")
        else:
            print("La contraseña debe tener al menos 8 caracteres, incluyendo letras y números.")

    # Crear usuario
    try:
        async with AsyncSessionLocal() as session:
            # Verificar si el email ya existe
            result = await session.execute(
                User.__table__.select().where(User.email == email)
            )
            if result.scalar_one_or_none():
                print("\nError: El email ya está registrado.")
                return

            # Verificar si el username ya existe
            result = await session.execute(
                User.__table__.select().where(User.username == username)
            )
            if result.scalar_one_or_none():
                print("\nError: El username ya está en uso.")
                return

            # Crear usuario
            user = User(
                email=email,
                username=username,
                full_name=full_name or None,
                hashed_password=auth_service.get_password_hash(password),
                is_superuser=True
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

            print(f"\nSuperusuario '{username}' creado exitosamente!")

    except Exception as e:
        print(f"\nError al crear superusuario: {e}")

if __name__ == "__main__":
    asyncio.run(create_superuser())
