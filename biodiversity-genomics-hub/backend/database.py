"""
Capa de persistencia del hub. Usamos SQLite (via SQLAlchemy async) como base
por defecto para que el proyecto corra sin configuración adicional; en
producción se puede apuntar DATABASE_URL a Postgres sin cambiar el código.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import String, Float, DateTime, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./biodiversity_hub.db")

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class SpeciesRecord(Base):
    """Snapshot cacheado de una especie: taxonomía, estado de conservación
    y métricas genéticas ya calculadas, para no re-consultar las APIs
    externas en cada request."""

    __tablename__ = "species_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scientific_name: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    gbif_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    iucn_category: Mapped[str | None] = mapped_column(String(16), nullable=True)
    occurrence_count: Mapped[int | None] = mapped_column(nullable=True)
    nucleotide_diversity: Mapped[float | None] = mapped_column(Float, nullable=True)
    gc_content: Mapped[float | None] = mapped_column(Float, nullable=True)
    sequences_analyzed: Mapped[int | None] = mapped_column(nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow
    )


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
