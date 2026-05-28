from app.main import db
from sqlalchemy import (
    Column, Integer, String, Numeric,
    ForeignKey, CheckConstraint, func,
    DateTime
)
from sqlalchemy.orm import  relationship
from datetime import datetime

class CtlPlatillos(db.Model):
    __tablename__ = 'ctl_platillos_menu'

    id_platillo = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    categoria_platillo_fk = Column(
        Integer,
        ForeignKey('cat_categorias_platillos_menu.id_categoria', ondelete='RESTRICT'),
        nullable=False
    )
    descripcion = Column(String(350), nullable=False)
    imagen_url = Column(String(100), nullable=False)
    popular = Column(Integer, default=0, nullable=False)
    activo = Column(Integer, default=1, nullable=False) 
    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relación ORM (carga perezosa por defecto)
    categoria = relationship('CatCategoriasPlatillos', back_populates='platillos', lazy='select')

    # Constraints a nivel de tabla
    __table_args__ = (
        CheckConstraint('precio >= 0', name='chk_precio_positivo'),
        CheckConstraint('activo IN (0, 1)', name='chk_activo_platillo'),
    )

    # Cuerpo de Salida
    def to_dict(self):
        return {
            "id_platillo": self.id_platillo,
            "nombre": self.nombre,
            "precio": float(self.precio) if self.precio else None,
            "categoria_id": self.categoria.id_categoria if self.categoria else None,
            "categoria_descripcion": self.categoria.descripcion if self.categoria else None,
            "descripcion": self.descripcion,
            "imagen_url": self.imagen_url,
            "popular": self.popular,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    def __repr__(self):
        return f"<CtlPlatillos(id={self.id_platillo}, nombre='{self.nombre}')>"

