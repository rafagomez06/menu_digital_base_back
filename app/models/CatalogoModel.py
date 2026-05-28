from app.main import db
from sqlalchemy import (
    Column, Integer, String,CheckConstraint
)
from sqlalchemy.orm import  relationship

## Modelos de tablas de catalogos

class CatCategoriasPlatillos(db.Model):
    __tablename__ = 'cat_categorias_platillos_menu'
    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(30), nullable=True)
    activo = Column(Integer, default=1, nullable=True)

    #Relacion
    platillos = relationship('CtlPlatillos', back_populates='categoria', lazy='select')

    __table_args__ = (
        CheckConstraint('activo IN (0, 1)', name='chk_activo_categoria'),
    )

    # Cuerpo de Salida
    def to_dict(self):
        return {
            "id_categoria": self.id_categoria,
            "descripcion": self.descripcion,
            "activo": self.activo,
        }
    
    def __repr__(self):
        return f"<CatCategoriasPlatillos(id={self.id_categoria}, desc='{self.descripcion}')>"    



