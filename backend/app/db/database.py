from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.core.config import settings

# Crear el motor de base de datos asíncrono
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    future=True,
    pool_size=settings.MAX_CONNECTIONS,
    max_overflow=10,
    poolclass=AsyncAdaptedQueuePool,
    pool_pre_ping=True,
    pool_timeout=30,
)

# Crear el sessionmaker asíncrono
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Crear la clase base para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de base de datos
async def get_db() -> AsyncSession:
    """
    Dependencia que proporciona una sesión de base de datos.
    Se usa como un generador asíncrono para asegurar que la sesión se cierre después de su uso.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

# Función para inicializar la base de datos
async def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas definidas.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Función para cerrar la conexión con la base de datos
async def close_db() -> None:
    """
    Cierra la conexión con la base de datos.
    """
    await engine.dispose()

# Clase base para operaciones CRUD
class CRUDBase:
    """
    Clase base para operaciones CRUD (Create, Read, Update, Delete).
    Proporciona métodos genéricos para operaciones comunes de base de datos.
    """
    def __init__(self, model):
        self.model = model

    async def get(self, db: AsyncSession, id: int):
        """Obtiene un registro por su ID."""
        return await db.get(self.model, id)

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ):
        """Obtiene múltiples registros con paginación."""
        query = await db.execute(
            self.model.__table__.select().offset(skip).limit(limit)
        )
        return query.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in):
        """Crea un nuevo registro."""
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj, obj_in):
        """Actualiza un registro existente."""
        obj_data = db_obj.__dict__
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: int):
        """Elimina un registro por su ID."""
        obj = await db.get(self.model, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

# Función para verificar la conexión a la base de datos
async def check_db_connection() -> bool:
    """
    Verifica si la conexión a la base de datos está activa.
    Retorna True si la conexión es exitosa, False en caso contrario.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return False
