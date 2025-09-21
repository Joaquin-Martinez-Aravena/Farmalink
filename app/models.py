
# app/models.py
from sqlalchemy import (
    BigInteger, Integer, String, Date, Numeric,
    ForeignKey, CheckConstraint, UniqueConstraint
)
from datetime import date, datetime
from sqlalchemy.types import BigInteger, Integer, String, Date, DateTime, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .bd import Base

class Categoria(Base):
    __tablename__ = "categoria"
    id_categoria: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    productos = relationship("Producto", back_populates="categoria")

class Usuario(Base):
    __tablename__ = "usuario"
    id_usuario: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    rol: Mapped[str] = mapped_column(String(12), nullable=False, default="EMPLEADO")
    __table_args__ = (CheckConstraint("rol IN ('ADMIN','EMPLEADO')", name="usuario_rol_check"),)

    compras_registradas = relationship("Compra", back_populates="usuario")

class Proveedor(Base):
    __tablename__ = "proveedor"
    id_proveedor: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    razon_social: Mapped[str] = mapped_column(String(200), nullable=False)
    contacto: Mapped[str | None] = mapped_column(String(120))
    telefono: Mapped[str | None] = mapped_column(String(40))
    email: Mapped[str | None] = mapped_column(String(160))

    compras = relationship("Compra", back_populates="proveedor")

class Producto(Base):
    __tablename__ = "producto"
    id_producto: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cod_producto: Mapped[str | None] = mapped_column(String(50), unique=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    id_categoria: Mapped[int] = mapped_column(
        ForeignKey("categoria.id_categoria", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )
    umbral_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estado: Mapped[str] = mapped_column(String(10), nullable=False, default="ACT")
    __table_args__ = (CheckConstraint("estado IN ('ACT','INA')", name="ck_producto_estado"),)

    categoria = relationship("Categoria", back_populates="productos")
    detalle_compra = relationship("DetalleCompra", back_populates="producto")
    lotes = relationship("Lote", back_populates="producto")

class Compra(Base):
    __tablename__ = "compra"
    id_compra: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    id_proveedor: Mapped[int] = mapped_column(
        ForeignKey("proveedor.id_proveedor", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )
    fecha_compra: Mapped[Date] = mapped_column(Date, nullable=False)
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    usuario_registra: Mapped[str | None] = mapped_column(String(120))  # histórico
    id_usuario_registra: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id_usuario", onupdate="CASCADE", ondelete="SET NULL")
    )

    proveedor = relationship("Proveedor", back_populates="compras")
    usuario = relationship("Usuario", back_populates="compras_registradas")
    detalle_compra = relationship("DetalleCompra", back_populates="compra", cascade="all, delete")
    lotes = relationship("Lote", back_populates="compra")

    __table_args__ = (CheckConstraint("total >= 0", name="ck_compra_total"),)

class DetalleCompra(Base):
    __tablename__ = "detalle_compra"
    id_detalle: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    id_compra: Mapped[int] = mapped_column(
        ForeignKey("compra.id_compra", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False
    )
    id_producto: Mapped[int] = mapped_column(
        ForeignKey("producto.id_producto", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    costo_unitario: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    compra = relationship("Compra", back_populates="detalle_compra")
    producto = relationship("Producto", back_populates="detalle_compra")

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_detalle_cantidad"),
        CheckConstraint("costo_unitario >= 0", name="ck_detalle_costo"),
    )

class Lote(Base):
    __tablename__ = "lote"
    id_lote: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    id_producto: Mapped[int] = mapped_column(
        ForeignKey("producto.id_producto", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )
    id_compra: Mapped[int] = mapped_column(
        ForeignKey("compra.id_compra", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False
    )
    fecha_venc: Mapped[Date] = mapped_column(Date, nullable=False)
    stock_lote: Mapped[int] = mapped_column(Integer, nullable=False)

    producto = relationship("Producto", back_populates="lotes")
    compra = relationship("Compra", back_populates="lotes")

    __table_args__ = (
        CheckConstraint("stock_lote >= 0", name="ck_lote_stock"),
        UniqueConstraint("id_producto", "id_compra", "fecha_venc", name="uq_lote"),
    )

class AjusteLote(Base):
    __tablename__ = "ajuste_lote"
    id_ajuste: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    id_lote: Mapped[int] = mapped_column(ForeignKey("lote.id_lote", ondelete="CASCADE"), nullable=False)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    motivo: Mapped[str] = mapped_column(String(200), nullable=False)
    id_usuario: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id_usuario", onupdate="CASCADE", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), nullable=False
)
